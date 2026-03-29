# Greenfield Pattern Mandate
# Apply to ALL code in this project

## Architecture
- Services: class-based, constructor dependency injection
- Controllers/routes: thin — validate, call service, return response
- Services: business logic only — no HTTP, no DB queries
- Repositories: DB layer only — no business logic
- Errors: extend AppError base class — never throw raw Error()

## TypeScript
- Interfaces for all data shapes, never raw objects in signatures
- Enums for status fields, event types, role names
- No 'any' — figure out the type
- Explicit return types on all exported functions

## Async
- async/await only — no .then() chains
- Promise.all() for parallel — never sequential await in a loop

## Naming
- PascalCase: PropertyService.ts
- camelCase: formatCurrency.ts
- kebab-case: property-routes.ts

## Never use console.log in production code
- Structured logging only (JSON) with requestId, userId, timestamp, service
