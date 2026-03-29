# Config File Constitution
# Applies to: .env, .env.example, pyproject.toml, vitest.config.ts,
#             tailwind.config.js, next.config.js, any INI or TOML file

## The golden rule
Application behaviour comes from environment variables.
Config files wire those variables into the framework.
Config files never contain secrets, credentials, or hardcoded URLs.

## .env and .env.example rules

.env.example MUST exist for every service and contain:
  - Every variable the service reads from the environment
  - A safe placeholder value for each variable
  - A comment explaining what each variable does
  - Grouped by category (DATABASE, SECURITY, AWS, EMAIL etc.)

.env MUST be in .gitignore — never committed.
.env.example MUST be committed — it is documentation.

Variable naming:
  Use SCREAMING_SNAKE_CASE
  Prefix by category: DB_, AWS_, JWT_, EMAIL_, REDIS_
  Example: DB_HOST, AWS_REGION, JWT_SECRET, EMAIL_FROM

Every service reads its own .env — never reads another service's .env.

## pyproject.toml rules

[tool.coverage.report]
  fail_under must be >= 80 — never lower without architect approval
  show_missing = true — always
  omit must only include non-production files:
    tests/*, conftest.py, */__init__.py, */config.py,
    */database.py, alembic/*, scripts/*, seed_*.py
  Never omit business logic files (routes, services, repositories)

[tool.ruff.lint]
  select must include: E, W, F, I, N, UP, B, ANN
  ignore ANN101 and ANN102 only — nothing else without approval

[tool.mypy]
  strict = true — always
  Never set ignore_errors = true

## vitest.config.ts rules

  coverage.thresholds must be >= 80 — never lower
  coverage.provider = 'istanbul' — always
  test.environment = 'jsdom' for React tests

## next.config.js / vite.config.ts rules

  Never hardcode API URLs — use process.env.NEXT_PUBLIC_API_URL
  Never disable TypeScript checking (typescript.ignoreBuildErrors = false)
  Never disable ESLint during builds (eslint.ignoreDuringBuilds = false)

## tailwind.config.js rules

  All colours defined in theme.extend.colors — no arbitrary values in code
  Content paths must cover all component locations
  Never use important: true globally
