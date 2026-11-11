# ADR 0009: Product Catalog with Independent Capabilities

- **Status:** Proposed
- **Date:** 2026-11-05
- **Author:** Jorge Armando Ceras Cárdenas - [armandx06](https://github.com/armandx06)

---

## Context and Problem Description

Sweetboard needs a catalog that supports several kinds of items at the same time:

- Goods sold to customers.
- Supplies purchased from suppliers.
- Ingredients consumed by recipes.
- Goods produced in-house from recipes.
- Services that are sold but do not hold stock.

A single item can hold more than one role. A sauce may be purchased, sold, and used in recipes. Bread may be bought from a supplier on some days and baked in-house on others. A product may be sold and also consumed as an ingredient. Modeling these roles as one mutually exclusive `type` would force the business to duplicate items or lose information.

The pre-implementation model used an `inventory` table with `is_purchased`, `is_manufactured`, and `is_sellable` flags, plus `unit_cost` and `sale_price` on the item itself. That model was never implemented. It also mixed catalog data with derived cost and with a single sale price, which does not support multiple price lists.

The fiscal/SAT domain remains out of scope for the MVP. This decision does not add tax fields or CFDI catalogs.

## Decision Drivers

- One SKU must be able to combine selling, purchasing, recipe use, and in-house production.
- Purchases, recipes, production, and sales need to filter the same catalog by capability.
- Adding a new capability must not require changing the identity of existing products.
- Services must live in the same catalog without creating fake stock.
- Cost must be derived from inventory, not stored as a mutable field on the product.
- Sale prices must support multiple price lists (public, consignment, cash) without duplicating products.
- The model must remain small enough for an MVP and follow the incremental approach of [ADR 0006](./0006-incremental-table-by-table-modeling-instead-of-full-upfront-er-design.md).

## Options Considered

1. **Single enum `product_type`:** one value such as `sellable`, `raw_material`, or `service`.
2. **Separate tables per kind:** `sellable_products`, `raw_materials`, `packaging`, and so on.
3. **Single `products` table with independent capability flags:** one identity and several booleans.
4. **Capability join table:** `product_capabilities(product_id, capability)` with one row per capability.

## Decision Outcome

Chosen option: **Option 3, a single `products` table with independent capability flags.**

```text
products
├── is_sellable           → can be sold
├── is_purchasable        → can be purchased from suppliers
├── is_recipe_component   → can be consumed by recipes
├── is_manufactured       → can be produced from a recipe
└── track_inventory       → holds stock (false for services)
```

`is_manufactured` expresses that the product is producible; it does not imply that an active recipe exists. The recipe itself is introduced in a later iteration.

`track_inventory = false` is used for services and other non-stock items. Those products never create lots, movements, or balances.

The product does **not** store `unit_cost` or `sale_price`:

- Cost is derived from the inventory ledger and the moving weighted average defined in [ADR 0010](./0010-inventory-ledger-lots-and-moving-weighted-average-cost.md).
- Sale prices belong to price lists, because the same product can have public, consignment, and cash prices.

### Implementation Details

Minimum product fields:

```text
products
├── id                 uuid primary key
├── sku                varchar, unique, required
├── name               varchar, required
├── description        text, nullable
├── category_id        uuid, nullable, references categories
├── base_unit_id       uuid, required, references units
├── is_sellable        boolean, default false
├── is_purchasable     boolean, default false
├── is_recipe_component boolean, default false
├── is_manufactured    boolean, default false
├── track_inventory    boolean, default true
├── minimum_stock      numeric, default 0
├── target_stock       numeric, nullable
├── shelf_life_days    integer, nullable
├── active             boolean, default false
├── activated_at       date, nullable
├── deactivated_at     date, nullable
├── created_at         timestamptz
└── updated_at         timestamptz
```

Rules:

- At least one capability must be true.
- `minimum_stock >= 0`.
- `target_stock` is either null or greater than or equal to `minimum_stock`.
- `shelf_life_days` is either null or greater than or equal to zero.
- If `track_inventory` is false, `minimum_stock` must be zero and `target_stock` must be null.
- `sku` is unique. It may be entered manually; when omitted, the API generates a sequential value such as `SKU-000001`.
- Products are deactivated with `active = false`, not deleted, once they have inventory history.
- `active` defaults to false, so a newly created product must be activated explicitly. Activation sets `activated_at`; deactivation sets `deactivated_at`.
- Authorization is not implemented yet; a future authentication and roles layer will decide who may activate or deactivate catalog records.

### Units

Products reference a base unit. The `units` table is shared by inventory, recipes, and future production planning:

```text
units
├── id               uuid primary key
├── code             varchar, unique, required
├── name             varchar, unique, required
├── dimension        mass | volume | count | time | temperature | length
├── factor_to_base   numeric, greater than zero
└── is_base          boolean
```

- `id` is the technical key used by foreign keys such as `products.base_unit_id`; `code` is the human-readable, stable key used in the UI, imports, and reports.
- Exactly one unit per dimension has `is_base = true`, enforced by a partial unique index.
- A base unit has `factor_to_base = 1`; every other unit in the dimension converts to the base by multiplying by its factor.
- A unit referenced by a product must not change its `code`, `dimension`, or `factor_to_base`; create a new unit instead. Changing the factor would retroactively alter every quantity already recorded in that unit.
- `mass`, `volume`, and `count` cover inventory quantities. `time`, `length`, and `temperature` are reserved for recipe steps and production planning, where baking time, pan size, and oven temperature matter as much as the ingredient list.
- Conversion is multiplicative. Temperature is an affine scale, so the first iteration stores a canonical temperature unit and does not convert between Celsius and Fahrenheit; if imperial or bilingual output is added later, the model will need an `offset_to_base` column.

Categories are grouping and reporting labels only. They do not determine capabilities, and a category may be created without a description. The planned starting set is:

```text
Panadería Dulce
Panadería Salada
Repostería y Postres Fríos
Pastelería y Celebraciones
Galletas y Secos
Temporada y Tradición
Bebidas
Productos de Reventa
Materia Prima
Empaques y Desechables
Insumos de Producción
Servicios y Envíos
```

Units, categories, and products are registered through the API by an administrator. There is no seed migration: the system starts with an empty catalog, and tests create their own fixtures from payloads.

The API exposes filters for each capability so that purchases, recipes, production, and sales can request only the products they need.

## Consequences

### Positive

- One product identity can be sold, purchased, consumed, and produced without duplication.
- Purchases, recipes, sales, and production share one catalog.
- Services fit the same model without fake inventory.
- Cost and price concerns stay out of the catalog table.
- Adding a new capability is a boolean change unless the number of capabilities grows enough to justify a join table.

### Negative / Trade-offs

- Capability flags can contradict each other; the application must validate them.
- `is_manufactured` does not guarantee a usable recipe; production must check for an active recipe.
- A boolean set is less flexible than a capability table. If capabilities become numerous or need metadata, the model will need a migration to `product_capabilities`.
- Type-specific data such as supplier SKUs, price lists, and recipe yields must live in separate tables.

## Notes

- Inventory, lots, and cost are defined in [ADR 0010](./0010-inventory-ledger-lots-and-moving-weighted-average-cost.md).
- The implementation plan is in [`docs/design/inventory-core.md`](../design/inventory-core.md).
- Fiscal/SAT, CFDI, and taxes remain out of scope for the MVP.
- This ADR is `Proposed` until the catalog and its tests are implemented.

---

Created by [armandx06](https://github.com/armandx06) at November 5, 2026.
