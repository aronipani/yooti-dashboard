# Good task decomposition — reference example

## Story
DASH-003 — As a new visitor I want to create an account
Complexity: M
Affected layers: database, api, frontend

## Correct decomposition — 4 tasks for M complexity

DASH-003-T001 — Database schema and user model
  Layer:      database
  Status:     PENDING
  Files:
    CREATE: prisma/schema.prisma (users table)
    CREATE: src/models/user.ts
    OUT OF SCOPE: src/routes/, frontend/
  AC covered: AC-1 (foundation)
  Depends on: none
  Steps:
    1. Add users table to prisma schema
    2. Define User TypeScript model
    3. Write migration
    4. Write unit tests for model

DASH-003-T002 — Registration API endpoint
  Layer:      api
  Status:     PENDING
  Files:
    CREATE: src/routes/auth/register.ts
    CREATE: src/services/auth.service.ts
    MODIFY: src/middleware/rate-limit.ts
    OUT OF SCOPE: frontend/, prisma/
  AC covered: AC-1, AC-2, AC-3, AC-4, AC-6
  Depends on: T001
  Steps:
    1. Create registration route handler
    2. Add password hashing in auth service
    3. Add rate limiting middleware
    4. Write integration tests for all AC

DASH-003-T003 — Welcome email service
  Layer:      api (async)
  Status:     PENDING
  Files:
    CREATE: src/services/email.service.ts
    OUT OF SCOPE: frontend/, prisma/, src/routes/
  AC covered: AC-5
  Depends on: T002
  Steps:
    1. Create email service with SendGrid
    2. Add welcome email template
    3. Wire to registration completion event
    4. Write integration test with mocked email

DASH-003-T004 — Registration frontend form
  Layer:      frontend
  Status:     PENDING
  Files:
    CREATE: src/pages/Register.tsx
    CREATE: src/components/RegisterForm.tsx
    OUT OF SCOPE: services/api/, prisma/
  AC covered: AC-1, AC-3, AC-4
  Depends on: T002
  Steps:
    1. Create RegisterForm component with validation
    2. Wire to POST /api/v1/auth/register
    3. Handle all error states from API
    4. Write component tests including axe accessibility

## Why this decomposition is correct
  - 4 tasks for M complexity — within the M limit of 2-3 is tight
    but acceptable because there are 4 distinct layers
  - Each task is at one layer only
  - Each task has clear dependencies
  - AC are distributed across tasks by which layer implements them
  - No task has more than 4 files
