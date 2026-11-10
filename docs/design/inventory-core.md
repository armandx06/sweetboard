# INVENTORY CORE — IMPLEMENTATION PLAN

> **Status:** Planned, not implemented. Last updated 2026-11-05.
>
> This document describes the first inventory iteration. It is a plan, not a description of current behavior. The authoritative decisions are [ADR 0009](../adr/0009-product-catalog-with-independent-capabilities.md) and [ADR 0010](../adr/0010-inventory-ledger-lots-and-moving-weighted-average-cost.md), both `Proposed` until the code and tests exist.

## Purpose

Build the smallest inventory core that can answer:

- What products exist and what can each one be used for?
- How much stock is on hand?
- Which lots make up that stock and when do they expire?
- What is the current moving weighted average cost?
- Which products are at or below their minimum stock?
- Which lots are close to expiry or already expired?
- What changes produced the current balance?

Purchases, recipes, production, sales, price lists, and fiscal handling are deliberately out of scope for this iteration.

## Confirmed decisions

| Topic                 | Decision                                                            |
| --------------------- | ------------------------------------------------------------------- |
| Costing               | Moving weighted average (WAC) per product and location              |
| Locations             | One default location, `Principal`, modeled as a table               |
| Units                 | Smallest practical base unit: `g`, `ml`, `piece`                    |
| Sellable products     | One SKU per sellable product                                        |
| Purchases             | Full receipt per purchase; partial receipts are out of scope        |
| Price lists           | Public, consignment, and cash; implemented in the sales iteration   |
| Recipes               | One output per recipe; no by-products                               |
| Waste                 | Not modeled as a recipe output; inventory write-offs remain         |
| Negative stock        | Allowed with a warning and an inventory review report               |
| SKU                   | Manual entry, with automatic `SKU-000001` when omitted              |
| Lot codes             | System-generated code plus optional manufacturer code               |
| Expiration            | Optional, with alerts                                               |
| Currency and language | MXN and Spanish for the UI and calculations; no multi-currency yet  |
| Taxes                 | Out of scope; prices are stored as the final charged amount for now |

## Scope

### In scope

- `units`, `categories`, `locations`, and `products`.
- `inventory_lots`, `inventory_movements`, and `stock_balances`.
- Manual entries, manual exits, adjustments, and expiry write-offs.
- WAC calculation and historical after-state on every movement.
- FEFO consumption for exits.
- Lot expiry alerts, low-stock alerts, and negative-stock alerts.
- Product and inventory read endpoints.
- Tests and documentation for all of the above.

### Out of scope

- Purchases and supplier product catalogs.
- Recipes, production orders, and production suggestions.
- Sales, price lists, consignment, returns, and payments.
- Authentication and permissions.
- Fiscal/SAT, CFDI, and taxes.
- Multi-location transfers.
- Demand forecasting and operations-research optimization.

## Seed data

### Units

| Code    | Name       | Dimension | Factor to base | Base |
| ------- | ---------- | --------- | -------------- | ---- |
| ---     | ---        | ---       | ---:           | ---  |
| `g`     | gram       | mass      | 1              | yes  |
| `kg`    | kilogram   | mass      | 1000           | no   |
| `ml`    | milliliter | volume    | 1              | yes  |
| `l`     | liter      | volume    | 1000           | no   |
| `piece` | piece      | count     | 1              | yes  |
| `dozen` | dozen      | count     | 12             | no   |

### Categories

- Panadería Dulce
- Panadería Salada
- Repostería y Postres Fríos
- Pastelería y Celebraciones
- Galletas y Secos
- Temporada y Tradición
- Bebidas
- Productos de Reventa
- Materia Prima
- Empaques y Desechables
- Insumos de Producción
- Servicios y Envíos

Categories are grouping labels only. A product's capabilities decide whether it is sold, purchased, consumed, or produced.

### Locations

- `Principal` as the default and only active location.

## Data model

| Table                 | Purpose                                                             |
| --------------------- | ------------------------------------------------------------------- |
| `units`               | Measurement units and conversion to the base unit of each dimension |
| `categories`          | Product grouping for catalogs and reports                           |
| `locations`           | Physical stock location; one default row                            |
| `products`            | Catalog with independent capabilities and minimum stock             |
| `inventory_lots`      | Physical lots with remaining quantity, cost, and expiry             |
| `inventory_movements` | Append-only stock and cost ledger                                   |
| `stock_balances`      | Current quantity, value, and WAC per product and location           |

Detailed fields, constraints, and formulas are in the ADRs. Do not duplicate them in several documents.

## API surface

### Catalog

| Method  | Path                     | Purpose                                                     |
| ------- | ------------------------ | ----------------------------------------------------------- |
| `POST`  | `/products`              | Create a product                                            |
| `GET`   | `/products`              | List products with capability, category, and status filters |
| `GET`   | `/products/{product_id}` | Product detail                                              |
| `PATCH` | `/products/{product_id}` | Update or deactivate a product                              |
| `GET`   | `/units`                 | List units                                                  |
| `GET`   | `/categories`            | List categories                                             |
| `POST`  | `/categories`            | Create a category                                           |

Products are deactivated with `PATCH`, never hard-deleted once they have inventory history.

### Inventory

| Method | Path                            | Purpose                                                   |
| ------ | ------------------------------- | --------------------------------------------------------- |
| `POST` | `/inventory/entries`            | Manual entry or initial stock; creates lot and movement   |
| `POST` | `/inventory/exits`              | Manual exit, adjustment, or expiry write-off              |
| `GET`  | `/inventory/stock`              | Balances with `low_stock`, `negative`, and search filters |
| `GET`  | `/inventory/stock/{product_id}` | Balance and lots for one product                          |
| `GET`  | `/inventory/lots`               | Lots filtered by product, expiry window, and status       |
| `GET`  | `/inventory/lots/{lot_id}`      | Lot detail                                                |
| `GET`  | `/inventory/movements`          | Ledger filtered by product, lot, type, and dates          |
| `GET`  | `/inventory/alerts`             | Low stock, negative stock, expiring lots, expired lots    |

Entries and exits accept a quantity and a unit; the API converts to the product base unit and returns the base quantity. Exit responses include warnings when the operation leaves negative stock.

## Implementation plan

### PR 1 — Catalog foundation

- [ ] Add `Unit`, `Category`, `Location`, and `Product` SQLAlchemy models.
- [ ] Export every new model from `app/models/__init__.py`.
- [ ] Create the Alembic migration for the four tables, constraints, and indexes.
- [ ] Add a data migration or seed step for units, categories, and the default location.
- [ ] Add Pydantic schemas for create, update, and read.
- [ ] Add CRUD functions for create, list, get, update, and deactivate.
- [ ] Add SKU generation when the request omits it.
- [ ] Add domain exceptions for duplicate SKU, unknown unit, unknown category, and invalid capability combinations.
- [ ] Add routers for `/products`, `/units`, and `/categories`.
- [ ] Add tests for product creation, capability validation, SKU generation, deactivation, and unit/category reads.
- [ ] Verify `alembic check` reports no pending operations.

### PR 2 — Ledger and cost engine

- [ ] Add `InventoryLot`, `InventoryMovement`, and `StockBalance` models.
- [ ] Export the models and create the migration.
- [ ] Add a monotonic `movement_seq` identity column for ledger order.
- [ ] Implement a pure WAC function that receives the current balance and a movement and returns the next balance.
- [ ] Implement system lot code generation (`LOT-YYYYMMDD-#####`) with a database sequence.
- [ ] Implement row locking for balances and lots.
- [ ] Add unit tests for every WAC scenario in the testing matrix.
- [ ] Add tests for lot code uniqueness and `quantity_remaining >= 0`.
- [ ] Verify `alembic check` reports no pending operations.

### PR 3 — Inventory API

- [ ] Add request and response schemas for entries, exits, stock, lots, movements, and alerts.
- [ ] Implement entry posting: validate product, unit dimension, and cost; create lot, movement, and balance atomically.
- [ ] Implement exit posting: validate product and unit; select lots by FEFO; post lot movements and a lotless movement for any shortfall.
- [ ] Implement expiry write-off limited to the remaining quantity of the lot.
- [ ] Implement stock listing with low-stock and negative-stock filters.
- [ ] Implement lot listing with expiry-window and status filters.
- [ ] Implement movement listing with product, lot, type, and date filters.
- [ ] Implement alerts for low stock, negative stock, expiring lots, and expired lots.
- [ ] Add warnings to responses that leave negative stock.
- [ ] Add integration tests for every endpoint and every error case.
- [ ] Add concurrency tests with `concurrent_client` for simultaneous entries and exits.

### PR 4 — Documentation and acceptance

- [ ] Update `docs/db/README.md` with the implemented tables, constraints, and business rules.
- [ ] Regenerate `docs/db/schema.sql`.
- [ ] Update the ChartDB model and export `docs/db/schema.json`.
- [ ] Update `docs/api/README.md` with every new endpoint, payload, status code, and error.
- [ ] Update this plan's status and remove it from the planned section if the implementation is complete.
- [ ] Move ADR 0009 and ADR 0010 to `Accepted`.
- [ ] Update the ADR index.
- [ ] Run the full verification suite.

## Acceptance criteria

- [ ] A product can be created with any valid combination of capabilities.
- [ ] A service product (`track_inventory = false`) cannot receive stock.
- [ ] A product can be entered with quantity, unit, unit cost, lot data, and optional expiry.
- [ ] The system generates a unique lot code and preserves the manufacturer code.
- [ ] Two entries at different costs produce the expected WAC.
- [ ] An exit uses WAC and FEFO.
- [ ] An exit that crosses zero leaves negative quantity, zero inventory value, and a warning.
- [ ] A later entry revalues a previously negative product correctly.
- [ ] Expiry write-off cannot exceed the lot's remaining quantity.
- [ ] Low-stock, negative-stock, expiring-lot, and expired-lot alerts are correct.
- [ ] Movements are append-only and the balance can be reconstructed from them.
- [ ] `uv run ruff check app tests` passes.
- [ ] `uv run pytest` passes.
- [ ] `alembic check` reports no pending operations.
- [ ] `docs/db/schema.sql`, `docs/db/schema.json`, and `docs/api/README.md` match the implementation.

## Testing matrix

| Area        | Case                                                         | Type        |
| ----------- | ------------------------------------------------------------ | ----------- |
| WAC         | Two receipts at different costs                              | Unit        |
| WAC         | Issue at current average                                     | Unit        |
| WAC         | Issue to exactly zero                                        | Unit        |
| WAC         | Issue beyond zero with a shortfall                           | Unit        |
| WAC         | Receipt after negative stock                                 | Unit        |
| WAC         | Issue with zero stock and a known last cost                  | Unit        |
| WAC         | Decimal rounding with fractional quantities                  | Unit        |
| Lots        | FEFO order with different expiry dates                       | Unit        |
| Lots        | FEFO skips expired, blocked, and empty lots                  | Unit        |
| Lots        | Write-off limited to remaining quantity                      | Integration |
| Catalog     | Capability validation and SKU generation                     | Integration |
| Catalog     | Deactivation keeps history                                   | Integration |
| Inventory   | Entry, stock, lot, and movement reads                        | Integration |
| Inventory   | Negative-stock warning                                       | Integration |
| Inventory   | Low-stock, expiring, and expired alerts                      | Integration |
| Concurrency | Two simultaneous entries on the same product                 | Concurrency |
| Concurrency | Two simultaneous exits on the same product                   | Concurrency |
| Database    | Unique SKU, unique lot code, non-negative remaining quantity | Constraint  |

## Edge cases and risks

- **Unit mismatch:** reject a unit from a different dimension before converting.
- **Inactive products:** reject new movements for inactive products; keep historical reads.
- **Zero and negative stock:** define `inventory_value` and `average_cost` exactly as in ADR 0010, and test the transitions.
- **No last cost:** if a product has never received stock, an exit uses zero cost and returns a warning; the first entry establishes the cost.
- **Backdated events:** use `posted_at` for ledger order and `occurred_at` for the business date. Do not recalculate historical balances in the MVP.
- **Expired lots:** never consume them automatically; require a write-off or an explicit block.
- **Multiple lots with the same expiry:** break ties with `received_at`, then `system_lot_code`.
- **Rounding:** use `Decimal` and six decimals; never use floats.
- **Concurrency:** lock the balance row before computing WAC; lock the lots selected by FEFO.
- **Sequence gaps:** lot code and SKU sequences may have gaps; that is acceptable.
- **Deletion:** never hard-delete products with movements, lots, or balances.

## Future iterations

### Iteration 2 — Purchases and purchase lists

- `purchases`, `purchase_items`, and `supplier_products`.
- Receiving creates lots and posts `purchase_receipt`.
- Purchase lists group low-stock products by preferred supplier, using `target_stock - quantity_on_hand`, pack size, minimum order quantity, and lead time.

### Iteration 3 — Recipes and production

- `recipes`, `recipe_items`, `production_orders`, `production_consumptions`, and `production_outputs`.
- One output per recipe; no by-products.
- Produced lots use the actual production cost and `expiration_date = production date + shelf_life_days`.
- Production suggestions are simple first; optimization comes later.

### Iteration 4 — Sales and price lists

- `sales`, `sale_items`, `price_lists`, and `product_prices`.
- Public, consignment, and cash lists with different return policies.
- FEFO issue and frozen COGS per line.
- Consignment semantics (sale versus stock transfer) must be decided before implementation.

### Later

- Multi-location transfers.
- Authentication and permissions.
- Fiscal/SAT and tax handling.
- Demand forecasting and operations-research optimization using sales, purchase, cost, and expiry history.
- Bilingual UI and currency equivalence.

## Resolved questions

1. **SKU:** manual, with automatic `SKU-000001` when omitted.
2. **Categories:** the twelve categories listed above.
3. **Target stock:** optional; suggestions fall back to `minimum_stock * 2`.
4. **Lot codes:** system-generated, with an optional manufacturer code.
5. **Expiration:** optional, with alerts.
6. **Currency:** MXN; Spanish UI for now.
7. **Negative stock:** allowed with warning; shortfall cost uses `last_cost`; inventory value never negative.
8. **Write-off:** limited to the lot's remaining quantity.
9. **Locations:** included from the start with one default row.
10. **Prices:** stored as the final charged amount for now; tax treatment is deferred.

## Notes

- Follow the layering and async rules in [AGENTS.md](../../AGENTS.md) and [CONTRIBUTING.md](../../CONTRIBUTING.md).
- Do not document tables in `docs/db/` until they are implemented, migrated, and tested.
- Keep this plan and the ADRs in sync; if a decision changes, amend the ADR instead of silently editing the plan.

---

Made by [armandx06](https://github.com/armandx06) at November 5, 2026.
