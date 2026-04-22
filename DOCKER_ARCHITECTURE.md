# Docker Architecture

This project runs as three services inside one Docker Compose network.

## Services

- `frontend`: React UI served on `localhost:3000`
- `backend`: FastAPI API served on `localhost:8000`
- `postgres`: PostgreSQL database served on `localhost:5432`

## Architecture Diagram

```text
                      Browser
                         |
                         v
                http://localhost:3000
                         |
                         v
                 +------------------+
                 |    frontend      |
                 |   React / serve  |
                 +------------------+
                         |
                         | HTTP API calls
                         v
                 +------------------+
                 |     backend      |
                 | FastAPI / Uvicorn|
                 +------------------+
                         |
                         | SQLAlchemy
                         v
                 +------------------+
                 |     postgres     |
                 |   PostgreSQL 16  |
                 +------------------+
```

## Networking

- All services join the shared `app-network` bridge network.
- Inside Docker, the backend is reachable as `http://backend:8000`.
- Inside Docker, the database is reachable as `postgres:5432`.
- From your machine, use `localhost` with the published ports.

## Volumes

- The backend mounts the project root into `/app` for live reload.
- The frontend mounts `frontend/src` and `frontend/public` for live changes.
- PostgreSQL stores data in the named volume `postgres_data`.

## Startup Flow

1. `postgres` starts first.
2. Docker waits until the database healthcheck passes.
3. `backend` starts and connects using `DATABASE_URL`.
4. `frontend` starts and calls the backend through the published host port.

## Key Files

- [docker-compose.yml](/e:/fast_api_demo_project/docker-compose.yml:1)
- [Dockerfile.backend](/e:/fast_api_demo_project/Dockerfile.backend:1)
- [Dockerfile.frontend](/e:/fast_api_demo_project/Dockerfile.frontend:1)
- [main.py](/e:/fast_api_demo_project/main.py:1)
