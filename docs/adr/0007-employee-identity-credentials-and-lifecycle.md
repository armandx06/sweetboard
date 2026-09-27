# ADR 0007: Employee Identity, Credentials, and Lifecycle Management

- **Status:** Accepted
- **Date:** September 27, 2026
- **Author:** [armandx06](https://github.com/armandx06)

---

## Context

Implementing the `Employee` model and its CRUD surfaced several interrelated decisions that don't belong to a single infrastructure choice (unlike ADRs 0001-0006), but to the business and security semantics of the entity itself: how an employee is identified, how their credentials are handled, and how they leave the system. This ADR groups those decisions together since they were made as a coherent set during the same implementation cycle, and future entities with similar needs (e.g., a future `User`/auth model, if `Employee` doesn't remain the sole identity table) should follow the same reasoning unless a new ADR supersedes it.

## Decision 1: System-Generated Usernames

Usernames are not supplied by the client. On creation, the API derives one from `first_name[:2] + last_name[:2] + birth_date:%y`, uppercased, with a two-digit numeric suffix (`01`, `02`, ...) to disambiguate employees who produce the same prefix. The suffix is computed by counting existing usernames matching that prefix via a `LIKE` filter, not an exact match, so it correctly detects prior collisions instead of always resolving to `01`.

**Rationale:** a predictable, short, human-typable username is preferable to requiring the client (a small bakery's admin) to invent and guarantee uniqueness manually. Deriving it from stable identity fields (name, birth year) keeps it memorable without exposing anything more sensitive than the name itself.

**Trade-off — the username is not permanently fixed:** if `first_name` or `last_name` is corrected via `PATCH /employees/{id}` (e.g., fixing a typo), the username is regenerated to stay consistent with the corrected name, rather than permanently freezing it at creation time. This means an employee's login identifier can change after a name correction. This is accepted for now on the basis that both the employee and the administrator must be notified of any such change, and is expected to be properly closed once email notifications (ADR pending) are implemented to inform the employee automatically when their username changes.

## Decision 2: Credential Handling (Passwords)

Passwords are never supplied by the client, at creation or otherwise. On creation, the API generates a random password, hashes it with `bcrypt` for storage, and returns the plaintext value exactly once, in the creation response only (`temporary_password` field). It is never persisted anywhere in plaintext, and it is never included in any read response (`GET /employees`, `GET /employees/{id}`) — only the hash is stored, and the hash itself is also excluded from every read schema, since exposing it would allow offline brute-force attempts without any legitimate client use case.

**Rationale:** removing password choice from the client eliminates weak/reused passwords for a workforce that isn't expected to manage their own credential hygiene closely. Returning the plaintext once, instead of never, is necessary because otherwise nobody — including the administrator — could retrieve it after hashing; a proper delivery channel (emailing the employee directly) is deferred as future scope, tracked alongside the username-change notification above.

## Decision 3: Password Reset as a Dedicated Action, Not Part of General Update

Resetting a password is exposed as `POST /employees/{id}/reset-password`, a standalone endpoint, separate from `PATCH /employees/{id}`.

**Rationale:** `PATCH` semantics apply a given, idempotent state change. A password reset is not idempotent — each call produces a different secret — so it doesn't fit the same contract as updating a phone number. Modeling it as its own `POST` action also keeps its distinct response shape (a one-time plaintext secret) from leaking into the general `EmployeeUpdate`/`EmployeeRead` contract.

## Decision 4: `PATCH` Is Scoped to Contact Information Only

`EmployeeUpdate` only accepts `first_name`, `last_name`, `phone_number`, and `email`. `username`, `password`, and `birth_date` are excluded from the schema entirely — not merely ignored — so they cannot be set through this endpoint even by omission-based confusion on the client side.

**Rationale:** the fields excluded from `EmployeeUpdate` are either system-derived (`username`, `password`, both covered by Decisions 1 and 2) or represent identity facts that shouldn't casually change post-creation (`birth_date`). Limiting the update surface to contact information keeps the endpoint's contract narrow and predictable, and avoids a client accidentally triggering side effects (like username regeneration) through an unrelated field.

## Decision 5: Deactivation (Soft Delete) for Real Terminations, Physical Deletion Reserved for Data-Entry Errors

Two distinct removal paths exist:

- `PATCH /employees/{id}/deactivate` and `/reactivate` set `active = false` / `true` and manage `termination_date`, preserving the row and its history. This is the path used when an employee actually stops working at the bakery.
- `DELETE /employees/{id}` performs a real, physical deletion. It exists only to correct data-entry mistakes (an employee record created and never activated), and is guarded: an employee can only be deactivated if they have a `hire_date` (i.e., they were actually activated at some point) — attempting to deactivate an employee that was never hired raises a domain error instead, funneling that case toward physical deletion instead.

**Rationale:** once `Employee` participates in relationships with other business data (shifts, sales, inventory movements), a physical delete would either cascade-destroy or orphan that history. Since `active` and `termination_date` already existed on the model for exactly this purpose, using them for real terminations was a matter of finishing an already-intended design, not adding new fields. Physical deletion remains available, but only for the narrow case where no real business history could possibly be attached yet (an employee who was created but never activated).

## Decision 6: Domain Exceptions Instead of Per-Endpoint HTTP Checks

CRUD functions (`app/crud/employee.py`) never raise `HTTPException` or know about HTTP status codes. Instead, they raise domain-specific exceptions (`EmployeeNotFound`, `InactiveEmployee`), which are translated to HTTP responses by centralized handlers (`app/exceptions/handlers.py`) registered once at the application level. The same centralization applies to `IntegrityError` (e.g., a username collision under concurrent creation), consistently mapped to `409 Conflict` regardless of which endpoint triggered it.

**Rationale:** the earlier pattern (`if employee is None: raise HTTPException(...)` repeated per router function) duplicated the same check and the same status code decision across every endpoint, and produced inconsistent results in practice (the same conflict returning `409` in one endpoint and `400` in another before this was centralized). Keeping the CRUD layer HTTP-agnostic also means it could be reused by a non-HTTP entry point (a CLI script, a background job) without dragging FastAPI-specific exceptions into it.

## Consequences

### Positive

- Credential and identity concerns for `Employee` are handled consistently, with no plaintext password ever persisted and no password hash ever exposed through the API.
- Employee history is preserved by default; accidental data loss from deleting an active employee's record is not possible through the normal deactivation flow.
- Error handling is uniform across the entity's endpoints, reducing the chance of a new endpoint silently reintroducing an inconsistent status code.

### Trade-offs / Known Gaps

- Username changes on name correction are not yet communicated to the affected employee or externally auditable beyond the updated `username` field itself; this depends on the future email-notification feature referenced in Decisions 1 and 2.
- The physical-deletion guard (`hire_date is None`) assumes `hire_date` is only ever set through `activate_employee`; if `hire_date` becomes settable through another path in the future, this guard must be revisited.
- Username generation under concurrent identical requests relies on catching `IntegrityError` and returning `409` rather than preventing the race outright (e.g., via an advisory lock); this is accepted as sufficient for the current low-concurrency, single-admin usage pattern.

---

Made by [armandx06](https://github.com/armandx06) at September 27, 2026
