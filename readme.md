DataLab

DataLab is a web application for uploading, cleaning, exploring, visualizing, and running lightweight ML workflows on tabular datasets. It provides user authentication, file storage, dataset previewing, a simple ML interface, and a Jinja2-driven frontend served by a FastAPI backend.

**Tech stack**
- **Backend:** FastAPI, Uvicorn
- **ORM / DB:** SQLAlchemy, asyncpg (Postgres compatible)
- **Caching / Queues:** Redis
- **Frontend:** Jinja2 templates + static JS/CSS
- **Other:** Alembic for migrations, S3-compatible storage helpers, email via fastapi-mail

**Key files**
- `main.py`: application entrypoint (starts Uvicorn).
- `backend/app/app.py`: FastAPI app and route registration.
- `requirements.txt`: pinned Python dependencies.

**Features**
- User registration, login, and email verification
- Dataset upload and secure storage
- Data cleaning and preview pages
- Visualization and lightweight ML workflow pages
- Email notifications and password reset flows

**Quick start (development)**

Prerequisites
- Python 3.11+ (virtualenv recommended)
- PostgreSQL (or other DB pointed by `DATABASE_URL`)
- Redis (for rate-limiting / caching)
- Optional: Docker & Docker Compose

Local setup

1. Create and activate a virtual environment:

	```bash
	python -m venv .venv
	.venv\Scripts\activate
	```

2. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

3. Create a `.env` file in the project root and set the required environment variables (see below).

4. Run database migrations (Alembic):

	```bash
	alembic upgrade head
	```

5. Start the app (development reload enabled):

	```bash
	python main.py
	```

The app will be available at `http://127.0.0.1:8000` by default.

**Environment variables**

The application loads settings from `.env` via Pydantic. The important variables the code expects include:

- `app_name` — application name
- `base_url` — public base URL
- `ENV` — environment name (e.g., DEVELOPMENT, PRODUCTION)
- `DATABASE_URL` — database DSN (Postgres example: `postgresql+asyncpg://user:pass@host/db`)
- `secret_key` — secret used for signing tokens
- `algorithms` — JWT algorithm (e.g. HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTE` — token expiry in minutes
- `REDIS_URL` / `redis_port` — Redis connection info

Notification / email config (for transactional emails):
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_FROM_NAME`, `MAIL_SERVER`, `MAIL_PORT`

These variables are defined and validated in `backend/app/core/config.py`.

**Docker / Production**

There's a `docker-compose.yml` in the project root. Typical production flow:

- Provide secrets and environment variables via a `.env` or Docker secrets
- Build and run containers:

```bash
docker-compose up --build
```

Adjust service definitions in `docker-compose.yml` to connect to managed Postgres/Redis or S3 storage as needed.

**Database migrations**

Alembic is configured in the repo — migration scripts are under `alembic/versions`. Use `alembic` to generate and apply schema changes.

**Running tests**

Run unit and integration tests with `pytest`:

```bash
pytest
```

**Development notes & structure**

- Template files: `frontend/templates`
- Static assets: `frontend/static`
- App package: `backend/app`
- Storage folder (local dev): `backend/app/storage`

If you need to upload example datasets for local development, place them under `backend/app/storage/` or use the app UI to upload.

**Contributing**

Please open issues or pull requests for bugfixes and features. When contributing:

- Keep changes small and focused
- Add tests for new behavior
- Update or add Alembic migrations if DB models change

**License**

This project includes a `LICENSE` file in the repository root — consult it for license terms.

---

If you'd like, I can:
- add a quick `Makefile` or `nox` session for common tasks
- add a sample `.env.example` with the minimal required variables
- generate a short CONTRIBUTING.md with testing and commit guidance

Wrote this README to [readme.md](readme.md)
