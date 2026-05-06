# AI Voice Agent Demo (Full Stack Skeleton)

This repository contains a minimal full stack skeleton:

- Backend: FastAPI (`backend/`)
- Frontend: React + TypeScript + Vite (`frontend/`)

## 1. Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 2. Run Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

## 3. Open in Browser

- Frontend app: `http://localhost:5173`
- Backend health endpoint: `http://localhost:8000/health`

From the frontend page, click **Check Backend Health** to verify communication with the backend.
