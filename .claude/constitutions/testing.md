# Testing Constitution — yooti-dashboard
# Applies to all layers and all test types

## Purpose
Tests are not optional. Tests are the proof that the code works.
The agent writes tests before implementation (TDD).
A story is not done until all test layers are green.

---

## The TDD mandate

Write the failing test first.
Write the minimum implementation to make it pass.
Refactor. Tests must still pass.
Iteration 1 of the code generation loop always starts with tests.

---

## Test naming — always descriptive

TypeScript (Vitest):
  describe('PaymentService', () => {
    describe('processPayment', () => {
      it('returns a transaction ID when payment succeeds')
      it('throws PaymentFailedError when card is declined')
      it('throws ValidationError when amount is negative')
    })
  })

Python (pytest):
  class TestProcessPayment:
    def test_returns_transaction_id_when_payment_succeeds(self)
    def test_raises_payment_failed_error_when_card_is_declined(self)
    def test_raises_validation_error_when_amount_is_negative(self)

Never:
  it('works')                                                ✗
  def test_1(self)                                           ✗
  it('test payment')                                         ✗

---

## Unit test rules

One assertion per test — tests fail for one clear reason.
Every test is independent — no shared mutable state.
Every test sets up its own data — no test depends on another test.
Mock all external dependencies — no network, no database, no filesystem.
Tests must be fast — entire unit suite under 30 seconds.

Test these five dimensions for every function:
  1. Happy path — normal input, expected output
  2. Boundary conditions — empty input, max input, zero, null
  3. Error paths — invalid input, service failure, timeout
  4. Contract — output matches declared return type
  5. Side effects — correct calls made to dependencies

---

## Integration test rules

Run against real services (real database, real cache).
Every test has explicit setup (seed data) and teardown (clean data).
Tests must not rely on data created by other tests.
Every acceptance criterion from the story must have at least one integration test.
Test the full HTTP round-trip for API tests — not just the service layer.

---

## Coverage thresholds — hard requirements

Overall coverage:       >= 80%
New code coverage:      >= 90%
These thresholds block the PR if not met.
Coverage must be measured on lines, branches, and functions.

---

## Mutation testing

Stryker (TypeScript) and mutmut (Python) run on every PR.
Mutation score >= 85% required (warn if below, QA reviews).
A mutation that survives means a test exists but protects nothing.
The agent adds tests for any surviving mutations.

---

## What is banned

Tests that always pass regardless of implementation
  expect(true).toBe(true)                                    ✗
  assert True                                                ✗

Tests that test the framework, not the code
  expect(typeof result).toBe('object')                       ✗ (unless type matters)

Tests that depend on execution order
Tests that make real network calls
Tests that access the real database in unit tests
Skipping tests without a documented reason and story reference
  it.skip('this test')                                       ✗
  it.skip('STORY-042: temporarily skipped — fix in sprint 4') ✓

## Self-audit — mandatory before marking any test COMPLETE

Write results to .agent/evidence/{STORY-ID}/code-audit.md.

  TEST QUALITY
  ☐ Every test has a clear Given/When/Then structure
  ☐ Every test asserts a specific outcome — no empty assertions
  ☐ No test depends on another test's state
  ☐ No hardcoded test data that should be in fixtures
  ☐ No real external services called in unit tests
  ☐ Test names describe behaviour not implementation
  ☐ Mutation score >= 85% on new code
