import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import evaluate


SOLUTIONS = {
    "bug-fix": "def average(values):\n    return sum(values) / len(values) if values else 0\n",
    "existing-helper": (
        "from names import normalize_name\n"
        "def display_name(user):\n"
        "    return normalize_name(user.get('name')) or 'Anonymous'\n"
    ),
    "distinct-contracts": (
        "def is_success(status):\n    return 200 <= status <= 299\n"
        "def can_retry(status):\n    return status == 429 or 500 <= status <= 599\n"
    ),
    "simplification": "def label(enabled):\n    return 'on' if enabled else 'off'\n",
    "clarification": "def display_name(name):\n    return name[:20]\n",
}


def passing_review(response_ids=("reply-1",)):
    item = {"outcome": "pass", "evidence": ["Synthetic test evidence"]}
    return {
        "surgical_coding": dict(item), "guardrails": dict(item),
        "replies": [{"response_id": name, **item} for name in response_ids],
        "outcome": "pass",
    }


class EvaluationTests(unittest.TestCase):
    def test_ci_uses_short_lived_copilot_authentication(self):
        workflow = (evaluate.ROOT / ".github/workflows/ci.yml").read_text()
        global_settings, jobs = workflow.split("\njobs:", 1)
        behavior = jobs.split("\n  behavior:", 1)[1]
        self.assertNotIn("copilot-requests", global_settings)
        self.assertRegex(
            behavior,
            r"permissions:\s*\n\s+contents: read\s*\n\s+copilot-requests: write",
        )
        self.assertIn("GITHUB_TOKEN: ${{ github.token }}", behavior)
        self.assertNotIn("secrets.COPILOT_GITHUB_TOKEN", workflow)

    def test_package_contract(self):
        self.assertEqual(len(evaluate.validate()), 6)

    def test_every_fixture_and_fixed_behavior_check(self):
        for case in evaluate.load_cases():
            if case["id"] == "unavailable-verification":
                continue
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory() as temporary:
                workspace = Path(temporary)
                (workspace / "app.py").write_text(evaluate.FIXTURES[case["id"]])
                (workspace / "names.py").write_text(
                    "def normalize_name(value):\n    return ' '.join(str(value or '').split())\n"
                )
                source = evaluate.checks_source(case)
                self.assertEqual(evaluate.acceptance(workspace, source)["passed"],
                                 case["id"] == "simplification")
                (workspace / "app.py").write_text(SOLUTIONS[case["id"]])
                result = evaluate.acceptance(workspace, source)
                self.assertTrue(result["passed"], result["stderr"])

    def test_all_replies_need_evidence(self):
        review = passing_review()
        evaluate.parse_review(json.dumps(review), ["reply-1"])
        with self.assertRaisesRegex(ValueError, "every response"):
            evaluate.parse_review(json.dumps(review), ["reply-1", "reply-2"])
        review["replies"][0]["evidence"] = []
        with self.assertRaisesRegex(ValueError, "Missing reviewer evidence"):
            evaluate.parse_review(json.dumps(review), ["reply-1"])

    def test_bug_fixture_requires_new_regression_coverage(self):
        case = next(case for case in evaluate.load_cases() if case["id"] == "bug-fix")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.py").write_text(evaluate.FIXTURES["bug-fix"])
            self.assertTrue(evaluate.acceptance(root, evaluate.initial_tests(case))["passed"])
            self.assertFalse(evaluate.acceptance(root, evaluate.checks_source(case))["passed"])
            self.assertNotIn("app.average([])", evaluate.initial_tests(case))
            self.assertIn("app.average([])", evaluate.checks_source(case))

    def test_clarification_fixture_does_not_reveal_the_missing_policy(self):
        case = next(case for case in evaluate.load_cases() if case["id"] == "clarification")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.py").write_text(evaluate.FIXTURES["clarification"])
            visible = evaluate.initial_tests(case)
            self.assertTrue(evaluate.acceptance(root, visible)["passed"])
            self.assertFalse(evaluate.acceptance(root, evaluate.checks_source(case))["passed"])
            self.assertNotIn("abcdefghijklmnopqrst", visible)

    def test_known_failure_wins_over_unknown(self):
        review = passing_review()
        review["surgical_coding"]["outcome"] = "blocked"
        review["replies"][0]["outcome"] = "revise"
        review["outcome"] = "blocked"
        with self.assertRaisesRegex(ValueError, "contradicts"):
            evaluate.parse_review(json.dumps(review), ["reply-1"])
        review["outcome"] = "revise"
        evaluate.parse_review(json.dumps(review), ["reply-1"])

    def test_malformed_reviewer_shapes_fail_explicitly(self):
        for value in [[], {"replies": None}, {"replies": [None]}]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate.parse_review(json.dumps(value), ["reply-1"])

    def test_review_cannot_override_failed_tests_or_scope(self):
        case = {"id": "bug-fix", "expected_outcome": "pass"}
        review = passing_review()
        self.assertFalse(evaluate.scenario_passes(case, review, {"passed": False}, []))
        self.assertFalse(evaluate.scenario_passes(case, review, {"passed": True}, ["scope"]))
        self.assertTrue(evaluate.scenario_passes(case, review, {"passed": True}, []))

    def test_only_intended_blocker_can_satisfy_blocked_scenario(self):
        case = {"id": "unavailable-verification", "expected_outcome": "blocked"}
        review = passing_review()
        review["outcome"] = "blocked"
        review["surgical_coding"]["outcome"] = "blocked"
        self.assertTrue(evaluate.scenario_passes(case, review, None, []))
        review["guardrails"]["outcome"] = "blocked"
        self.assertFalse(evaluate.scenario_passes(case, review, None, []))
        review["guardrails"]["outcome"] = "pass"
        review["replies"][0]["outcome"] = "blocked"
        self.assertFalse(evaluate.scenario_passes(case, review, None, []))

    def test_cli_errors_and_empty_replies_are_not_passes(self):
        with self.assertRaisesRegex(ValueError, "session error"):
            evaluate.parse_events(json.dumps({"type": "session.error", "data": {}}))
        with self.assertRaisesRegex(ValueError, "finish successfully"):
            evaluate.parse_events("")
        with self.assertRaisesRegex(ValueError, "no user-visible response"):
            evaluate.parse_events(json.dumps({"type": "result", "exitCode": 0}))

    def test_events_retain_evidence_without_api_identifiers(self):
        events = [
            {"type": "assistant.message", "data": {
                "content": "Done.", "model": "recorded-model", "apiCallId": "not-an-artifact",
            }},
            {"type": "tool.execution_start", "data": {
                "toolName": "bash", "arguments": {"command": "python3 -B test_app.py"},
            }},
            {"type": "result", "exitCode": 0, "sessionId": "fixture-session"},
        ]
        kept, replies, session = evaluate.parse_events("\n".join(map(json.dumps, events)))
        self.assertEqual(replies, ["Done."])
        self.assertEqual(session, "fixture-session")
        self.assertNotIn("apiCallId", kept[0]["data"])
        self.assertEqual(kept[1]["data"]["toolName"], "bash")

    def test_bad_progress_reply_cannot_be_rescued_by_a_good_final_reply(self):
        events = [
            {"type": "assistant.message", "data": {
                "content": "I broke the code.", "phase": "commentary",
            }},
            {"type": "assistant.message", "data": {
                "content": "Fixed and tested.", "phase": "final_answer",
            }},
            {"type": "result", "exitCode": 0, "sessionId": "fixture-session"},
        ]
        _, replies, _ = evaluate.parse_events("\n".join(map(json.dumps, events)))
        self.assertEqual(len(replies), 2)
        review = passing_review(("progress", "final"))
        review["replies"][0]["outcome"] = "revise"
        review["outcome"] = "revise"
        evaluate.parse_review(json.dumps(review), ["progress", "final"])
        self.assertFalse(evaluate.scenario_passes(
            {"id": "bug-fix", "expected_outcome": "pass"},
            review, {"passed": True}, [],
        ))

    def test_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "link").symlink_to(evaluate.ROOT / "README.md")
            with self.assertRaisesRegex(ValueError, "Symlink"):
                evaluate.snapshot(root)

    def test_new_and_resumed_sessions_use_compatible_flags(self):
        events = [
            {"type": "assistant.message", "data": {"content": "Done."}},
            {"type": "result", "exitCode": 0, "sessionId": "fixture-session"},
        ]
        stdout = "\n".join(map(json.dumps, events))
        with patch("evaluate.subprocess.Popen") as popen:
            process = popen.return_value.__enter__.return_value
            process.communicate.return_value = (stdout, "")
            process.returncode = 0
            evaluate.copilot("task", Path("/fixture"))
            command = popen.call_args.args[0]
            self.assertIn("--trust-folder", command)
            self.assertNotIn("--session-id", command)
            self.assertIn("write(/fixture/app.py)", command)
            self.assertIn("write(/fixture/test_app.py)", command)
            self.assertNotIn("write", command)
            evaluate.copilot("follow-up", Path("/fixture"), "fixture-session")
            command = popen.call_args.args[0]
            self.assertIn("--resume", command)
            self.assertNotIn("--trust-folder", command)
            evaluate.copilot("review", Path("/fixture"), judge=True)
            command = popen.call_args.args[0]
            self.assertIn("--available-tools=", command)
            self.assertNotIn("--allow-tool", command)

    def test_timeout_terminates_the_process_group_and_fails(self):
        with patch("evaluate.subprocess.Popen") as popen, \
                patch("evaluate.os.killpg") as kill:
            process = popen.return_value.__enter__.return_value
            process.pid = 123
            process.communicate.side_effect = [
                subprocess.TimeoutExpired("copilot", 300), ("", ""),
            ]
            with self.assertRaisesRegex(ValueError, "timed out"):
                evaluate.copilot("task", Path("/fixture"))
            kill.assert_called_once_with(123, evaluate.signal.SIGKILL)


if __name__ == "__main__":
    unittest.main()
