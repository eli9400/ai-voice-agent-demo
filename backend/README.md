# Backend (FastAPI)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Create `backend/.env` and set:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run Redis

```bash
docker compose up -d redis
```

## Run Backend

```bash
uvicorn app.main:app --reload --port 8000
```

## Run Worker

```bash
celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo
```

## Endpoints

- `GET /health`
- `POST /api/sessions`
- `POST /api/sessions/{session_id}/messages`
- `GET /api/sessions/{session_id}`
- `POST /api/jobs`
- `POST /api/jobs/audio`
- `GET /api/jobs/{job_id}`

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

Create job:

```bash
curl -X POST http://localhost:8000/api/jobs -H "Content-Type: application/json" -d "{\"content\":\"hello\"}"
```

Upload audio job (CMD example):

```bash
curl -X POST "http://localhost:8000/api/jobs/audio" -F "file=@C:\path\to\audio.wav"
```

Get job status:

```bash
curl http://localhost:8000/api/jobs/<JOB_ID>
```

## Notes

- Session storage is in-memory only (Python dictionary).
- Restarting the backend clears all sessions.
- Jobs are processed asynchronously by Celery.
- Redis is used as both broker and result backend.
- Audio transcription uses OpenAI Whisper (`whisper-1`).
- Do not commit real API keys to source control.

## Real Transcription Check

1. Upload audio with `POST /api/jobs/audio`.
2. Copy the returned `job_id`.
3. Poll `GET /api/jobs/{job_id}` until `status` is `done`.
4. Confirm `result.transcript` contains the real transcription text.
