from pathlib import Path

from openai import OpenAI

from app.core.settings import app_settings

VOICE_AGENT_SYSTEM_PROMPT = (
    "You are a helpful AI voice customer support agent. Answer clearly, briefly, "
    "and politely. If the user request is unclear, ask one focused follow-up question."
)


def _create_openai_client() -> OpenAI:
    if not app_settings.openai_api_key.strip():
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Set it in backend/.env before running audio jobs."
        )
    return OpenAI(api_key=app_settings.openai_api_key)


def transcribe_audio(file_path: str) -> str:
    audio_path = Path(file_path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    client = _create_openai_client()

    try:
        with audio_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=app_settings.whisper_model,
                file=audio_file,
            )
    except Exception as exc:
        raise RuntimeError(f"OpenAI transcription failed for file '{audio_path.name}'.") from exc

    transcript_text = getattr(transcription, "text", None)
    if not transcript_text or not transcript_text.strip():
        raise RuntimeError("OpenAI transcription response did not include transcript text.")

    return transcript_text.strip()


def generate_assistant_response(transcript: str) -> str:
    transcript_text = transcript.strip()
    if not transcript_text:
        raise ValueError("Transcript is empty and cannot be sent to the assistant model.")

    client = _create_openai_client()

    try:
        completion = client.chat.completions.create(
            model=app_settings.chat_model,
            messages=[
                {"role": "system", "content": VOICE_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": transcript_text},
            ],
        )
    except Exception as exc:
        raise RuntimeError("OpenAI assistant response generation failed.") from exc

    assistant_message = completion.choices[0].message.content if completion.choices else None
    if not assistant_message or not assistant_message.strip():
        raise RuntimeError("Assistant response was empty.")

    return assistant_message.strip()
