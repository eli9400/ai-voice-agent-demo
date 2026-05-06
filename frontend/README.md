# Frontend (React + TypeScript + Vite)

## Install

```bash
npm install
```

## Run

```bash
npm run dev
```

## App URL

Open:

`http://localhost:5173`

## What This UI Does

- Ask for microphone permission in the browser.
- Record voice audio from the microphone.
- Upload recorded audio to:
  `POST http://localhost:8000/api/jobs/audio`
- Receive `job_id`.
- Poll every 2 seconds:
  `GET http://localhost:8000/api/jobs/{job_id}`
- Show live status (`queued` / `processing` / `done` / `failed`).
- Display:
  - transcript
  - assistant response
  - automatic TTS playback from `assistant_audio_url`
  - errors (if any)

## How To Test

1. Start backend + Redis + Celery worker (`--pool=solo`) from the backend project.
2. Run this frontend with `npm run dev`.
3. Open `http://localhost:5173`.
4. Allow microphone access when the browser asks.
5. Click **Start Recording**, speak, then click **Stop Recording**.
6. Wait for status to reach `done`.
7. Verify transcript and assistant response are shown and AI audio plays automatically.
