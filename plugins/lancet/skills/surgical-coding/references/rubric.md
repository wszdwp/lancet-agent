# Lancet quality rubric

Evaluate the task outcome, diff, tool results, and all user-visible replies
together. Judge observed behavior, not the agent's claims or intentions.

## MVP checklist

Start here. The MVP has two acceptance criteria, with no weighted score.

### 1. Surgical coding

- The requested behavior is complete, with evidence from focused checks of the
  requirement and relevant existing behavior. For a bug fix, retain the
  before/after reproducer where practical.
- Every changed hunk serves the task or a direct consequence; there is no
  unrelated cleanup, speculative feature, or unnecessary abstraction.
- The code uses readable repository patterns and suitable existing helpers.
  Callers, tests, and directly affected documentation are included when needed.

Review the diff and check results. A small diff alone does not establish a pass.

### 2. Plain, short, complete replies each round

For every user-visible response, including questions and progress updates:

- **Plain:** the opening states the answer, outcome, blocker, or necessary
  question. A reader can understand it without decoding avoidable jargon.
- **Short:** default to one short paragraph or a short list. Every sentence
  serves the current round; remove filler, repetition, and routine narration.
  More detail is justified only by completeness or the user's explicit request.
- **Complete:** answer what this round requires. A delivery reply states the
  meaningful change and verification status, plus material caveats or next steps.
  A clarification asks what is needed to proceed without pretending work is done.

Retain the conversation and cite each response reviewed. A good final reply
cannot erase an earlier failure. Missing rounds are unknown, not assumed good.
Do not pass a cryptic or incomplete reply merely because it is short.

### Decision and feedback

Safety, preservation of user work, truthful claims, and explicit task controls are
mandatory guardrails, not extra capabilities to optimize.

- **Pass:** both criteria and the guardrails pass with supporting evidence.
- **Revise:** a known failure in either criterion or a guardrail, even if other
  evidence is missing.
- **Blocked:** evidence, access, or requirements are missing and no known failure
  already requires revision. Honest uncertainty is not dishonesty, but it does
  not establish verified correctness.

For a question-only round, mark surgical coding not applicable with a reason;
review the reply without claiming evidence of coding capability.

## Manual evaluation

1. Select a case from [test-cases.md](./test-cases.md). Prepare a target repository
   matching its setup; record the actual files, checks, and starting snapshot.
   The JSON describes scenarios, not executable fixtures.
2. Record the instruction revision, model/tool configuration, and task controls
   before the run. Keep acceptance expectations fixed.
3. Retain the diff, repository check output, full conversation, and tool evidence.
   Review every reply, not just the final one.
4. An independent reviewer applies both criteria and the guardrails. Cite evidence
   or the specific blocker; do not infer safety from a diff alone.
5. Record the outcome and smallest correction. Improve the instructions from
   observed failures, then rerun the same task from the same starting state.

Start with one small bug fix and its follow-up round. Keep failed and blocked
attempts. Do not average away a failed case or treat missing evidence as a pass.
This is the initial feedback loop, not proof of general capability.

## Review record

Keep this JSON inside a Markdown evaluation record, not in every agent reply.
Replace `null` values with observed results; they are unreviewed, never passes.
Use `pass`, `revise`, or `blocked`. Only surgical coding may use `N/A`, with a
reason; label the record `reply-only` when no coding was required.

```json
{
  "case_id": "bug-fix",
  "starting_state": null,
  "instruction_revision": null,
  "model_and_tools": null,
  "controls": {
    "allowed_changes": [],
    "required_checks": [],
    "reply_detail": "brief"
  },
  "surgical_coding": { "outcome": null, "evidence": [] },
  "replies": [
    { "response_id": null, "outcome": null, "evidence": [] }
  ],
  "guardrails": { "outcome": null, "evidence": [] },
  "evaluation_scope": "coding-task",
  "outcome": null,
  "correction_or_blocker": null
}
```
