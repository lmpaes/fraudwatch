# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

FraudWatch is a vehicle assistance fraud prevention dashboard. It consists of:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL (port 8000)
- **Frontend**: Single static HTML file (`frontend/fraud_dashboard.html`) that consumes the backend API directly — no build step, no framework.

## Running the App

**With Docker (recommended):**
```bash
docker compose up -d --build
```
API at `http://localhost:8000`, Swagger at `http://localhost:8000/docs`.

**Re-seed the database** (regenerates all data relative to today's date):
```bash
docker compose run --rm seed
```

**Tear down** (keep data: omit `-v`; wipe data: add `-v`):
```bash
docker compose down -v
```

**Without Docker** (Python 3.11+ and PostgreSQL 14+ required):
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env   # then set DATABASE_URL in .env
# Create DB: psql -c "CREATE DATABASE fraudwatch;"
python seed.py
uvicorn main:app --reload --port 8000
```

## Architecture

### Backend (`backend/`)

| File | Role |
|------|------|
| `main.py` | FastAPI app, CORS, router registration, `/api/dashboard/*` endpoints |
| `models.py` | SQLAlchemy ORM: `Case`, `CaseFactor`, `CaseHistory`, `Blocklist`, `BlocklistReason` |
| `schemas.py` | Pydantic v2 models for request/response validation |
| `crud.py` | All DB operations; also houses `get_kpis()` and `get_charts()` logic |
| `database.py` | SQLAlchemy engine + session factory; reads `DATABASE_URL` from env |
| `services/score.py` | Score calculation, holiday detection, initials/color generation |
| `routers/cases.py` | CRUD routes for `/api/cases` |
| `routers/blocklist.py` | CRUD routes for `/api/blocklist` |
| `routers/export.py` | CSV/JSON export routes |
| `seed.py` | Populates DB with 15 blocklist entries and 80 cases (dates relative to today) |

### Data Flow for Score Calculation

Score is computed in `services/score.py:calculate_score()` and called from `crud.create_case()` and `crud.update_case()`. The score is **stored** on the `Case` record at creation/edit time — it is never recalculated on read. Blocklist membership is checked by exact case-insensitive name match (`ilike`).

Score factors:
- **Blocklist** (0 or 45 pts): automatic, based on name lookup
- **Reincidência** (0–25 pts): manual, from operator input
- **Transporte** (0, 10, or 20 pts): automatic, derived from `transport` field
- **Data suspeita** (0 or 10 pts): automatic, if date is within ±3 days of a national holiday

### Key Design Decisions

- `CaseUpdate` uses a `_Date` alias for the `date` field to avoid shadowing `datetime.date` in Pydantic v2 — see the comment in `schemas.py:6`.
- The `seed` service in `docker-compose.yml` runs once (`restart: "no"`) and exits; re-running requires `docker compose run --rm seed`.
- Editing or deleting a blocklist entry does **not** retroactively affect existing case scores/factors — those are immutable after creation unless the case itself is edited.
- The `NATIONAL_HOLIDAYS` set is duplicated between `services/score.py` and `crud.get_charts()` — keep them in sync when updating holidays.
- The frontend is a single HTML file with no build system; all JS/CSS is inline or via CDN. Open it directly in a browser or serve statically.

## API Filter Parameter

Most endpoints accept `?filter=all|week|month`. The `week` filter is a 7-day rolling window (today − 6 days), and `month` is a 30-day rolling window (today − 29 days). This is applied in `crud._apply_filter()`.
