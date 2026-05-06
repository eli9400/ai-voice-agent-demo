from typing import Any

from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    content: str = Field(min_length=1)


class CreateJobResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict[str, Any] | None = None
