# Diagnosis Agent — Self-Healing

| Code | Source | Auto-fix | Escalate after |
|------|--------|----------|----------------|
| LINT_ERROR | ESLint/Biome/Ruff | Read error, fix manually | 3 retries |
| TYPE_ERROR | tsc/mypy | Fix types, check interfaces | 3 retries |
| IMPORT_ERROR | Hallucination guard | Scan package.json, correct path | 2 retries |
| LOGIC_ERROR | Unit tests | Re-read AC from .plan, rewrite | 5 retries |
| A11Y_ERROR | axe-core | Fix ARIA, labels, contrast | 3 retries |
| ENV_ERROR | Integration tests | STOP — escalate to DevOps | Immediately |
| SCOPE_ERROR | Scope guard | STOP — escalate to Dev | Immediately |

## Process
1. Read complete error output
2. Classify using table above
3. Apply minimum fix targeting the root cause only
4. Restart from Step 1 of generation loop
5. Log each attempt in .agent/evidence/DASH-NNN/iteration-log.json
