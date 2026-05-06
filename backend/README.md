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
- `GET /api/audio/{filename}`

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

Audio pipeline:

`upload -> Whisper transcription (whisper-1) -> GPT response (gpt-4o-mini) -> TTS (gpt-4o-mini-tts)`

Get job status:

```bash
curl http://localhost:8000/api/jobs/<JOB_ID>
```

Example done result:

```json
{
  "job_id": "d43f9fcb-5d44-47a5-b77f-8b94b6f2de21",
  "status": "done",
  "result": {
    "original_filename": "audio.wav",
    "stored_file_path": "C:\\...\\backend\\storage\\audio_uploads\\d43f9fcb-5d44-47a5-b77f-8b94b6f2de21.wav",
    "transcript": "I need help with my order status.",
    "assistant_response": "Sure, I can help. Please share your order number so I can check the status.",
    "assistant_audio_url": "/api/audio/8f7f0ad8-9e57-49da-99f2-cd08a8b72f93.mp3"
  }
}
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
4. Confirm `result.transcript` and `result.assistant_response` are both returned.
