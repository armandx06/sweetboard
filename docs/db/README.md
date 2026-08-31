# DATABASE SCHEMA SNAPSHOTS

---

## Naming convention

Each snapshot is a numbered folder, similar to ADRs:

```text
docs/db/
├── schema.json      # Global full-schema backup (re-importable)
├── schema.sql       # Global full-schema DDL (latest state)
├── 001-sat/
│   ├── schema.json  # Snapshot-specific ChartDB export
│   ├── schema.sql   # Snapshot-specific DDL export
│   └── README.md    # What changed, why, key decisions...
├── 002-customers/
└── ...
```

Numbering is sequential and independent of the phase roadmap — a schema change doesn't need to correspond to a full phase (see [ADR 0004](../adr/0004-chartdb-for-er-modeling.md)). Minor revisions to an already-numbered schema (e.g. renaming a column, adding an index) are documented in that same folder's README instead of creating a new one.

Create a new numbered folder when the change is structural enough to be worth a distinct snapshot — new tables, changed relationships, or a decision worth explaining on its own.

## Incremental Approach & Full Recovery

To maximize practicality and avoid massive data redundancy, each schema inside a numbered folder represents only snapshot during that specific phase.

For full database recovery or to view the complete, up-to-date schema layout, refer to the global docs/db/schema.json and docs/db/schema.sql files at the root level, which always contain the most recent state of the entire ecosystem.

---

## Snapshot contents

| File          | Description                                                     |
| ------------- | --------------------------------------------------------------- |
| `schema.json` | ChartDB's native export format for that specific snapshot phase |
| `schema.sql`  | Plain DDL export, kept for readable diffs in pull requests      |
| `README.md`   | What changed in this snapshot, why, and any key decisions       |

---

Made by [armandx06](https://github.com/armandx06) at August 30, 2026
