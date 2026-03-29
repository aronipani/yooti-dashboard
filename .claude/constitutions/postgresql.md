# PostgreSQL Constitution — yooti-dashboard

## Purpose
Defines how database queries, schemas, and migrations are written.
Agent reads this when writing any database interaction code.

---

## Naming conventions

Tables:               snake_case, plural nouns
  users, payment_transactions, property_listings             ✓
  User, PaymentTransaction                                   ✗

Columns:              snake_case
  created_at, user_id, first_name                            ✓
  createdAt, userId                                          ✗

Primary keys:         always named id (UUID or BIGSERIAL)
  id UUID PRIMARY KEY DEFAULT gen_random_uuid()              ✓

Foreign keys:         [referenced_table_singular]_id
  user_id, property_id, payment_id                          ✓

Indexes:              idx_[table]_[columns]
  idx_users_email, idx_orders_user_id_created_at             ✓

Timestamps:           created_at and updated_at on every table
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

---

## Schema rules

Every table must have:
  id          — primary key (UUID preferred, BIGSERIAL for high-volume)
  created_at  — when the row was created
  updated_at  — when the row was last modified (use trigger to auto-update)

NULL policy:
  Be explicit — every column is either NOT NULL or nullable with a reason.
  Default to NOT NULL. Add nullable only when business logic requires it.

Soft deletes:
  Use deleted_at TIMESTAMPTZ NULL instead of deleting rows.
  Add index on deleted_at for queries that filter active records.

Enum types:
  Use PostgreSQL enum types for status fields:
  CREATE TYPE payment_status AS ENUM ('pending', 'complete', 'failed')

---

## Query rules

Never use string interpolation in queries:
  query = f"SELECT * FROM users WHERE id = {user_id}"        ✗ SQL injection
  query = "SELECT * FROM users WHERE id = $1"                ✓ parameterised

Always select specific columns — never SELECT *:
  SELECT * FROM users                                        ✗
  SELECT id, email, name, created_at FROM users              ✓

Always use LIMIT on queries without guaranteed single results.

Use CTEs for complex queries — not deeply nested subqueries:
  WITH active_users AS (
    SELECT id FROM users WHERE deleted_at IS NULL
  )
  SELECT ...

---

## Index rules

Always add indexes for:
  Foreign key columns
  Columns used in WHERE clauses of frequent queries
  Columns used in ORDER BY of paginated queries
  Columns used in JOIN conditions

Use partial indexes for queries on subsets:
  CREATE INDEX idx_orders_pending ON orders(created_at)
  WHERE status = 'pending'

Never add indexes speculatively — add them when the query exists.

---

## Migration rules

Every schema change is a migration — never alter the schema directly.
Migrations must be reversible — write both up and down.
Never drop a column in the same migration that stops writing to it.
  Step 1: stop writing to the column (deploy)
  Step 2: backfill or confirm column is empty (verify)
  Step 3: drop the column (separate migration, separate deploy)

Never rename a column — add new, migrate data, drop old.
Test every migration against a copy of production data before deploying.

---

## Performance rules

N+1 queries are banned — use JOINs or batch loading:
  for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = $1", user.id)  ✗

  orders = db.query("SELECT * FROM orders WHERE user_id = ANY($1)", user_ids) ✓

Use EXPLAIN ANALYZE before committing any complex query.
Connection pooling — always use a pool, never new connections per request.
Use database-level constraints — do not rely solely on application validation.

---

## What is banned

Raw string queries with user input (SQL injection)
SELECT * in production queries
Schema changes without migrations
Dropping columns without a staged rollout
Synchronous database calls in async handlers
Storing sensitive data (passwords, tokens) in plaintext
