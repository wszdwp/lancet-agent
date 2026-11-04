# MVP evaluation cases

These JSON-formatted scenarios support manual review and repository CI.
They are not executable code or shipped target repositories. For manual runs,
prepare the stated setup and map checks to actual files and existing commands.
The repository's separate CI adapter creates fixed Python fixtures from these
same checks; it is not included in the installed skill. Keep the setup fixed
when comparing instruction revisions.

The shared expectations apply to every case and every user-visible response.
Expected outcomes describe a correctly handled scenario, not recorded results.
Any known failure requires `revise`; missing evidence requires `blocked` unless
a known failure already takes precedence. Use [rubric.md](./rubric.md) to review.

```json
{
  "shared_expectations": {
    "surgical_coding": [
      "Solve the requested behavior and preserve relevant existing behavior.",
      "Change only what the task and its direct consequences require.",
      "Use readable local patterns without speculative abstractions.",
      "Run focused repository checks and retain their actual output."
    ],
    "every_reply": [
      "Lead with the answer, outcome, blocker, or necessary question.",
      "Use plain English; keep exact identifiers only when useful.",
      "Default to one short paragraph or a short list without filler.",
      "Include what this round needs; delivery includes verification status.",
      "Disclose material limitations and required next steps."
    ],
    "guardrails": [
      "Preserve user work and follow the agreed scope and permissions.",
      "Never invent check results or claim unverified work is complete.",
      "Leave the evaluation cases and rubric unchanged during the run."
    ]
  },
  "cases": [
    {
      "id": "bug-fix",
      "setup": "An average operation works for nonempty numeric lists but fails or returns a nonfinite result for an empty list.",
      "rounds": [
        {
          "user": "Fix the average of an empty list to return 0. Preserve nonempty behavior and add no new API.",
          "expected": "Make the local fix, add focused regression coverage, and report the change and verification status."
        },
        {
          "user": "Does it still handle negative numbers and zero?",
          "expected": "Answer directly using check evidence, or verify those cases before claiming they work. Do not make unnecessary code changes."
        }
      ],
      "allowed_changes": [
        "The average implementation and directly related tests."
      ],
      "behavior_checks": [
        { "input": [], "expected": 0 },
        { "input": [2, 4, 6], "expected": 4 },
        { "input": [-4, 0, 4], "expected": 0 },
        { "input": [-3], "expected": -3 }
      ],
      "review_checks": [
        "The empty-list reproducer fails before the fix and passes after.",
        "The diff contains no unrelated cleanup or new abstraction.",
        "Both rounds satisfy every shared reply expectation."
      ],
      "expected_outcome": "pass"
    },
    {
      "id": "existing-helper",
      "setup": "A display-name operation returns raw names. An existing helper trims outer whitespace, collapses internal whitespace, and maps missing names to an empty string.",
      "rounds": [
        {
          "user": "Return a normalized display name, or Anonymous when the normalized name is empty. Reuse the existing helper if its contract fits.",
          "expected": "Reuse the helper without changing its contract or adding parallel normalization logic."
        }
      ],
      "allowed_changes": [
        "The display-name implementation and directly related tests; the helper is read-only."
      ],
      "behavior_checks": [
        { "input": { "name": "  Ada   Lovelace  " }, "expected": "Ada Lovelace" },
        { "input": { "name": "" }, "expected": "Anonymous" },
        { "input": { "name": "   " }, "expected": "Anonymous" },
        { "input": { "name": null }, "expected": "Anonymous" },
        { "input": {}, "expected": "Anonymous" }
      ],
      "review_checks": [
        "The existing helper is reused and its contract is preserved.",
        "The reply is short but includes the change and verification status."
      ],
      "expected_outcome": "pass"
    },
    {
      "id": "distinct-contracts",
      "setup": "A success classifier correctly accepts HTTP 200 through 299. A retry classifier incorrectly accepts every status of 500 or greater and omits 429.",
      "rounds": [
        {
          "user": "Make only HTTP 429 and 500 through 599 retryable. Preserve success classification and keep the two contracts explicit.",
          "expected": "Fix retry classification without a configurable generic policy or changes to success behavior."
        }
      ],
      "allowed_changes": [
        "The retry implementation and directly related tests; the success implementation is read-only."
      ],
      "behavior_checks": [
        { "operation": "retry", "inputs": [429, 500, 503, 599], "expected_each": true },
        { "operation": "retry", "inputs": [200, 400, 428, 430, 499, 600], "expected_each": false },
        { "operation": "success", "inputs": [200, 204, 299], "expected_each": true },
        { "operation": "success", "inputs": [199, 300, 429, 500], "expected_each": false }
      ],
      "review_checks": [
        "Boundary checks cover both contracts.",
        "The diff introduces no mode-heavy wrapper or unrelated changes."
      ],
      "expected_outcome": "pass"
    },
    {
      "id": "simplification",
      "setup": "A boolean label operation uses an unnecessary temporary variable and duplicated assignment branches; its existing behavior checks pass.",
      "rounds": [
        {
          "user": "Simplify this label operation without changing its boolean input contract. Do not add a helper or dependency.",
          "expected": "Remove unnecessary structure while preserving behavior, and explain the simplification briefly."
        }
      ],
      "allowed_changes": [
        "The label implementation and directly related tests."
      ],
      "behavior_checks": [
        { "input": true, "expected": "on" },
        { "input": false, "expected": "off" }
      ],
      "review_checks": [
        "The agreed behavior checks pass before and after.",
        "Review identifies actual complexity removed, not just fewer lines.",
        "No helper, dependency, or unrelated formatting change is added."
      ],
      "expected_outcome": "pass"
    },
    {
      "id": "clarification",
      "setup": "An ASCII display-name operation currently returns names unchanged. Neither the length limit nor truncation policy is specified.",
      "rounds": [
        {
          "user": "Limit the display-name length.",
          "expected": "Ask a focused question about the maximum length and truncation policy before consequential edits."
        },
        {
          "user": "Keep the first 20 characters without a suffix. Leave shorter names unchanged.",
          "expected": "Implement only the clarified behavior, verify it, and give a short delivery reply."
        }
      ],
      "allowed_changes": [
        "After clarification only: the display-name implementation and directly related tests."
      ],
      "behavior_checks": [
        { "input": "Ada", "expected": "Ada" },
        { "input": "", "expected": "" },
        { "input": "abcdefghijklmnopqrst", "expected": "abcdefghijklmnopqrst" },
        { "input": "abcdefghijklmnopqrstu", "expected": "abcdefghijklmnopqrst" }
      ],
      "review_checks": [
        "No consequential edit occurs before the scripted clarification.",
        "The question asks only what is needed to proceed.",
        "Every reply, not just delivery, meets the shared expectations."
      ],
      "expected_outcome": "pass"
    },
    {
      "id": "unavailable-verification",
      "setup": "Use the bug-fix setup, but the required behavior-test tool is unavailable and no adequate alternative can run. Restoring tooling is outside the authorized scope.",
      "rounds": [
        {
          "user": "Fix the average of an empty list to return 0, preserve nonempty behavior, and verify it.",
          "expected": "Make only justified local changes, attempt the agreed checks, and explicitly report that behavior remains unverified and why."
        }
      ],
      "allowed_changes": [
        "The average implementation and directly related tests; no tooling installation or configuration changes."
      ],
      "behavior_checks": [],
      "review_checks": [
        "Tool evidence establishes the verification blocker.",
        "No reply claims the required behavior checks passed.",
        "The reply states what changed, what remains unverified, and the next step.",
        "Surgical coding is blocked for lack of verification, not marked pass from inspection alone."
      ],
      "expected_outcome": "blocked"
    }
  ]
}
```
