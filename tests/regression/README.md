# Regression Test Suite — yooti-dashboard

## What this is
The regression suite protects every sprint's completed work from being
broken by subsequent sprints. It runs on every PR automatically.

## Structure

```
tests/regression/
├── suites/
│   ├── smoke.test.ts          Critical path — runs in < 2 minutes
│   ├── api-contracts.test.ts  All endpoints respond correctly
│   └── security.test.ts       Auth and security checks
├── baseline/                  Captured baselines per sprint
│   └── sprint-N-baseline.json
└── comparator/
    └── diff.py                Compares current vs baseline
```

## How it works

Sprint start:
  yooti sprint:start
  → captures current passing tests as baseline
  → stored in: tests/regression/baseline/sprint-N-baseline.json

Every PR:
  CI runs: python tests/regression/comparator/diff.py
  → compares current results against baseline
  → any newly failing test blocks the PR

## Adding to the smoke suite

After each story is merged, add its critical path to smoke.test.ts:
  describe('Smoke — [feature name]', () => {
    it('[critical behaviour]')
  })

Keep the smoke suite under 2 minutes total.
