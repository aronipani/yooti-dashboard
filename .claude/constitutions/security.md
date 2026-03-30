# Security Constitution — yooti-dashboard
# Applies to ALL layers: TypeScript, Python, React, SQL, agents

## Purpose
Security is not optional and not a separate concern.
These rules apply everywhere, always, regardless of the story type.
A single violation blocks the PR — no exceptions.

---

## Credentials and secrets — never in code

Never hardcode:
  API keys, passwords, tokens, connection strings,
  private keys, certificates, or any secret value.

Always use environment variables:
  process.env.DATABASE_URL                                   ✓
  os.environ.get("DATABASE_URL")                             ✓
  const DB_URL = "postgresql://user:pass@host/db"            ✗

Always document required env vars in .env.example.
Never commit .env to git — it is in .gitignore.
Rotate any secret that was accidentally committed immediately.

---

## Input validation — validate everything from outside the system

All external inputs must be validated before use:
  API request bodies — use Zod (TypeScript) or Pydantic (Python)
  URL parameters — validate type and range
  Query strings — validate and sanitise
  File uploads — validate type, size, and content

Reject early — fail fast on invalid input, before any processing.
Never trust client-provided IDs for authorisation decisions.

---

## Authentication and authorisation

Every protected endpoint must verify authentication.
Every protected resource must verify the requester has permission.
Authentication ≠ authorisation — always check both.

Never:
  Trust a userId passed in the request body for authorisation
  Skip auth checks because "this is an internal endpoint"
  Use GET requests for state-changing operations

Always:
  Extract userId from the verified JWT token, not the request body
  Check that the authenticated user owns the resource they are requesting
  Use middleware for authentication — not inline in every handler

---

## SQL injection prevention

Always use parameterised queries — never string interpolation:
  f"SELECT * FROM users WHERE id = {user_id}"                ✗
  "SELECT * FROM users WHERE id = $1", [user_id]             ✓
  db.query("SELECT * FROM users WHERE id = ?", user_id)      ✓

---

## XSS prevention (frontend)

Never use dangerouslySetInnerHTML without explicit security review.
Always sanitise user-generated content before rendering.
Use Content Security Policy headers.
React escapes output by default — do not bypass it.

---

## Sensitive data handling

Never log:
  Passwords (even hashed), tokens, card numbers,
  full SSNs, private keys, session tokens.

Always log security events (at WARNING level minimum):
  Failed authentication attempts
  Authorisation failures
  Unusual access patterns

Mask sensitive data in logs:
  email: user@example.com → u***@example.com in logs
  card: 4242424242424242  → ****4242 in logs

---

## Dependency security

Run Snyk on every PR — 0 HIGH or CRITICAL findings required.
Pin dependency versions — no floating ranges in production:
  "express": "^4.18.0"                                       ✗ (floating)
  "express": "4.18.2"                                        ✓ (pinned)
Run npm audit or pip-audit before every release.

---

## Rate limiting and abuse prevention

Authentication endpoints must have rate limiting.
API endpoints that trigger emails or SMS must have rate limiting.
Use exponential backoff for retry logic — never tight loops.

---

## What is banned — zero tolerance

Hardcoded credentials anywhere in the codebase
eval() or exec() with user input
SQL string interpolation with user input
Storing passwords in plaintext
Logging passwords, tokens, or card numbers
Skipping authentication on any non-public endpoint
Trusting user-provided IDs for authorisation
math.random() or random.random() for security tokens (use crypto)

## Self-audit — mandatory before marking any task COMPLETE

Run this checklist on every file regardless of language.
Write results to .agent/evidence/{STORY-ID}/code-audit.md.

  UNIVERSAL SECURITY CHECKS
  ☐ No secrets or API keys in any file
  ☐ No hardcoded URLs that should be environment variables
  ☐ No debug endpoints or admin routes without auth
  ☐ No logging of sensitive data (passwords, tokens, PII)
  ☐ Input validated and sanitised before use
  ☐ Error messages never reveal internal implementation details
  ☐ No eval() or exec() with user input
  ☐ Snyk scan: 0 HIGH or CRITICAL findings
  ☐ Semgrep scan: 0 findings
