from typing import Any

from app.celery_app import celery_app
from app.workers.tasks import (
    process_mock_ai_message,
    process_mock_audio_transcription,
)


def create_job(content: str) -> str:
    task = process_mock_ai_message.delay(content)
    return task.id


def create_audio_job(file_path: str, original_filename: str) -> str:
    task = process_mock_audio_transcription.delay(file_path, original_filename)
    return task.id


def get_job_status(job_id: str) -> tuple[str, dict[str, Any] | None]:
    task_result = celery_app.AsyncResult(job_id)
    state = task_result.state

    if state == "PENDING":
        return "queued", None
    if state in {"RECEIVED", "STARTED", "RETRY"}:
        return "processing", None
    if state == "SUCCESS":
        result = task_result.result
        if isinstance(result, dict):
            return "done", result
        return "done", {"value": result}
    if state in {"FAILURE", "REVOKED"}:
        return "failed", None

    return "processing", None
