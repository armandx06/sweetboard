# DOCUMENTATION

This directory is the documentation index for Sweetboard. It describes implemented behavior, not aspirational design.

## Where to start

| Audience / task             | Document                                   |
| --------------------------- | ------------------------------------------ |
| Run the full stack          | [`../README.md`](../README.md)             |
| Contribute code or docs     | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) |
| Call the HTTP API           | [`api/README.md`](./api/README.md)         |
| Understand or change the DB | [`db/README.md`](./db/README.md)           |
| Read architecture decisions | [`adr/README.md`](./adr/README.md)         |
| Inspect the DDL snapshot    | [`db/schema.sql`](./db/schema.sql)         |
| Inspect the ChartDB export  | [`db/schema.json`](./db/schema.json)       |

## Current documentation map

```text
docs/
├── README.md          # This index and documentation rules
├── api/
│   └── README.md      # HTTP endpoints, payloads, errors, examples
├── adr/
│   ├── README.md      # ADR index and process
│   ├── template.md    # Template for new ADRs
│   └── 0001..0008     # Accepted Architecture Decision Records
└── db/
    ├── README.md      # Tables, relationships, constraints, business rules
    ├── schema.sql     # pg_dump --schema-only snapshot
    └── schema.json    # Native ChartDB save/export
```

## Documentation rules

### Keep docs with the change

Update the relevant document in the same change that modifies behavior:

| Change                                  | Update                                                       |
| --------------------------------------- | ------------------------------------------------------------ |
| Endpoint, payload, status code, error   | `docs/api/README.md` and tests                               |
| Table, column, constraint, relationship | Model + Alembic migration + `docs/db/README.md` + snapshots  |
| Architectural or cross-cutting decision | New or amended ADR under `docs/adr/`                         |
| Setup, scripts, ports, test workflow    | Root `README.md`, `apps/api/README.md`, or `CONTRIBUTING.md` |
| Frontend commands or routes             | The corresponding app README                                 |

### Schema documentation

- `docs/db/README.md` is the narrative reference for tables, constraints, and business rules.
- `docs/db/schema.sql` is generated with `pg_dump --schema-only`; it is a snapshot, not a migration source.
- `docs/db/schema.json` is a native ChartDB save/export. Do not hand-edit it.
- Document only tables that are implemented, migrated, and tested, per [ADR 0006](./adr/0006-incremental-table-by-table-modeling-instead-of-full-upfront-er-design.md).
- ChartDB represents tables, columns, and foreign-key relationships, but may omit partial unique indexes and `CHECK` constraints. The README and `schema.sql` remain authoritative for those.

The regeneration procedure is in [`db/README.md`](./db/README.md#maintaining-schemajson-chartdb).

### ADRs

- Every architectural decision gets a numbered ADR using [`adr/template.md`](./adr/template.md).
- Accepted ADRs are historical records. Do not rewrite the original decision; add an `Amended` date and extend the relevant section, or supersede the ADR with a new one.
- The index is in [`adr/README.md`](./adr/README.md).

### Links and style

- Use relative links between documents; do not hard-code absolute repository URLs.
- Keep commands copy-pasteable and state the directory they run from.
- Prefer tables and short sections over long prose.
- Do not duplicate volatile values such as the current Alembic head or endpoint counts in several places. Keep them in the owning document (`docs/db` or `docs/api`).

## Verifying documentation changes

There is no documentation linter or CI. Before committing:

1. Check that relative links resolve.
2. Run the API checks if the change touches code or API docs:

   ```bash
   cd apps/api
   uv run ruff check app tests
   uv run pytest
   ```

3. Run the frontend checks if the change touches an app:

   ```bash
   pnpm --filter landing lint
   pnpm --filter web lint
   pnpm --filter landing build
   pnpm --filter web build
   ```

4. For schema changes, also run `alembic check` and regenerate `docs/db/schema.sql` and the ChartDB export.

---

Made by [armandx06](https://github.com/armandx06) at November 3, 2026.
