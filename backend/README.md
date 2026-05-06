# Backend (FastAPI)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /health`
- `POST /api/sessions`
- `POST /api/sessions/{session_id}/messages`
- `GET /api/sessions/{session_id}`

## Quick curl Examples

Health:

```bash
curl http://localhost:8000/health
```

Create session:

```bash
curl -X POST http://localhost:8000/api/sessions
```

Add message:

```bash
curl -X POST http://localhost:8000/api/sessions/<SESSION_ID>/messages -H "Content-Type: application/json" -d "{\"content\":\"hello\"}"
```

Get session:

```bash
curl http://localhost:8000/api/sessions/<SESSION_ID>
```

## Notes

- Session storage is in-memory only (Python dictionary).
- Restarting the backend clears all sessions.
