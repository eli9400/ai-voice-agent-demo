from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.jobs import (
    AudioJobResponse,
    CreateJobRequest,
    CreateJobResponse,
    JobStatusResponse,
)
from app.services.job_service import create_audio_job, create_job, get_job_status

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".webm", ".ogg"}
AUDIO_UPLOAD_DIR = Path(__file__).resolve().parents[3] / "storage" / "audio_uploads"
AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("", response_model=CreateJobResponse, status_code=201)
def create_job_endpoint(payload: CreateJobRequest) -> CreateJobResponse:
    job_id = create_job(payload.content)
    return CreateJobResponse(job_id=job_id, status="queued")


@router.post("/audio", response_model=AudioJobResponse, status_code=201)
async def create_audio_job_endpoint(file: UploadFile = File(...)) -> AudioJobResponse:
    original_filename = file.filename or ""
    extension = Path(original_filename).suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid audio file extension. Allowed: .mp3, .wav, .m4a, .webm, .ogg",
        )

    stored_filename = f"{uuid4()}{extension}"
    stored_file_path = AUDIO_UPLOAD_DIR / stored_filename
    try:
        file_bytes = await file.read()
        stored_file_path.write_bytes(file_bytes)
    finally:
        await file.close()

    job_id = create_audio_job(
        file_path=str(stored_file_path),
        original_filename=original_filename,
    )
    return AudioJobResponse(job_id=job_id, status="queued", filename=stored_filename)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status_endpoint(job_id: str) -> JobStatusResponse:
    status, result = get_job_status(job_id)
    return JobStatusResponse(job_id=job_id, status=status, result=result)
