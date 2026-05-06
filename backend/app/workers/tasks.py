import time
from pathlib import Path

from openai import OpenAI

from app.core.settings import app_settings
from app.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.process_mock_ai_message")
def process_mock_ai_message(content: str) -> dict[str, str]:
    time.sleep(3)
    return {
        "input": content,
        "assistant_message": f"Async mock AI response: {content}",
    }


def _create_openai_client() -> OpenAI:
    if not app_settings.openai_api_key.strip():
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Set it in backend/.env before running transcription jobs."
        )
    return OpenAI(api_key=app_settings.openai_api_key)


@celery_app.task(name="app.workers.tasks.process_mock_audio_transcription")
def process_mock_audio_transcription(
    file_path: str,
    original_filename: str,
) -> dict[str, str]:
    audio_path = Path(file_path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    time.sleep(3)
    client = _create_openai_client()

    try:
        with audio_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=app_settings.whisper_model,
                file=audio_file,
            )
    except Exception as exc:
        raise RuntimeError(
            f"OpenAI transcription failed for file '{original_filename}'."
        ) from exc

    transcript_text = getattr(transcription, "text", None)
    if not transcript_text:
        raise RuntimeError("OpenAI transcription response did not include transcript text.")

    return {
        "original_filename": original_filename,
        "stored_file_path": str(audio_path),
        "transcript": transcript_text,
    }
