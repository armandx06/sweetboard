# ADR 0006: Incremental Table-by-Table Modeling Instead of Full Upfront ER Design

- **Status:** Accepted
- **Date:** September 18, 2026
- **Author:** [armandx06](https://github.com/armandx06)

---

## Context

ADR 0004 established ChartDB as the tool for visually designing the database schema _before_ writing SQLAlchemy models and migrations, with the stated goal of reasoning about relationships and catching design issues before they were encoded into code. In practice, this meant modeling the entire domain in ChartDB — spanning multiple business areas (products, inventory, recipes, production batches, lots) — before any table was implemented in code.

This produced the opposite of the intended effect. The ER diagram kept growing as each new entity revealed dependencies on entities not yet modeled, with no implementation to validate whether the design was actually workable. This led to repeated redesign cycles inside ChartDB itself, no code being written, and eventually the abandonment of the diagram and a restart of the modeling effort from zero — a pattern that had already occurred more than once before this ADR.

The root problem was not the tool, but the scope of a single modeling cycle: designing an entire subsystem (or the entire database) before any part of it touched real code or real data removed any feedback loop that could catch an unworkable design early, cheaply, and concretely.

## Decision

ChartDB remains the tool of choice for ER modeling, per ADR 0004. What changes is the scope and role of that modeling step:

1. **One table (or a tightly coupled small group of tables) is modeled in ChartDB at a time** — never the full remaining schema or an entire future phase.
2. That table is implemented as a SQLAlchemy model and Alembic migration, and tested against real or realistic data, **before** the next table is modeled.
3. ChartDB is treated as a disposable draft for the table currently being worked on, not as the canonical, evolving diagram of the whole system.
4. If implementation reveals that a modeled table needs to change, the correction happens in code and a new migration — not by returning to redesign the diagram.
5. This ADR **amends ADR 0004**: it does not replace the choice of tool, only the workflow around when and how much is designed before code is written.
6. **ADR 0005 is unaffected.** `docs/db/schema.json` and `docs/db/schema.sql` remain the single source of truth in `docs/db/`, per ADR 0005 — the only change is that these files now represent schema that has already been implemented and tested, rather than an aspirational full design.

## Consequences

### Positive

- Smaller feedback loops: a design flaw surfaces after one table's worth of work, not after weeks of modeling an entire subsystem.
- Progress becomes tangible and cumulative — each cycle ends with working, tested code, not a bigger diagram.
- Reduces the incentive for full project restarts, since there is no large, ever-changing diagram to abandon.
- Design decisions become increasingly evidence-based, informed by how earlier tables actually behaved with real data, rather than purely anticipatory.

### Trade-offs

- Less upfront visibility into the full schema at any given point, since only implemented (or currently in-progress) tables are modeled in detail.
- Cross-entity relationships that span future, not-yet-modeled tables may require minor rework once those tables are eventually designed, since they weren't fully anticipated in advance.

---

Made by [armandx06](https://github.com/armandx06) at September 18, 2026
