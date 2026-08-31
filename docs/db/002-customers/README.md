# DB DOCS: 002 — Customer Reference Data

## What changed

This snapshot adds the `customers` and `addresses` tables and links customers to the SAT catalogs (`tax_systems`, `cfdi_uses`) introduced in snapshot 001.

---

## Contents

| File                                                                 | Description                            |
| -------------------------------------------------------------------- | -------------------------------------- |
| [docs/db/002-customers/schema.sql](docs/db/002-customers/schema.sql) | DDL SQL dump (truth for this snapshot) |
| [docs/db/002-customers/README.md](docs/db/002-customers/README.md)   | This document                          |

---

## Tables (summary)

- `customers`
  - `id` (uuid PK)
  - `first_name` (text)
  - `last_name` (text)
  - `company_name` (text, nullable)
  - `is_company` (boolean, default `true`)
  - `rfc` (text, nullable)
  - `tax_system_code` (text, nullable)
  - `default_cfdi_use` (text, nullable)
  - `requires_invoice` (boolean, default `false`)
  - `phone_number` (text)
  - `email` (text, nullable)
  - `active` (boolean, default `false`)
  - `activated_at` (date, nullable)
  - `deactivated_at` (date, nullable)
  - `created_at` (timestamptz)
  - `updated_at` (timestamptz, nullable)

- `addresses`
  - `id` (uuid PK)
  - `customer_id` (uuid, FK)
  - `street` (text)
  - `exterior_number` (text)
  - `interior_number` (text, nullable)
  - `neighborhood` (text)
  - `city` (text)
  - `state` (text)
  - `postal_code` (text)
  - `country` (text)
  - `address_notes` (text, nullable)
  - `latitude` (numeric(10,8), nullable)
  - `longitude` (numeric(11,8), nullable)
  - `is_default` (boolean, default `false`)
  - `is_billing` (boolean, default `false`)

## Custom types

- No new custom types are declared in this snapshot (the `sat_method` enum is defined in snapshot 001).

## Relationships & constraints

- Foreign keys:
  - `customers.tax_system_code` → `tax_systems.sat_code`
  - `customers.default_cfdi_use` → `cfdi_uses.sat_code`
  - `addresses.customer_id` → `customers.id`

- Checks and validation notes (review before production):
  - RFC length: `length(rfc) in (12,13)` (present in DDL).
  - Postal code: `length(postal_code) = 5`.
  - The DDL contains invalid checks (`CHECK (first_name > 1)`, `CHECK (phone_number >= 10)`) that should be corrected (use `length(...)` or regex-based checks).

- Partial unique index requirement (enforce at-most-one default/billing address per customer):

  ```sql
  CREATE UNIQUE INDEX ux_addresses_customer_default ON public.addresses (customer_id)
    WHERE is_default = true;

  CREATE UNIQUE INDEX ux_addresses_customer_billing ON public.addresses (customer_id)
    WHERE is_billing = true;
  ```

## Decisions and notes

- Use `uuid` (`gen_random_uuid()`) for PKs to simplify replication and client-side generation.
- `created_at` uses `timestamptz` and is set by the DB default; update `updated_at` via application logic or a trigger.
- Review and fix the invalid check constraints in the DDL before applying to production.

---

Exported from ChartDB on August 30, 2026.

Made by [armandx06](https://github.com/armandx06) at August 30, 2026
