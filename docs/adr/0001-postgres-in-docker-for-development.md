# ADR 0001: Using PostgreSQL in Docker for the Development Environment

- **Status:** Accepted
- **Date:** 2026-07-26
- **Decider:** Jorge Armando Ceras Cárdenas - [armandx06](https://github.com/armandx06)

## Context

The sweetboard project requires a relational database to manage the operational administration of [Repostería Cárdenas](https://www.reposteriacardenas.com).

The goal is to create a reproducible development environment without relying on native installations on the developer’s machine.

## Decision

The official postgres:18-alpine image is used, run via Docker Compose, with data persistence via a named volume `sweetboard_pgdata`.

## Consequences

- Any contributor can spin up the environment with a single command: `docker compose -f infra/docker/docker-compose.yml --project-directory . up -d`
- Data persists across container restarts thanks to the volume.
- Docker must be installed as the only external dependency.
- The host port and credentials are managed via environment variables (.env), never hardcoded in the Compose file, see the [.env.example](../../.env.example) file for an example.

---

Made by [armandx06](https://github.com/armandx06) at July 26, 2026
