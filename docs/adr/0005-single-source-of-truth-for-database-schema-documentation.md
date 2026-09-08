# ADR 0005: Single Source of Truth for Database Schema Documentation

- **Status:** Accepted
- **Date:** September 8, 2026
- **Author:** [armandx06](https://github.com/armandx06)

---

## Context

Previously, database schema documentation was managed using sequentially numbered snapshot folders for each schema milestone (e.g., `docs/db/001-sat/`, `docs/db/002-customers/`), loosely inspired by ADR numbering. Each folder contained:

- A snapshot-specific ChartDB export (`schema.json`)
- A snapshot-specific DDL export (`schema.sql`)
- A local `README.md` describing changes for that specific snapshot

While this approach provided isolated history per feature milestone, it introduced several drawbacks as the project evolved:

1. **Data Redundancy & Directory Clutter:** Re-exporting full `schema.json` and `schema.sql` files into new subdirectories generated significant file duplication.
2. **Ambiguity of Current State:** Finding the definitive, up-to-date schema required navigating to the highest-numbered directory or checking root overrides.
3. **Redundant Versioning:** Git natively tracks line-by-line file evolution, commit histories, and pull request diffs. Maintaining folder-based snapshots replicated what Git already handles out of the box.

## Decision

We will transition from snapshot-based folders to a **Single Source of Truth (SSOT)** structure maintained directly inside `docs/db/`.

1. **Canonical Files at Root:**
   - `docs/db/schema.json`: Active ChartDB export representing the current ER model.
   - `docs/db/schema.sql`: Active DDL SQL dump representing the target database state.
   - `docs/db/README.md`: Consolidated documentation detailing all active entities, custom types, constraints, and business rules.
2. **Deprecation of Snapshot Subfolders:**
   - Sequential milestone folders (`docs/db/001-*/`, `docs/db/002-*/`, etc.) are removed.
3. **Delegation of Schema History to Git:**
   - Schema evolution and past iterations are tracked strictly via Git commits, tags, and PR diffs.
   - Past states can be inspected using standard Git commands (e.g., `git show <tag/commit>:docs/db/schema.sql`).
4. **Architectural Rationale:**
   - High-level architectural decisions regarding database design will continue to be recorded as ADRs in `docs/adr/`.

## Consequences

### Positive

- **Streamlined Maintenance:** Eliminates directory sprawl and file duplication.
- **Clear PR Diffs:** Changes to tables, columns, or constraints are instantly readable in Pull Requests against `main`.
- **Single Reference Point:** Developers and tools have one predictable location for the latest schema (`docs/db/`).

### Trade-offs

- **Historical Inspection:** Viewing a past schema snapshot requires standard Git commands (`git log`, `git show`) rather than browsing a folder in the file tree.

## Notes

Recommended to minify the schema.json after each update to reduce file size and improve version control.

---

Made by [armandx06](https://github.com/armandx06) at September 8, 2026
