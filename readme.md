<div align="center">

# <img width="675" height="207" alt="image" src="https://github.com/user-attachments/assets/bca93fcd-38d8-4e46-86d1-81da865386cc" />


**A browser-based, no-code data workspace**

Upload a CSV / XLSX / JSON dataset, clean it column-by-column or all at once, explore it through interactive charts, and (soon) run lightweight ML workflows — all without leaving the browser.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-8-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tailwind](https://img.shields.io/badge/Tailwind-CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Cloud-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)

</div>

---

## 🖼️ Preview

<div align="center">

**Landing Page**

<img width="900" alt="DataLab landing page" src="https://github.com/user-attachments/assets/bc261359-60cc-4372-b5fa-dcc33e31e676" />

<br/><br/>

**Dashboard**

<img width="900" alt="DataLab dashboard" src="https://github.com/user-attachments/assets/0ba09c1b-7199-412b-8429-5ddc596ce0fe" />

</div>

---

## 🧰 Tech Stack

<div align="center">

| Layer | Technology | Badge |
|---|---|---|
| 🌐 Web framework | FastAPI 0.138 + Uvicorn 0.30 | ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/-Uvicorn-2A2A2A?style=flat-square&logo=gunicorn&logoColor=white) |
| 📄 Templates | Jinja2 3.1 (server-rendered HTML) | ![Jinja](https://img.shields.io/badge/-Jinja2-B41717?style=flat-square&logo=jinja&logoColor=white) |
| 🗄️ ORM | SQLAlchemy 2.0 (async) | ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) |
| 🔌 DB driver | asyncpg (PostgreSQL) | ![Postgres](https://img.shields.io/badge/-asyncpg-4169E1?style=flat-square&logo=postgresql&logoColor=white) |
| 🔁 Migrations | Alembic | ![Alembic](https://img.shields.io/badge/-Alembic-6BA81E?style=flat-square&logo=alembic&logoColor=white) |
| ⚡ Caching | Redis 8 (`redis-py`) + `cachetools` TTLCache (RAM) | ![Redis](https://img.shields.io/badge/-Redis-DC382D?style=flat-square&logo=redis&logoColor=white) |
| 🧮 Data engine | pandas 3, NumPy 2, openpyxl | ![Pandas](https://img.shields.io/badge/-pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white) |
| 🔐 Auth | PyJWT + passlib (bcrypt) | ![JWT](https://img.shields.io/badge/-JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white) |
| 📧 Email | fastapi-mail + aiosmtplib | ![Email](https://img.shields.io/badge/-fastapi--mail-EA4335?style=flat-square&logo=gmail&logoColor=white) |
| ☁️ Cloud Storage | Supabase Storage (production) | ![Supabase](https://img.shields.io/badge/-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white) |
| ☁️ S3 support (alt) | boto3 | ![AWS](https://img.shields.io/badge/-boto3%20S3-232F3E?style=flat-square&logo=amazons3&logoColor=white) |
| ✅ Validation | Pydantic v2 + pydantic-settings | ![Pydantic](https://img.shields.io/badge/-Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) |
| 🚦 Rate Limiting | slowapi (SlowAPI middleware) | ![SlowAPI](https://img.shields.io/badge/-SlowAPI-FF4136?style=flat-square) |
| 🐳 Containerisation | Docker + Docker Compose (Postgres 18 + Redis 7 + web) | ![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white) |
| 🎨 Frontend | Tailwind CSS (CDN) · Space Grotesk / Inter / IBM Plex Mono · custom themes | ![Tailwind](https://img.shields.io/badge/-Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white) |

</div>

---

## 📁 Project Structure

```
DataLab/
├── main.py                          # Uvicorn entrypoint (sets sys.path, runs reload)
├── requirements.txt
├── alembic.ini
├── alembic/versions/                # DB migration scripts
├── dockerfile
├── docker-compose.yml
├── .env example                     # Template — copy to .env and fill in values
│
├── backend/
│   ├── __init__.py
│   └── app/
│       ├── app.py                   # FastAPI instance, router mounting, exception handlers, page routes
│       ├── core/
│       │   ├── config.py            # AppConfig + NotificationConfig (pydantic-settings, lru_cache)
│       │   ├── mail.py              # NotificationService (email sending via fastapi-mail)
│       │   └── supabase.py          # Supabase client initialisation
│       ├── database/
│       │   ├── base.py              # SQLAlchemy declarative Base
│       │   ├── session.py           # Async engine + get_db dependency
│       │   └── redis.py             # Redis helpers: mail_send / is_mail_send / mail_work_done
│       ├── models/
│       │   └── models.py            # User, Dataset ORM models; FileType enum
│       ├── schemas/
│       │   ├── auth.py              # UserCreate, UserLogin, ResetPasswordRequest, UserPasswordReset
│       │   ├── dataset.py           # Dataset, DatasetResponse, DatasetVisualized, ColumnWiseClean, overallclean, renameColumn
│       │   └── token.py             # TokenData schema
│       ├── repository/
│       │   ├── user.py              # register, login, update_verify_email, update_password, get_user
│       │   └── dataset.py           # DatasetRepository: add_dataset, get_user_datasets, delete_dataset
│       ├── service/
│       │   ├── authRepo.py          # for_Auth service: login_user, create_user, password_reset
│       │   ├── data_engine.py       # pandas engine: preview, columns, visualize, clean, rename
│       │   ├── base.py              # BaseRepository (injects db + background tasks)
│       │   ├── dataset_route_handler.py  # (WIP) Dataset route handling helpers
│       │   └── ml_engine.py         # (WIP) ML engine placeholder
│       ├── router/
│       │   ├── auth.py              # /auth/* API endpoints
│       │   ├── dataset.py           # /datasets/* API endpoints
│       │   ├── analytics.py         # (WIP) Analytics routes
│       │   ├── process.py           # (WIP) Processing routes
│       │   └── deps.py              # get_current_user, get_verified_user_dataset, APP_DIR
│       ├── security/
│       │   ├── jwt_handler.py       # create_access_token, verify_token, set_auth_cookies
│       │   └── auth_handler.py      # bcrypt password hashing
│       ├── middleware/
│       │   └── rate_limiting.py     # slowapi Limiter setup
│       ├── cache/
│       │   └── cache.py             # DatasetCacheService: TTLCache RAM + Supabase/disk cache
│       ├── exceptions_handler/
│       │   ├── handle_expection.py  # Custom exception hierarchy (DataLabExceptionHandler + subclasses)
│       │   └── errors/              # HTML error templates (404.html, 429.html, 500.html)
│       ├── utils/
│       │   ├── email_verification.py
│       │   └── password_reset.py
│       ├── storage/                 # Local file storage root (dev only, auto-created)
│       └── templates/emails/        # Jinja2 email templates
│
└── frontend/
    ├── templates/                   # Page templates (base, landing, dashboard, upload, clean, visualize, ml, auth pages)
    └── static/
        ├── css/                     # style.css + datalab-ledger-theme.css
        └── js/
```

---

## 🔌 API Endpoints

### 🔐 Authentication — `/auth`

| Method | Path | Auth required | Rate Limit | Description |
|---|---|:---:|:---:|---|
| `POST` | `/auth/login` | — | 5/min | Credential login; sets `access_token` HTTP-only cookie |
| `POST` | `/auth/register` | — | 5/min | Create account; triggers verification email |
| `GET` | `/auth/me` | ✅ | 60/min | Returns current user's username + email |
| `POST` | `/auth/logout` | ✅ | 60/min | Records `logged_out_at`, clears cookie |
| `GET` | `/auth/verify-email?token=` | — | — | Marks account verified via signed token |
| `POST` | `/auth/password-reset` | — | 3/hr | Sends password-reset magic link to email |
| `POST` | `/auth/password-reset-verify?token=` | — | 3/hr | Sets new password via signed token |

### 📦 Datasets — `/datasets`

| Method | Path | Rate Limit | Description |
|---|---|:---:|---|
| `POST` | `/datasets/upload` | 10/min | Upload a CSV / XLSX / JSON file |
| `GET` | `/datasets/list` | 60/min | JSON list of the current user's datasets |
| `GET` | `/datasets/view` | — | HTML dashboard (dataset list) |
| `DELETE` | `/datasets/delete?dataset_id=` | 10/min | Delete a dataset and its file |
| `GET` | `/datasets/preview?dataset_id=` | — | 10-row preview + `describe()` + null/dtype table |
| `GET` | `/datasets/columns?dataset_id=` | — | Column names, dtypes, null counts for full file |
| `POST` | `/datasets/visualize?dataset_id=` | — | Chart data (bar / line / pie / hist / scatter) |
| `POST` | `/datasets/column-clean?dataset_id=` | 20/min | Column-level clean (drop-na / fill-na) |
| `POST` | `/datasets/overall-clean?dataset_id=` | 20/min | Dataset-wide clean (drop rows or cols / fill all nulls) |
| `POST` | `/datasets/rename-column?dataset_id=` | 20/min | Rename a column |
| `GET` | `/datasets/download?dataset_id=` | — | Streaming file download |

> ℹ️ All dataset endpoints require a valid `access_token` cookie. The `dataset_id` query parameter is a UUID that identifies the dataset and must belong to the requesting user.

### 🗺️ Page Routes (HTML)

| Path | Page |
|---|---|
| `/` | Landing page (guests) or redirect to `/datasets/view` (logged-in) |
| `/landing` | Public marketing page |
| `/login` | Login form |
| `/register` | Registration form |
| `/upload` | Upload page *(auth required)* |
| `/preview` | Preview page |
| `/clean` | Data cleaning page *(auth required)* |
| `/visualize` | Visualization builder *(auth required)* |
| `/ml` | ML workflow page *(auth required)* |
| `/change-password` | Password reset form |
| `/email-verify` | Enter email to re-send verification |
| `/mail-verification?token=` | Email verification landing page |

---

## 🚀 Quick Start (Local Development)

### ✅ Prerequisites

- 🐍 Python 3.11+
- 🐘 PostgreSQL (running locally or via Docker)
- ⚡ Redis (running locally or via Docker)

### 1️⃣ Clone and Create a Virtual Environment

```bash
git clone <repo-url>
cd DataLab

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables

```bash
# Windows
copy ".env example" .env
# macOS / Linux
cp ".env example" .env
```

Edit `.env` with your values — see [Environment Variables](#️-environment-variables) below.

### 4️⃣ Apply Database Migrations

```bash
alembic upgrade head
```

### 5️⃣ Start the Dev Server

```bash
python main.py
```

Open **`http://127.0.0.1:8000`** in your browser. The server runs with `--reload` enabled.

> 📚 FastAPI's auto-generated API docs are available at `http://127.0.0.1:8000/docs`.

---

## 🐳 Docker (All-in-One)

Docker Compose starts **PostgreSQL 18**, **Redis 7**, and the **DataLab web** container together.

```bash
docker-compose up --build
```

The compose file automatically:
1. ⏳ Waits for Postgres to pass its health check
2. 🔁 Runs `alembic upgrade head`
3. 🚀 Starts Uvicorn on port `8000`

PostgreSQL data is persisted in the `postgres_data` named volume between restarts.

```bash
# Stop and remove containers (data volume is preserved)
docker-compose down
```

---

## ⚙️ Environment Variables

Validated at startup via **pydantic-settings** (`backend/app/core/config.py`). Copy `.env example` to `.env` and fill in all values.

### 🏷️ Application

| Variable | Example | Description |
|---|---|---|
| `APP_NAME` | `DATALAB` | Application display name |
| `ENV` | `DEVELOPMENT` | `DEVELOPMENT` or `PRODUCTION` |
| `base_url` | `http://localhost:8000` | Public base URL (used in email magic links) |
| `SECRET_KEY` | `change-me` | Secret for signing JWT tokens |
| `ALGORITHMS` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTE` | `60` | Access token lifetime in minutes |

### 🗄️ Database

| Variable | Example | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:pass@localhost:5432/DataLab` | Async PostgreSQL DSN |

### ⚡ Caching

| Variable | Example | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `REDIS_PORT` | `6379` | Redis port |

### 📧 Email (SMTP / Gmail)

| Variable | Example | Description |
|---|---|---|
| `MAIL_USERNAME` | `you@gmail.com` | SMTP username |
| `MAIL_PASSWORD` | `app-password` | SMTP password or Gmail App Password |
| `MAIL_FROM` | `you@gmail.com` | Sender address |
| `MAIL_FROM_NAME` | `DataLab` | Sender display name |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP host |
| `MAIL_PORT` | `587` | SMTP port (587 for STARTTLS) |

### ☁️ Supabase (Production Storage)

| Variable | Example | Description |
|---|---|---|
| `SUPABASE_URL` | `https://xyz.supabase.co` | Supabase project URL |
| `SUPABASE_KEY` | `eyJ...` | Supabase anon/service key |
| `SUPABASE_BUCKET` | `datasets` | Supabase Storage bucket name |

---

## 🗃️ Database Models

### 👤 `User` — table `users`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | Auto-generated |
| `username` | String(20) | Unique |
| `email` | Text | Unique |
| `password` | Text | bcrypt hash |
| `is_verified` | Boolean | Email verified flag |
| `is_active` | Boolean | Account active flag |
| `storage_used_bytes` | Integer | Running total of uploaded file sizes |
| `storage_limit_bytes` | Integer | Default ~15 MB (15,728,640 bytes) |
| `logged_out_at` | DateTime (nullable) | Used to invalidate tokens issued before logout |
| `created_at` | DateTime | Server default (`now()`) |

### 📊 `Dataset` — table `datasets`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | Auto-generated |
| `owner_id` | UUID (FK → users) | Cascade delete |
| `original_name` | String(255) | Original filename |
| `file_path` | String(512) | Local path (dev) or Supabase key (prod) |
| `file_type` | Enum | `csv`, `json`, or `xlsx` |
| `file_size_bytes` | Integer | Size recorded at upload; updated on clean |
| `last_accessed_at` | DateTime | Updated on access |
| `created_at` | DateTime | Server default (`now()`) |

---

## 🧠 Data Engine

The pandas engine (`backend/app/service/data_engine.py`) is executed via `run_in_threadpool` so it never blocks the async event loop. All read operations go through `DatasetCacheService` which maintains a **TTLCache (RAM, 20 entries, 15 min TTL)** backed by local disk (dev) or Supabase Storage (prod).

| Function | Description |
|---|---|
| `data_engine_preview` | Reads up to 10 rows; returns preview rows, `describe()` summary, and null/dtype table |
| `data_engine_columns` | Returns column names, dtypes, and per-column null counts for the full file |
| `data_engine_visual` | Aggregates data for bar / line / pie / histogram (single-series or multi-series crosstab) and scatter charts |
| `column_wise_clean` | Applies `drop-na` or `fill-na` (mean, mode, or custom value) to a single named column; writes back and updates cache |
| `overall_clean` | Applies `drop-na` (axis=0 rows or axis=1 columns) or `fill-na` with a custom value across all columns |
| `rename_column` | Renames one column and writes back atomically |
| `update_dataset` | Shared writer: writes to local file (dev) or Supabase Storage (prod), then updates RAM cache |

**📁 Supported file types:** CSV · XLSX · JSON

---

## 🔐 Authentication Flow

```
Register → verification email (signed token link)
              ↓
         GET /auth/verify-email?token=  →  is_verified = True
              ↓
         POST /auth/login  →  HTTP-only Secure cookie (access_token)
              ↓
         Protected routes read cookie → JWT verified + logged_out_at check
              ↓
         POST /auth/logout  →  logged_out_at recorded, cookie cleared
                               (tokens issued before this timestamp are rejected)
```

Password reset follows the same signed-token pattern via `/auth/password-reset` → email → `/auth/password-reset-verify?token=`.

---

## 🛡️ Exception Handling

All custom exceptions inherit from `DataLabExceptionHandler(Exception)` and carry a `detail` message + `status_code`. The hierarchy:

| Exception | Status | Trigger |
|---|---|---|
| `ClientNotAuthorized` | 401 | Missing or invalid auth cookie |
| `InvalidCredentials` | 401 | Wrong username / password |
| `TokenInvalid` | 401 | Bad or expired signed token |
| `TokenExpired` | 401 | JWT past its expiry |
| `AccessDenied` | 403 | User doesn't own the resource |
| `StorageLimitExceeded` | 403 | Upload would exceed quota |
| `DatasetNotFound` | 404 | Dataset UUID not found |
| `UserNotFound` | 404 | User lookup failed |
| `ValidationError` | 422 | Bad request payload |
| `DataProcessingError` | 500 | Pandas engine fault |

`app.py` registers handlers for `RateLimitExceeded`, `StarletteHTTPException`, `DataLabExceptionHandler`, and bare `Exception` — returning either JSON or a styled HTML error page (`404.html`, `429.html`, `500.html`) depending on the `Accept` header.

---

## 📝 Development Notes

- 💾 **Local storage** is created automatically at `backend/app/storage/` when `ENV=DEVELOPMENT`.
- ☁️ **Production storage** — set `ENV=PRODUCTION`; files are uploaded to / read from Supabase Storage. boto3 is also included for S3-compatible storage alternatives.
- 🚦 **Rate limiting** — `slowapi` is active via `SlowAPIMiddleware`. Decorator limits are applied on auth (5/min login, 3/hr reset) and dataset mutation endpoints (10–20/min).
- 🔁 **Alembic** — generate a new migration after changing any SQLAlchemy model:

  ```bash
  alembic revision --autogenerate -m "describe your change"
  alembic upgrade head
  ```

- 📚 **API docs** — available at `/docs` (Swagger UI) and `/redoc` when the server is running.
- 🗂️ **Cache strategy** — `DatasetCacheService` uses a two-tier cache: in-memory `TTLCache` (900s, 20 slots) for hot datasets, and local disk cache for production Supabase downloads. `update_cache()` is called after every mutating operation to keep the cache consistent.

---

## 🗺️ Roadmap

### ✅ Completed
- [x] User registration, email verification, login / logout
- [x] Cookie-based JWT auth with `logged_out_at` token invalidation
- [x] Password reset via signed magic link email
- [x] Dataset upload (CSV, XLSX, JSON) with per-user storage quota
- [x] Dataset list, delete, and streaming download
- [x] Data preview (10-row table + `describe()` + null/dtype info)
- [x] Column-wise cleaning — drop nulls, fill with mean / mode / custom value
- [x] Dataset-wide cleaning — drop rows or columns, fill all nulls
- [x] Column rename
- [x] Interactive chart builder — bar, line, pie, histogram, scatter
- [x] Transactional email (verification + password reset) via fastapi-mail
- [x] Docker Compose setup (Postgres 18 + Redis 7 + web)
- [x] Alembic migrations
- [x] Rate limiting — slowapi decorators active on auth and dataset endpoints
- [x] Exception Handling — custom exception hierarchy with clean HTTP responses
- [x] Exception Handling UI — styled HTML error pages (404, 429, 500)
- [x] Cloud storage — Supabase Storage integration for production (`ENV=PRODUCTION`)
- [x] Two-tier caching — TTLCache RAM cache + Supabase-backed disk cache

### 🔜 Upcoming
- [ ] 🤖 **ML features** — train and evaluate models (classification / regression) directly on uploaded datasets
- [ ] 🔢 **Column encoding** — one-hot, label encoding, ordinal mapping for categorical columns
- [ ] 🚀 **Full deployment** — CI/CD pipeline, production Docker image, hosting (Railway / Render / EC2)

---

## 📄 License

See the [`LICENSE`](LICENSE) file in the repository root for terms.
