import time
from pathlib import Path

from app.celery_app import celery_app
from app.services.ai_service import (
    generate_assistant_response,
    generate_speech_audio,
    get_transcription_metadata,
    transcribe_audio,
)


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
    audio_path = Path(file_path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    time.sleep(3)
    transcript_text = transcribe_audio(str(audio_path))

    try:
        assistant_response = generate_assistant_response(transcript_text)
    except Exception as exc:
        raise RuntimeError(
            f"Assistant response generation failed for file '{original_filename}'."
        ) from exc

    try:
        assistant_audio_path = generate_speech_audio(assistant_response)
    except Exception as exc:
        raise RuntimeError(
            f"Assistant speech generation failed for file '{original_filename}'."
        ) from exc

    assistant_audio_filename = Path(assistant_audio_path).name

    return {
        "original_filename": original_filename,
        "stored_file_path": str(audio_path),
        "transcript": transcript_text,
        **get_transcription_metadata(),
        "assistant_response": assistant_response,
        "assistant_audio_url": f"/api/audio/{assistant_audio_filename}",
    }
