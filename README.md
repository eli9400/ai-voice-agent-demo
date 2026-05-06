# AI Voice Agent Demo

A full-stack voice conversation demo that records microphone input in the browser, processes it asynchronously in the backend, and plays back an AI-generated voice reply.

## Voice Conversation Flow

```text
Browser Mic Recording
    -> FastAPI Upload Endpoint
    -> Redis Queue
    -> Celery Worker (--pool=solo)
    -> OpenAI Whisper (transcript)
    -> OpenAI GPT (assistant response)
    -> OpenAI TTS (assistant audio)
    -> Frontend Polling + Auto Playback
```

## Key Features

- Browser microphone recording via MediaRecorder
- Async background job processing with Redis + Celery
- Whisper transcription (`whisper-1`)
- GPT text response generation (`gpt-4o-mini`)
- TTS audio generation (`gpt-4o-mini-tts`, `alloy`)
- Polling-based job status updates (no WebSocket yet)
- Automatic playback of AI audio response in the UI

## Tech Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, Celery, Redis, OpenAI Python SDK
- Infra: Docker Compose (Redis service)

## Prerequisites

- Node.js
- Python 3.11+
- Docker Desktop
- OpenAI API key

## Environment Variables

Create `backend/.env`:

```env
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env` files.

## Installation

Backend:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Frontend:

```bash
cd frontend
npm install
```

## Run Locally

1. Start Redis (from project root):

```bash
docker compose up -d redis
```

2. Start backend:

```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

3. Start Celery worker:

```bash
cd backend
.\.venv\Scripts\activate
celery -A app.celery_app.celery_app worker --pool=solo --loglevel=info
```

On Windows, keep `--pool=solo` to avoid multiprocessing issues.

4. Start frontend:

```bash
cd frontend
npm run dev
```

5. Open `http://localhost:5173`.

## Frontend Usage

1. Click **Start Recording**.
2. Allow microphone permissions in the browser.
3. Speak, then click **Stop Recording**.
4. Wait while status moves from `queued`/`processing` to `done`.
5. Review transcript + assistant response.
6. Listen to auto-played AI TTS response.

## Manual API Testing

Upload audio:

```bash
curl -X POST "http://localhost:8000/api/jobs/audio" -F "file=@C:\path\to\audio.mp3"
```

Check job status:

```bash
curl "http://localhost:8000/api/jobs/JOB_ID_HERE"
```

Fetch generated AI audio file:

```bash
curl "http://localhost:8000/api/audio/GENERATED_FILENAME.mp3" --output ai-response.mp3
```

## Common Issues

- `docker` command not recognized: install Docker Desktop.
- Redis not running: `docker compose up -d redis`.
- Celery issues on Windows: run worker with `--pool=solo`.
- Microphone blocked in browser: allow mic permissions for `localhost`.
- Missing `OPENAI_API_KEY`: create and fill `backend/.env`.
- `uvicorn` not recognized: activate `.venv` and install requirements.

## Current Scope

This version supports full voice conversation flow: record -> transcribe -> respond -> synthesize -> play.

Not included yet:

- WebSocket realtime streaming
- Database persistence
- Authentication

## License

MIT License
