# SWEETBOARD

---

## How to run the development environment

1. Clone the repository
2. Navigate to the project directory
3. Create a `.env` file based on [.env.example](./.env.example)
4. Run `docker compose -f infra/docker/docker-compose.yml --project-directory . up -d` to run the postgresql service and the fastapi service
5. Run `pnpm --filter web dev` to start the web application, or `pnpm --filter landing dev` to start the landing application

---

Made by [armandx06](https://github.com/armandx06) at August 05, 2026
