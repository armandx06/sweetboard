# DB DOCS — Database Architecture & Schema

## Overview

This document serves as the single source of truth for the application's database schema. It unifies all domain models including SAT fiscal catalogs, customer management, and address structures—into a single root documentation layout.

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

### SAT Fiscal Catalogs

Reference catalogs imported from official SAT specifications to support CFDI 4.0 invoicing logic:

- `payment_methods`
  - `sat_code` (text, PK)
  - `sat_method` (enum `sat_method` — values: `PUE`, `PDD`)
  - `description` (text)
  - `requires_reference` (boolean, default `false`)

- `cfdi_uses`
  - `sat_code` (text, PK)
  - `description` (text)
  - `applies_to_individual` (boolean, default `true`)
  - `applies_to_company` (boolean, default `true`)

- `tax_systems`
  - `sat_code` (text, PK)
  - `description` (text)
  - `applies_to_individual` (boolean, default `true`)
  - `applies_to_company` (boolean, default `true`)

- `tax_system_cfdi_uses` (junction table)
  - `tax_system_code` (text, FK)
  - `cfdi_use_code` (text, FK)
  - Primary key: (`tax_system_code`, `cfdi_use_code`)

- `sat_product_codes`
  - `sat_code` (text, PK)
  - `type` (text)
  - `description` (text)

### Customer Reference Data

Domain entities for client management, billing parameters, and shipping/billing addresses:

- `customers`
  - `id` (uuid PK, default `gen_random_uuid()`)
  - `first_name` (text)
  - `last_name` (text)
  - `company_name` (text, nullable)
  - `is_company` (boolean, default `true`)
  - `rfc` (text, nullable)
  - `tax_system_code` (text, nullable, FK)
  - `default_cfdi_use` (text, nullable, FK)
  - `requires_invoice` (boolean, default `false`)
  - `phone_number` (text)
  - `email` (text, nullable)
  - `active` (boolean, default `false`)
  - `activated_at` (date, nullable)
  - `deactivated_at` (date, nullable)
  - `created_at` (timestamptz, default `CURRENT_TIMESTAMP`)
  - `updated_at` (timestamptz, nullable)

- `addresses`
  - `id` (uuid PK, default `gen_random_uuid()`)
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

---

## Custom types

- `sat_method`: ENUM with values `'PUE'`, `'PDD'` (declared in the JSON and SQL exports).

---

## Relationships & constraints

### Foreign keys

- `tax_system_cfdi_uses.tax_system_code` → `tax_systems.sat_code`
- `tax_system_cfdi_uses.cfdi_use_code` → `cfdi_uses.sat_code`
- `customers.tax_system_code` → `tax_systems.sat_code`
- `customers.default_cfdi_use` → `cfdi_uses.sat_code`
- `addresses.customer_id` → `customers.id`

### Checks and validation notes

- **SAT Codes**: Stored as `text` to preserve exact external catalog identifiers (e.g., leading zeros or alphanumeric keys).
- **Postal Code**: Strict length validation `length(postal_code) = 5`.
- **RFC**: Validated for Mexican fiscal standards `length(rfc) in (12, 13)`.
- **DDL Fix Requirement**: Note that initial raw exports may contain invalid check syntax (e.g., `CHECK (first_name > 1)`, `CHECK (phone_number >= 10)`). These must be corrected to use string length syntax prior to applying in production:
  - `CHECK (length(first_name) > 1)`
  - `CHECK (length(phone_number) >= 10)`

### Partial unique index requirement

To enforce that a customer can have at most **one** default shipping address and **one** default billing address, apply partial unique indexes:

```sql
CREATE UNIQUE INDEX ux_addresses_customer_default
  ON public.addresses (customer_id)
  WHERE is_default = true;

CREATE UNIQUE INDEX ux_addresses_customer_billing
  ON public.addresses (customer_id)
  WHERE is_billing = true;
```

(In SQLAlchemy models, implement via **table_args** using postgresql_where).

## Decisions and notes

- SAT Codes as text: Preserved as text (instead of integers) to maintain exact parity with official external catalogs and preserve leading zeros.
- UUID Primary Keys: Used uuid (gen_random_uuid()) for business entity primary keys (customers, addresses) to simplify distribution, replication, and client-side ID generation.
- Timestamping: created_at uses timestamptz default. Application logic or database triggers manage updated_at.
- Single Source of Truth: Snapshots are managed entirely through Git commits on docs/db/schema.json and docs/db/schema.sql, avoiding folder duplication.

---

Exported from ChartDB on August 30, 2026.

Made by [armandx06](https://github.com/armandx06) at September 8, 2026
