import time

from app.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.process_mock_ai_message")
def process_mock_ai_message(content: str) -> dict[str, str]:
    time.sleep(3)
    return {
        "input": content,
        "assistant_message": f"Async mock AI response: {content}",
    }


@celery_app.task(name="app.workers.tasks.process_mock_audio_transcription")
def process_mock_audio_transcription(
    file_path: str,
    original_filename: str,
) -> dict[str, str]:
    time.sleep(3)
    return {
        "original_filename": original_filename,
        "stored_file_path": file_path,
        "transcript": f"Mock transcript for audio file: {original_filename}",
    }
