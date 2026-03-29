# Bad task decomposition — what NOT to do

## Story
DASH-003 — As a new visitor I want to create an account
Complexity: M

## Wrong decomposition — one task per AC

DASH-003-T001 — Implement AC-1 account creation     ✗
DASH-003-T002 — Implement AC-2 duplicate email      ✗
DASH-003-T003 — Implement AC-3 password validation  ✗
DASH-003-T004 — Implement AC-4 email validation     ✗
DASH-003-T005 — Implement AC-5 welcome email        ✗
DASH-003-T006 — Implement AC-6 rate limiting        ✗

## Why this is wrong

  1. AC-1, AC-2, AC-3, AC-4, AC-6 are all implemented in the same
     API endpoint file. Splitting them into separate tasks means
     the agent will create the same file 5 times or create
     conflicts between tasks.

  2. There are 6 tasks for an M complexity story.
     M allows 2-3 tasks maximum.

  3. Tasks do not have a meaningful dependency order.
     AC-3 and AC-4 are both frontend validation —
     they belong in the same task.

  4. The agent will not know which task owns which file,
     leading to scope conflicts and duplicate code.

## Rule to remember

  If your tasks look like a numbered list of your AC
  you have decomposed by AC not by layer.
  Start over. Group by layer instead.
