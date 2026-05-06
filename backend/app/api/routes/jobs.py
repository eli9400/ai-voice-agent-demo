from fastapi import APIRouter

from app.schemas.jobs import CreateJobRequest, CreateJobResponse, JobStatusResponse
from app.services.job_service import create_job, get_job_status

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=CreateJobResponse, status_code=201)
def create_job_endpoint(payload: CreateJobRequest) -> CreateJobResponse:
    job_id = create_job(payload.content)
    return CreateJobResponse(job_id=job_id, status="queued")


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status_endpoint(job_id: str) -> JobStatusResponse:
    status, result = get_job_status(job_id)
    return JobStatusResponse(job_id=job_id, status=status, result=result)
