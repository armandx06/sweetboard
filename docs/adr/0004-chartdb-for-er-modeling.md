# ADR 0004: Tool for ER Modeling

- **Status:** Accepted
- **Date:** August 30, 2026
- **Assigned to:** Jorge Armando Ceras Cárdenas - [armandx06](https://github.com/armandx06)

## Context and Problem Description

Before writing SQLAlchemy models and Alembic migrations, the project needs a way to visually design the database schema (ER diagrams) during development. Designing the schema directly in code, without a visual step first, makes it harder to reason about relationships and catch design issues before they're encoded into models and migrations.

## Factors Behind the Decision

The tool needs to satisfy three factors:

- **Open source:** the project should not depend on a proprietary SaaS tool, its pricing changes, or its availability.
- **Easy integration:** it must run as a single, isolated service inside the existing Docker-based development environment, without requiring changes to the application stack.
- **Security in local use:** since it will handle the project's real schema, including business-sensitive entities, it must run entirely on the developer's machine, with no data leaving it.

## Options Considered

1. Design the schema directly in SQLAlchemy models, without a dedicated ER modeling tool
2. Use a proprietary, cloud-hosted ER modeling tool
3. Use an open-source, self-hostable ER modeling tool

## Outcome of the decision

Option 3 was chosen. ChartDB was selected as the specific tool, since it satisfies all three factors: it's fully open source (AGPLv3), integrates as a single stateless container with no dependency on the rest of the stack, and runs entirely offline/local by default, with no schema data sent anywhere outside the machine.

Between ChartDB's official Docker image and a community fork that adds on-disk diagram persistence, the official image was chosen. The fork has low adoption (single maintainer, low download count), and the supply-chain risk of running an unofficial image outweighs the convenience of built-in persistence.

### Implementation Details

1. Add `CHARTDB_HOST_PORT` and `CHARTDB_INTERNAL_PORT` to `.env`.
2. Add a new `infra/docker/docker-compose.dev.yml` file with a single `chartdb` service, using the official `ghcr.io/chartdb/chartdb` image, with `DISABLE_ANALYTICS=true`.
3. Merge it with the main compose file via `pnpm dev:infra`, which runs `docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml --project-directory .`, so both stacks share the same `.env` and are managed with a single command.
4. Since the official image doesn't persist diagrams to disk, schema snapshots (JSON export + SQL DDL export) are versioned manually in `docs/db/`, numbered independently of the development phase roadmap (see `docs/db/README.md`).

## Consequences

ChartDB is a development-only dependency; it is never deployed to production or exposed outside `localhost`. Diagram state lives in the browser until manually exported, so losing browser storage before exporting means losing unsaved diagram work. Schema history lives in `docs/db/`, decoupled from ChartDB itself, so the project isn't locked into this specific tool going forward.

---

Created by [armandx06](https://github.com/armandx06) on August 30, 2026
