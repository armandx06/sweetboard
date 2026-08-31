# DB DOCS: 001 — SAT Fiscal Catalogs

## What changed

This snapshot contains the initial SAT reference catalogs consumed by the application: payment methods, CFDI uses, tax systems, and SAT product codes. The snapshot includes a ChartDB JSON export and a DDL SQL dump for review and versioning.

---

## Contents

| File                                                       | Description                            |
| ---------------------------------------------------------- | -------------------------------------- |
| [docs/db/001-sat/schema.json](docs/db/001-sat/schema.json) | ChartDB native export (re-importable)  |
| [docs/db/001-sat/schema.sql](docs/db/001-sat/schema.sql)   | DDL SQL dump (useful for diffs in PRs) |
| [docs/db/001-sat/README.md](docs/db/001-sat/README.md)     | This document                          |

---

## Tables (summary)

- `payment_methods`
  - `sat_code` (PK, text)
  - `sat_method` (enum `sat_method` — values: PUE, PDD)
  - `description` (text)
  - `requires_reference` (boolean, default `false`)

- `cfdi_uses`
  - `sat_code` (PK, text)
  - `description` (text)
  - `applies_to_individual` (boolean, default `true`)
  - `applies_to_company` (boolean, default `true`)

- `tax_systems`
  - `sat_code` (PK, text)
  - `description` (text)
  - `applies_to_individual` (boolean, default `true`)
  - `applies_to_company` (boolean, default `true`)

- `tax_system_cfdi_uses` (junction table)
  - `tax_system_code` (text)
  - `cfdi_use_code` (text)
  - Primary key: (`tax_system_code`, `cfdi_use_code`)
  - Foreign keys to `tax_systems.sat_code` and `cfdi_uses.sat_code`

- `sat_product_codes`
  - `sat_code` (PK, text)
  - `type` (text)
  - `description` (text)

## Custom types

- `sat_method`: enum with values `PUE`, `PDD` (declared in the JSON and SQL exports).

## Relationships & constraints

- `tax_system_cfdi_uses` enforces referential integrity to `tax_systems` and `cfdi_uses` using foreign keys.
- SAT codes are stored as `text` to preserve exact external catalog identifiers (no integer casting).

## Decisions and notes

- Use `text` for SAT codes to keep parity with official catalogs and external imports.
- Default boolean values are preserved from the ChartDB export.
- The `sat_method` enum centralizes accepted payment method values.

---

Exported from ChartDB on August 30, 2026.

Made by [armandx06](https://github.com/armandx06) at August 30, 2026
