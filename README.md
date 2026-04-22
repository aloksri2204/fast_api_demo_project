# FastAPI Demo Project

A small full-stack demo app with:

- `FastAPI` for the backend API
- `React` for the frontend
- `PostgreSQL` for persistence
- `Docker Compose` for containerized development

## Project Structure

```text
fast_api_demo_project/
|-- main.py
|-- models.py
|-- database_models.py
|-- database_connection.py
|-- requirements.txt
|-- docker-compose.yml
|-- Dockerfile.backend
|-- Dockerfile.frontend
`-- frontend/
```

## Run With Docker

### Prerequisites

- Docker Desktop
- Docker Compose

### Start containers

```bash
docker compose up -d --build
```

### Open the app

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### Stop containers

```bash
docker compose down
```

### Stop containers and remove database data

Use this only when you want a fresh PostgreSQL volume.

```bash
docker compose down -v
```

## Run As A Standalone Local Utility

This mode runs the services without Docker.

### Prerequisites

- Python 3.13+
- Node.js 22+
- PostgreSQL 16+

### 1. Create the database

Create a PostgreSQL database named `fastapi_db` and ensure this user exists:

- User: `user`
- Password: `password`

### 2. Start the backend

From the project root:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`.

If your local PostgreSQL credentials are different, set `DATABASE_URL` before starting:

```powershell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/fastapi_db"
uvicorn main:app --reload
```

### 3. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm start
```

The frontend will run on `http://localhost:3000`.

## Environment Variables

### Backend

- `DATABASE_URL`: SQLAlchemy connection string
- `ALLOWED_ORIGINS`: Comma-separated CORS origins

### Frontend

- `REACT_APP_API_URL`: API base URL used by the React app

## Common Commands

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

## Notes

- The backend seeds demo products only when the `product` table is empty.
- The frontend rewrites Docker-only hostnames such as `backend` to the browser host automatically.
- The current Compose setup uses the existing PostgreSQL role `user` with password `password`.
