# ADR 0008: Shared Addresses with Per-Role Link Tables

- **Status:** Accepted
- **Date:** October 18, 2026
- **Amended:** November 11, 2026
- **Author:** [armandx06](https://github.com/armandx06)

---

## Context

Employees, customers, and suppliers all need one or more addresses. The initial design, drafted in ChartDB for customers only, modeled this as a one-to-many relationship: `addresses.customer_id` referenced `customers.id`, and the flags `is_default` and `is_billing` lived on `addresses`.

That design does not scale to the rest of the domain, for two reasons:

1. **The same real-world person can hold several roles.** A customer can also be a supplier, and a customer can also be an employee. They live at the same physical address, but with a single owner column on `addresses` the only option would be to duplicate the address row once per role.
2. **Every new role would force a change to `addresses`.** Adding `supplier_id` and `employee_id` columns to the same table would turn it into a table that must be altered for each new type of subject.

Employee, Customer, and Supplier are already implemented as independent tables sharing `PersonMixin` (ADR 0007 and subsequent work), so any solution must work with them as they are.

## Considered Options

1. **Nullable foreign key per subject on `addresses`** (`customer_id`, `supplier_id`, `employee_id`, with a `CHECK` that only one is set). Rejected: an address row still belongs to exactly one subject, so sharing is impossible, and the table changes with every new role.
2. **Polymorphic association** (`subject_type` + `subject_id`). Rejected: a polymorphic `subject_id` cannot carry a real foreign key, so referential integrity would be enforced only in application code.
3. **A common `people` supertype table, with roles as extensions of it.** The cleanest model for "one person, several roles", but it requires restructuring Employee, Customer, and Supplier, which are already implemented and tested. Deferred, not discarded (see Consequences).
4. **A general `addresses` table plus one link table per role.** Chosen.

## Decision

Addresses are modeled as a many-to-many relationship between each role that can hold several addresses and a shared `addresses` table. Locations, which have exactly one address, use a direct foreign key instead; see [Location addresses use a direct foreign key](#location-addresses-use-a-direct-foreign-key-november-11-2026).

```sql
addresses(
    id,
    street,
    exterior_number,
    interior_number,
    neighborhood,
    city,
    state,
    postal_code,
    country,
    address_notes,
    latitude,
    longitude
)
customer_addresses  (customer_id, address_id, is_default, is_billing, active, activated_at, deactivated_at)
supplier_addresses  (supplier_id, address_id, is_default, is_billing, active, activated_at, deactivated_at)
employee_addresses  (employee_id, address_id, is_default, active, activated_at, deactivated_at)
```

1. **`addresses` describes only a physical place.** It has no owner column and no flag that depends on who uses it. This is unrelated to the inventory `locations` table described below.
2. **One link table per role** (`customer_addresses`, `supplier_addresses`, `employee_addresses`). Each link table has real foreign keys to its role table and to `addresses`, so integrity is enforced by the database.
3. **Relationship attributes live in the link tables, not in `addresses`.** `is_default` and `is_billing`, which the earlier customer-only design placed on `addresses`, describe how a particular subject uses an address, so they move to the link tables. Which attributes each link table carries is decided when that table is implemented; customers and suppliers keep both, while employee addresses intentionally omit `is_billing` (migration `e423c02db1c6`).
4. **Composite primary key `(subject_id, address_id)`** on each link table, with no surrogate id. This prevents linking the same address twice to the same subject.
5. **At most one default address per subject**, enforced by a partial unique index on `subject_id` where `is_default` is true.
6. **Foreign key behavior:**
   - `subject_id` is `ON DELETE CASCADE`: if a subject is physically deleted (reserved for data-entry errors, per ADR 0007), its link rows disappear with it.
   - `address_id` is `ON DELETE RESTRICT`: an address that is still linked to any subject cannot be deleted.
7. **An index on `address_id` in each link table.** The composite primary key only helps lookups by `subject_id`; the extra index supports finding every subject that shares an address and the `RESTRICT` check on deletion.
8. **Implementation order follows ADR 0006:** `addresses` and `customer_addresses` first, then `supplier_addresses` and `employee_addresses`, each implemented, migrated, and tested before the next. This order has been completed; `docs/db/schema.json` and `docs/db/schema.sql` now reflect the resulting schema.

### Address link lifecycle and API semantics

- Each link row has `active`, `activated_at`, and `deactivated_at`. Creating a link sets `active = true` and `activated_at = today`.
- `DELETE /{role}/{id}/addresses/{address_id}` is a soft delete of the link: it sets `active = false`, `deactivated_at = today`, clears `is_default`, and clears `is_billing` for customers and suppliers. The shared row in `addresses` is not deleted.
- At most one link per subject may have `is_default = true`; the CRUD layer clears the previous default before setting a new one.
- Employee addresses expose `is_default` but not `is_billing`.
- Editing a shared address changes it for every role linked to that address.

### Implementation status (November 3, 2026)

All three link tables, their lifecycle fields, and their CRUD endpoints are implemented and tested. The employee billing flag was removed by migration `e423c02db1c6`, and the lifecycle fields were added by `c4f8a1d2b6e3`.

### Location addresses use a direct foreign key (November 11, 2026)

Locations are deliberately excluded from the link-table pattern. A location is a physical place that holds stock, so it has exactly one address and needs none of the per-link attributes that justify the role tables:

```sql
locations(
    id,
    name,
    address_id,        -- not null, references addresses (id) on delete restrict
    is_default,
    active,
    activated_at,
    deactivated_at,
    created_at,
    updated_at
)
```

1. **`locations.address_id` is a direct, non-null foreign key.** There is no `location_addresses` table.
2. **`ON DELETE RESTRICT`**: an address referenced by a location cannot be deleted. This extends the protection that link tables already provide for customers, suppliers, and employees.
3. **An index on `address_id`.** PostgreSQL does not index foreign keys automatically; the index supports both the `RESTRICT` check and lookups of every location that shares an address.
4. **Addresses remain ownerless and shareable.** Multiple locations may reference the same `addresses` row; `address_id` is not unique. Sharing an address does not imply that the locations are the same entity.
5. **Location lifecycle lives on `locations`.** `is_default`, `active`, `activated_at`, and `deactivated_at` describe the location, not its use of an address, so they do not belong in a link table.
6. **At most one default location**, enforced by a partial unique index on `is_default` where `is_default = true`, mirroring the one-default rule for the role link tables.

This exception holds while the cardinality stays at exactly one address per location. If a location ever needs separate delivery and billing addresses, or a history of previous addresses, the decision must be revisited with a link table similar to the role tables. The `addresses` row itself would not change.

## Consequences

### Positive

- One address row can serve a person who is at once a customer, a supplier, and an employee, without duplication.
- Adding a role that needs addresses means adding a link table; `addresses` does not change.
- Referential integrity is enforced by real foreign keys on every relationship.
- Flags such as default and billing are stored where they are actually true: per subject, not per address.

### Trade-offs

- Three link tables mean more tables, migrations, and CRUD than a single foreign key would.
- **Editing a shared address changes it for every subject linked to it.** Correcting a typo is intended to propagate, but moving one subject to a new address means creating a new address row and re-linking, not editing in place.
- **Nothing in the database states that a customer, a supplier, and an employee are the same person.** Sharing an address is the only implicit signal, and name and contact data remain duplicated across the three role tables and can diverge. A future `people` supertype (option 3) would address this and would let the three link tables collapse into one; `addresses` itself would not change.
- Unlinking an address can leave an orphan row in `addresses`; a cleanup policy is deferred until it becomes a real problem.
- Changing a subject's default address requires unsetting the previous default and setting the new one in the same transaction, because of the partial unique index.
- Reading "the addresses of customer X" requires a join through the link table.
- Locations are the exception: they use a direct `address_id` foreign key instead of a link table. This keeps the model simpler, but a future need for multiple addresses per location requires a migration to a link table.

## Amendments

- **November 3, 2026:** Address link tables gained `active`, `activated_at`, and `deactivated_at` (migration `c4f8a1d2b6e3`), and employee links dropped `is_billing` (migration `e423c02db1c6`). See [Address link lifecycle and API semantics](#address-link-lifecycle-and-api-semantics).
- **November 11, 2026:** Locations were added to the address model as a direct `locations.address_id` foreign key rather than a `location_addresses` link table. A location has exactly one address and no per-link flags, so the many-to-many pattern does not apply. The `addresses` table remains ownerless, and `ON DELETE RESTRICT` protects an address that any location uses. See [Location addresses use a direct foreign key](#location-addresses-use-a-direct-foreign-key-november-11-2026).

---

Made by [armandx06](https://github.com/armandx06) at October 18, 2026. Amended November 11, 2026.
