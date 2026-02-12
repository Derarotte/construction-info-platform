# Backend (FastAPI + SQLAlchemy + Alembic)

## 1. Install

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure

```bash
copy .env.example .env
```

Set `DATABASE_URL` in `.env` if needed.

## 3. Run migration

```bash
alembic upgrade head
```

## 4. Start API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Quick check

- `GET /api/health`
- `GET /api/projects`
- `GET /api/quality-issues`
- `POST /api/quality-issues`
- `POST /api/quality-issues/{issue_id}/transition`
- `GET /api/tasks?project_id=...`
- `POST /api/tasks`
- `GET /api/tasks/critical-path?project_id=...`
