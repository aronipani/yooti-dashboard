# Brownfield Rules — Surgical Mode

## Core principle
Make the smallest possible change to achieve the story goal.
You are a surgeon, not an architect.

## Before touching any file
1. Check .agent/discovery/risk-surface.json — is this file high risk?
2. If coverage < 40% or dependents > 5: write characterization tests FIRST
3. Read 50 lines above and below your change point for context

## Style — match exactly
- Indentation, quotes, semicolons: match what's already there
- If existing code uses .then(): your new code uses .then()
- You are joining a codebase, not rewriting it

## Tests — append only
- NEVER modify an existing passing test
- ADD new tests only — append to existing test files
- Characterization tests lock existing behavior (right or wrong)

## Reuse first
Search before creating: does this utility/pattern already exist?

## Found a bug out of scope?
Do NOT fix it. Write .agent/tech-debt/DASH-NNN-bug.md and move on.
