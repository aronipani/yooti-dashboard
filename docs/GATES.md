# Human Decision Gates — yooti-dashboard

## G1 PM Sign-Off (before sprint)
- [ ] All stories have Given/When/Then ACs
- [ ] Definition of Done per story
- [ ] Ambiguity blockers resolved
FAIL: sprint does not start

## G2 Architecture Review (Days 1-2)
- [ ] ADRs approved
- [ ] .plan files reviewed for M/L stories
- [ ] No breaking cross-system changes without approval
FAIL: code generation does not begin

### Plan quality checklist — architect reviews each plan against this

DECOMPOSITION
- [ ] Tasks split by layer — not by acceptance criterion
- [ ] No more tasks than the complexity allows
  (XS=1, S=1-2, M=2-3, L=3-4, XL=4-5)
- [ ] Each task touches no more than 5-7 files
- [ ] Every AC from the story is covered by at least one task
- [ ] No AC is left without a task covering it

SCOPE
- [ ] Every file in CREATE/MODIFY scope is necessary for this task
- [ ] OUT OF SCOPE section lists unrelated directories
- [ ] No file appears in two tasks (no overlap between tasks)
- [ ] Scope does not bleed into unrelated services

DEPENDENCIES
- [ ] Tasks are ordered correctly — database before API before frontend
- [ ] Dependency chain has no circular references
- [ ] Tasks that can run in parallel are identified

IMPLEMENTATION STEPS
- [ ] Steps are actionable and specific
- [ ] Steps follow the correct order
- [ ] Steps reference the right files from scope
- [ ] No step touches a file outside the scope

APPROVE when all boxes above are checked.
REJECT with specific feedback on which box failed and why.

## G3 Developer PR Review (Days 6-8)
- [ ] Code matches intent
- [ ] No out-of-scope file changes
- [ ] Patterns consistent
- [ ] No hardcoded secrets
APPROVE: continue | REQUEST CHANGES: agent corrects | REJECT: replan

## G4 QA Sign-Off (Day 9)

Run: yooti qa:review DASH-NNN

### Hard gates (any failure = automatic reject)
| Gate | Threshold | Evidence file |
|------|-----------|---------------|
| Unit tests | 100% pass | test-results.json |
| Integration tests | 100% pass | test-results.json |
| Zero regressions | 0 newly failing | regression-diff.json |
| Overall coverage | >= 80% | coverage-summary.json |
| New code coverage | >= 90% | coverage-summary.json |
| CRITICAL security | 0 findings | security-scan.json (Snyk) |
| HIGH security | 0 findings | security-scan.json (Snyk) |
| Semgrep | 0 findings | security-scan.json |
| Accessibility | 0 violations | accessibility.json (if frontend) |

### Soft gates (QA judgement — review required)
| Gate | Target | Evidence file |
|------|--------|---------------|
| Mutation score | >= 85% | mutation-score.json |

FAIL (hard gate): agent generates more tests, reruns Phase 5
FAIL (soft gate): QA reviews and decides — approve or reject with notes

## G5 Deployment Approval (Day 10)
- [ ] Staging stable > 30 min
- [ ] Smoke tests passing
- [ ] p99 latency within 20% of prod baseline
- [ ] Rollback plan confirmed
GO: deploy | NO-GO: hold
