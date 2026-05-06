# AI Voice Agent Demo

## Overview
This is a full-stack AI voice agent demo that allows users to upload an audio file, transcribe it using OpenAI Whisper, generate an AI response using GPT, and display the result in a React UI.

## Architecture
```text
React Frontend
    |
    v
FastAPI Backend
    |
    v
Redis Queue
    |
    v
Celery Worker
    |
    v
OpenAI Whisper + GPT
```

## Features
- Audio file upload
- Async background processing
- Job polling
- Hebrew/English transcription support via Whisper
- GPT assistant response generation
- React + TypeScript UI
- FastAPI REST API
- Redis + Celery worker architecture
- Docker-based Redis service

## Tech Stack
Frontend:
- React
- TypeScript
- Vite

Backend:
- Python
- FastAPI
- Celery
- Redis
- OpenAI Python SDK

Infrastructure:
- Docker Compose

## Prerequisites
- Node.js
- Python 3.11+
- Docker Desktop
- OpenAI API key

## Environment Variables
Create the file:

`backend/.env`

With:

```env
OPENAI_API_KEY=your_api_key_here
```

Never commit `.env` files.

## Installation
Backend setup:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Frontend setup:

```bash
cd frontend
npm install
```

## Running the Project
Step 1 - Start Redis (from the project root):

```bash
docker compose up -d redis
```

Step 2 - Start Backend:

```bash
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Step 3 - Start Celery Worker:

```bash
cd backend
.\.venv\Scripts\activate
celery -A app.celery_app.celery_app worker --pool=solo --loglevel=info
```

On Windows, use `--pool=solo` to avoid multiprocessing issues.

Step 4 - Start Frontend:

```bash
cd frontend
npm run dev
```

Open:

`http://localhost:5173`

## Manual API Testing
Upload audio:

```bash
curl -X POST "http://localhost:8000/api/jobs/audio" -F "file=@C:\path\to\audio.mp3"
```

Check job status:

```bash
curl "http://localhost:8000/api/jobs/JOB_ID_HERE"
```

## Expected Flow
1. User uploads audio in React UI.
2. Backend stores the file.
3. Backend creates Celery job.
4. Redis queues the job.
5. Celery worker processes the audio.
6. OpenAI Whisper transcribes the audio.
7. GPT generates assistant response.
8. Frontend polls until result is ready.
9. Transcript and assistant response are displayed.

## Common Issues
- Docker command not recognized: install Docker Desktop.
- Redis not running: run `docker compose up -d redis`.
- Celery PermissionError on Windows: use `--pool=solo`.
- Uvicorn not recognized: activate `.venv` and install requirements.
- Missing OPENAI_API_KEY: create `backend/.env`.
- Audio file not found in curl: verify full file path and extension.

## Project Status
Current version supports uploaded audio files, async transcription, and GPT response generation.

Future improvements:
- TTS audio response
- WebSocket realtime updates
- Persistent PostgreSQL storage
- Authentication
- Conversation history

## License
MIT License
