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

- Select an audio file.
- Upload it to:
  `POST http://localhost:8000/api/jobs/audio`
- Receive `job_id`.
- Poll every 2 seconds:
  `GET http://localhost:8000/api/jobs/{job_id}`
- Show live status (`queued` / `processing` / `done` / `failed`).
- Display:
  - transcript
  - assistant response
  - errors (if any)

## How To Test

1. Start backend + Redis + Celery worker (`--pool=solo`) from the backend project.
2. Run this frontend with `npm run dev`.
3. Open `http://localhost:5173`.
4. Choose an audio file (`.mp3`, `.wav`, `.m4a`, `.webm`, `.ogg`).
5. Click **Upload Audio**.
6. Wait for status to reach `done`, then verify transcript and assistant response are shown.
