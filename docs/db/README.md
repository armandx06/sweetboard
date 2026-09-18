# DB DOCS — Database Architecture & Schema

## Overview

This document serves as the single source of truth for the application's database schema. It documents only entities that have already been implemented as SQLAlchemy models and Alembic migrations, and validated against real or realistic data — per the incremental, table-by-table modeling workflow described in [ADR 0006](../adr/0006-incremental-table-by-table-modeling-instead-of-full-upfront-er-design.md).

Visual design files and full DDL dumps are kept synchronized at the root level of `docs/db/`.

---

## Contents

| File                                         | Description                                                |
| -------------------------------------------- | ---------------------------------------------------------- |
| [`docs/db/schema.json`](docs/db/schema.json) | ChartDB native export (re-importable for ER modeling)      |
| [`docs/db/schema.sql`](docs/db/schema.sql)   | Full DDL SQL dump (useful for diffs in PRs and migrations) |
| [`docs/db/README.md`](docs/db/README.md)     | This document                                              |

---

## Tables (summary)

_No tables documented yet. Each table is added here only after its model and migration are implemented and tested, per ADR 0006._

---

## Custom types

_None yet._

---

## Relationships & constraints

### Foreign keys

_None yet._

### Checks and validation notes

_None yet._

---

## Decisions and notes

- **Single Source of Truth:** Snapshots are managed entirely through Git commits on `docs/db/schema.json` and `docs/db/schema.sql`, avoiding folder duplication (see [ADR 0005](../adr/0005-single-source-of-truth-for-database-schema-documentation.md)).
- **Incremental modeling:** Entities are added to this document one table (or one tightly coupled small group of tables) at a time, only once implemented and tested — not as an upfront full design (see [ADR 0006](../adr/0006-incremental-table-by-table-modeling-instead-of-full-upfront-er-design.md)).

---

Made by [armandx06](https://github.com/armandx06) at September 18, 2026
