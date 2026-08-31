# SWEETBOARD

---

## How to run the development environment

1. Clone the repository
2. Navigate to the project directory
3. Create a `.env` file based on [.env.example](./.env.example)
4. Run `pnpm dev:infra` to start the PostgreSQL, FastAPI, and ChartDB services
5. Run `pnpm --filter web dev` to start the web application, or `pnpm --filter landing dev` to start the landing application

---

## Infra scripts

All commands below merge `infra/docker/docker-compose.yml` (main stack) with `infra/docker/docker-compose.dev.yml` (development-only tooling, currently ChartDB), using the same file flags and `--project-directory .` so they all read the same `.env`.

| Command                | Description                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `pnpm dev:infra`       | Start all services in the background                                                                              |
| `pnpm dev:infra:down`  | Stop and remove containers, keeping named volumes (database data is preserved)                                    |
| `pnpm dev:infra:reset` | Same as above, plus removes volumes (`-v`) — wipes the database completely                                        |
| `pnpm dev:infra:logs`  | Follow logs for all services. Pass a service name to filter, e.g. `pnpm dev:infra:logs -- sweetboard-chartdb-dev` |
| `pnpm dev:infra:ps`    | List running containers and their status                                                                          |

### ChartDB (ER modeling)

Available at `http://localhost:8080` once the environment is running (see [ADR 0004](./docs/adr/0004-chartdb-for-er-modeling.md)). Development-only tool — not part of the production stack. Diagrams are stored in the browser's local storage and are not persisted by the container; export schema snapshots to `docs/db/` after meaningful changes.

---

Made by [armandx06](https://github.com/armandx06) at August 30, 2026
