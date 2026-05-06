from pathlib import Path
from uuid import uuid4

from openai import OpenAI

from app.core.settings import app_settings

VOICE_AGENT_SYSTEM_PROMPT = (
    "You are a Hebrew-speaking AI voice customer support agent for a fictional telecom "
    "company called DemoCell.\n"
    "Your job is to help customers with mobile plans, billing questions, reception issues, "
    "SIM activation, and joining the service.\n"
    "Speak in natural Hebrew unless the user speaks another language.\n"
    "Keep answers short, clear, and suitable for voice conversation.\n"
    "Ask only one focused follow-up question when information is missing.\n"
    "Do not invent account-specific details, prices, or policies.\n"
    "If you do not have enough information, explain that you need more details.\n"
    "Be polite, practical, and conversational.\n"
    "Avoid long explanations."
)
TTS_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "storage" / "tts_outputs"
TTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def generate_speech_audio(text: str) -> str:
    tts_input = text.strip()
    if not tts_input:
        raise ValueError("Assistant response is empty and cannot be converted to speech.")

    output_filename = f"{uuid4()}.mp3"
    output_path = (TTS_OUTPUT_DIR / output_filename).resolve()
    client = _create_openai_client()

    try:
        speech_response = client.audio.speech.create(
            model=app_settings.tts_model,
            voice=app_settings.tts_voice,
            input=tts_input,
            response_format="mp3",
        )
        speech_response.write_to_file(output_path)
    except Exception as exc:
        raise RuntimeError("OpenAI TTS generation failed.") from exc

    return str(output_path)
