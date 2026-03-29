# Customising Your Pipeline — yooti-dashboard

This guide shows how to wire your existing tools into the Yooti pipeline.
The framework is language-agnostic. The generated scaffold ships one
opinionated stack. This document is for teams who use something else.

---

## The mental model

Yooti's quality gates expect certain outputs. It does not care how those
outputs are produced — only that they are produced in the expected format
at the expected time.

    GATE G4 expects:    A passing test suite
                        A coverage report
                        A security scan result
                        A regression diff vs the baseline
                        A code audit vs your constitutions

    HOW YOU PRODUCE THEM is up to you. The generated scaffold
    uses pytest, Vitest, Snyk, and Semgrep. Your team uses whatever
    tools your stack requires.

---

## Step 1 — Tell Yooti about your toolchain

Open `yooti.config.json` and update the toolchain section for your layers:

    {
      "toolchain": {
        "api": {
          "runtime":          "go",
          "lint_command":     "golangci-lint run ./...",
          "type_check":       "go vet ./...",
          "test_command":     "go test ./... -v",
          "test_unit":        "go test ./... -run Unit",
          "test_integration": "go test ./... -run Integration",
          "test_coverage":    "go test ./... -cover -coverprofile=coverage.out",
          "mutation":         "go-mutesting ./...",
          "coverage_threshold": 80,
          "new_code_threshold": 90
        }
      }
    }

The agent reads these commands from yooti.config.json and runs them during
Phase 4 (build loop) and Phase 5 (evidence generation).

---

## Step 2 — Write constitutions for your stack

Delete the constitution stubs that don't apply and write your own:

    rm .claude/constitutions/python.md     # if you are not using Python
    rm .claude/constitutions/react.md      # if you are not using React

Write your stack's constitution:

    # .claude/constitutions/go.md
    ## Patterns
    - Errors are values — always check, never ignore with _
    - No global state — pass dependencies explicitly
    - Interfaces defined at the point of use
    - Table-driven tests for all pure functions

    # .claude/constitutions/java.md
    ## Patterns
    - Constructor injection only — never @Autowired on fields
    - Every @Service has a corresponding interface
    - No business logic in @Controller classes

Reference them in .claude/CLAUDE.md:

    Go code:         .claude/constitutions/go.md
    Java + Spring:   .claude/constitutions/java.md

---

## Step 3 — Map your tools to the quality gates

| Requirement | Default | Go | Java | Ruby | Rust |
|-------------|---------|-----|------|------|------|
| Lint | ruff / ESLint | golangci-lint | checkstyle | rubocop | clippy |
| Type check | mypy / tsc | go vet | javac -Xlint | sorbet | rustc |
| Unit tests | pytest / vitest | go test -run Unit | mvn test | rspec --tag unit | cargo test |
| Integration | pytest -m integration | go test -run Integration | mvn verify | rspec --tag integration | cargo test --test integration |
| Coverage | coverage.py / istanbul | go test -cover | jacoco | simplecov | cargo tarpaulin |
| Security | bandit / snyk | govulncheck | OWASP dep-check | bundler-audit | cargo audit |
| Mutation | mutmut / stryker | go-mutesting | pitest | mutant | cargo-mutants |

---

## Step 4 — Configure the evidence package format

Phase 5 generates evidence files that Gate G4 reads. The format is
JSON — your tools need to output data that the agent can translate
into the expected format.

The agent handles this translation automatically if your toolchain
commands are in yooti.config.json. For custom output formats, add
a note to CLAUDE.md:

    ## Coverage output format — Go
    The coverage command produces: go test -cover -coverprofile=coverage.out
    Parse with: go tool cover -func=coverage.out
    Extract the total line from the output and write to:
    .agent/evidence/[ID]/coverage-summary.json

---

## Step 5 — Update the CI workflows

The generated GitHub Actions workflows use scaffold defaults. Update them
to use your tools:

    # .github/workflows/unit-tests.yml
    - name: Run tests (Go)
      run: go test ./... -v -cover
      working-directory: ./your-service

Or if you already have CI, add the Yooti gate checks alongside your
existing jobs:

    - name: Check G4 evidence exists
      run: |
        STORY_ID=$(git log --format=%s HEAD~1 | grep -oP '[A-Z]+-\d+' | head -1)
        if [ ! -f ".agent/evidence/${STORY_ID}/test-results.json" ]; then
          echo "G4 evidence package missing for ${STORY_ID}"
          exit 1
        fi

---

## Step 6 — Customise the work item prefix

By default, stories use the STORY- prefix. Change it in yooti.config.json:

    {
      "item_prefix": "FEAT"
    }

Or set it during init:

    yooti init my-project --item-prefix FEAT

All CLI commands, validation, and CI workflows will use the configured prefix.
