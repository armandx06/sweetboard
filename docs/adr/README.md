# ARCHITECTURE DECISION RECORDS

Architecture Decision Records (ADRs) capture decisions that affect the structure, workflow, or long-term maintenance of Sweetboard. They explain **why** a choice was made, what alternatives were considered, and what trade-offs were accepted.

ADRs are records of decisions, not tutorials. Current setup instructions live in the root [README](../README.md) and [CONTRIBUTING.md](../../CONTRIBUTING.md); current API and schema details live in [docs/api](../api/README.md) and [docs/db](../db/README.md).

## Index

| ADR                                                                                     | Decision                                                        | Status   | Date       | Notes                        |
| --------------------------------------------------------------------------------------- | --------------------------------------------------------------- | -------- | ---------- | ---------------------------- |
| [0001](./0001-postgres-in-docker-for-development.md)                                    | Run PostgreSQL in Docker with a persistent named volume         | Accepted | 2026-07-26 |                              |
| [0002](./0002-using-asynchronous-sqlalchemy-with-asyncpg.md)                            | Use async SQLAlchemy 2.0 with asyncpg for runtime and Alembic   | Accepted | 2026-07-28 |                              |
| [0003](./0003-ports-environment-variables-naming.md)                                    | Separate host and internal port environment variables           | Accepted | 2026-08-02 |                              |
| [0004](./0004-chartdb-for-er-modeling.md)                                               | Use ChartDB as the local ER modeling tool                       | Accepted | 2026-08-30 | Amended by ADR 0005 and 0006 |
| [0005](./0005-single-source-of-truth-for-database-schema-documentation.md)              | Keep one canonical schema snapshot in `docs/db/`                | Accepted | 2026-09-08 |                              |
| [0006](./0006-incremental-table-by-table-modeling-instead-of-full-upfront-er-design.md) | Model and implement one table group at a time                   | Accepted | 2026-09-18 | Amends ADR 0004              |
| [0007](./0007-employee-identity-credentials-and-lifecycle.md)                           | Server-generated employee credentials and soft-delete lifecycle | Accepted | 2026-09-27 | Amended 2026-11-03           |
| [0008](./0008-shared-addresses-with-per-role-link-tables.md)                            | Share physical addresses and keep role flags in link tables     | Accepted | 2026-10-18 | Amended 2026-11-03           |

The highest number currently in use is **0008**. A new ADR takes the next unused number.

## When to write an ADR

Write one when a decision:

- Changes the database model, migration strategy, or schema documentation workflow.
- Introduces or changes a cross-cutting backend pattern (layering, exceptions, async access).
- Chooses or replaces a tool, service, or infrastructure component.
- Has consequences that future contributors must know to avoid undoing it accidentally.

Do not write an ADR for routine implementation details, dependency bumps, typo fixes, or decisions already fully covered by an existing ADR.

## Naming and format

- File name: `NNNN-kebab-case-title.md`, for example `0009-background-job-runner.md`.
- Title: `# ADR NNNN: Short Decision Title`.
- Start from [`template.md`](./template.md).
- Required metadata: `Status`, `Date`, and `Author` (or `Decider`/`Assigned to`, matching the existing records).
- Use `Amended: YYYY-MM-DD` when extending an accepted ADR without replacing its decision.

## Status lifecycle

| Status       | Meaning                                           |
| ------------ | ------------------------------------------------- |
| `Proposed`   | Under discussion; not yet binding.                |
| `Accepted`   | The decision is in effect.                        |
| `Superseded` | Replaced by a newer ADR; link to the replacement. |
| `Deprecated` | No longer recommended, but not yet replaced.      |

An accepted ADR is not rewritten to pretend the original decision was different. Add an amendment, or create a new ADR that supersedes it.

## Process

1. Copy `template.md` to the next number.
2. Describe the context, the forces at play, the options, and the chosen outcome.
3. Record the consequences, including the negative ones.
4. Add the new record to the index above.
5. If the decision replaces an earlier one, update the old ADR's `Status` to `Superseded` and link to the new record.
6. Commit the ADR with the code or documentation change that implements it.

---

Made by [armandx06](https://github.com/armandx06) at November 3, 2026.
