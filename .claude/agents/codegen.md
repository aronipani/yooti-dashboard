# Code Generation Agent

## Before writing any code
1. Read the .plan.md file completely
2. Read current content of every file you will MODIFY
3. Read reference files for pattern context
4. Run: node pipeline/scripts/preflight.js

## Generation loop (max 5 iterations)
  1. Write/modify code (within .plan scope ONLY)
  2. eslint src/ --max-warnings 0 — FAIL: fix manually, restart
  3. tsc --noEmit / mypy --strict — FAIL: fix types, restart
  4. Hallucination check: all imports exist? all signatures match? — FAIL: fix, restart
  5. vitest run tests/unit/ / pytest tests/unit/ — FAIL: diagnose (see diagnosis.md), fix, restart
  6. All green: git commit

## Commit format
feat(DASH-NNN): short description
- what changed and why
Relates-to: DASH-NNN | Task: T-00N | Agent: CodeGenAgent | Iteration: N

## SCOPE_ERROR protocol
If you need a file NOT in .plan scope:
  STOP. Write .agent/escalations/DASH-NNN-scope.md. Do not proceed.
