from pathlib import Path
from threading import Lock
from typing import Any
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
_IVRIT_MODEL: Any | None = None
_IVRIT_MODEL_LOCK = Lock()


def _create_openai_client() -> OpenAI:
    if not app_settings.openai_api_key.strip():
        raise RuntimeError(
            "OPENAI_API_KEY is not configured. Set it in backend/.env before generating AI responses."
        )
    return OpenAI(api_key=app_settings.openai_api_key)


def _normalized_transcription_provider() -> str:
    provider = app_settings.transcription_provider.strip().lower().replace("_", "-")
    if provider == "ivrit-ai":
        return "ivrit"
    return provider


def _load_ivrit_model() -> Any:
    global _IVRIT_MODEL

    if _IVRIT_MODEL is not None:
        return _IVRIT_MODEL

    with _IVRIT_MODEL_LOCK:
        if _IVRIT_MODEL is not None:
            return _IVRIT_MODEL

        try:
            import ivrit
        except ImportError as exc:
            raise RuntimeError(
                "Ivrit AI transcription dependencies are missing. "
                "Run `pip install -r backend/requirements.txt`."
            ) from exc

        model_kwargs = {
            "engine": app_settings.ivrit_engine,
            "model": app_settings.ivrit_model,
        }
        if app_settings.ivrit_device.strip():
            model_kwargs["device"] = app_settings.ivrit_device.strip()
        if app_settings.ivrit_compute_type.strip():
            model_kwargs["compute_type"] = app_settings.ivrit_compute_type.strip()

        try:
            _IVRIT_MODEL = ivrit.load_model(**model_kwargs)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load Ivrit AI transcription model '{app_settings.ivrit_model}'."
            ) from exc

        return _IVRIT_MODEL


def _load_faster_whisper_model() -> Any:
    global _IVRIT_MODEL

    if _IVRIT_MODEL is not None:
        return _IVRIT_MODEL

    with _IVRIT_MODEL_LOCK:
        if _IVRIT_MODEL is not None:
            return _IVRIT_MODEL

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "Faster Whisper dependencies are missing. "
                "Run `pip install -r backend/requirements.txt`."
            ) from exc

        model_kwargs = {}
        if app_settings.ivrit_device.strip():
            model_kwargs["device"] = app_settings.ivrit_device.strip()
        if app_settings.ivrit_compute_type.strip():
            model_kwargs["compute_type"] = app_settings.ivrit_compute_type.strip()

        try:
            _IVRIT_MODEL = WhisperModel(app_settings.ivrit_model, **model_kwargs)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load Ivrit AI Faster Whisper model '{app_settings.ivrit_model}'."
            ) from exc

        return _IVRIT_MODEL


def _extract_transcript_text(transcription: Any, provider_name: str) -> str:
    if isinstance(transcription, dict):
        transcript_text = transcription.get("text")
    else:
        transcript_text = getattr(transcription, "text", None)

    if not transcript_text or not transcript_text.strip():
        raise RuntimeError(f"{provider_name} transcription response did not include transcript text.")

    return transcript_text.strip()


def _transcribe_audio_with_ivrit(audio_path: Path) -> str:
    if app_settings.ivrit_engine.strip().lower() == "faster-whisper":
        return _transcribe_audio_with_faster_whisper(audio_path)

    model = _load_ivrit_model()

    try:
        transcription = model.transcribe(
            path=str(audio_path),
            language=app_settings.transcription_language.strip() or None,
            output_options={"word_timestamps": False, "extra_data": False},
        )
    except Exception as exc:
        raise RuntimeError(f"Ivrit AI transcription failed for file '{audio_path.name}'.") from exc

    return _extract_transcript_text(transcription, "Ivrit AI")


def _transcribe_audio_with_faster_whisper(audio_path: Path) -> str:
    model = _load_faster_whisper_model()
    initial_prompt = app_settings.ivrit_initial_prompt.strip() or None

    try:
        segments, _ = model.transcribe(
            str(audio_path),
            language=app_settings.transcription_language.strip() or "he",
            task="transcribe",
            initial_prompt=initial_prompt,
            word_timestamps=False,
            condition_on_previous_text=False,
        )
        transcript_text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
    except Exception as exc:
        raise RuntimeError(
            f"Ivrit AI Faster Whisper transcription failed for file '{audio_path.name}'."
        ) from exc

    return _extract_transcript_text({"text": transcript_text}, "Ivrit AI")


def _transcribe_audio_with_openai(audio_path: Path) -> str:
    client = _create_openai_client()

    try:
        with audio_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=app_settings.whisper_model,
                file=audio_file,
            )
    except Exception as exc:
        raise RuntimeError(f"OpenAI transcription failed for file '{audio_path.name}'.") from exc

    return _extract_transcript_text(transcription, "OpenAI")


def transcribe_audio(file_path: str) -> str:
    audio_path = Path(file_path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    provider = _normalized_transcription_provider()
    if provider == "ivrit":
        return _transcribe_audio_with_ivrit(audio_path)
    if provider == "openai":
        return _transcribe_audio_with_openai(audio_path)

    raise RuntimeError(
        f"Unsupported TRANSCRIPTION_PROVIDER '{app_settings.transcription_provider}'. "
        "Use 'ivrit' or 'openai'."
    )


def get_transcription_metadata() -> dict[str, str]:
    provider = _normalized_transcription_provider()
    if provider == "ivrit":
        return {
            "transcription_provider": "ivrit",
            "transcription_engine": app_settings.ivrit_engine,
            "transcription_model": app_settings.ivrit_model,
            "transcription_language": app_settings.transcription_language,
        }
    if provider == "openai":
        return {
            "transcription_provider": "openai",
            "transcription_engine": "openai",
            "transcription_model": app_settings.whisper_model,
            "transcription_language": app_settings.transcription_language,
        }
    return {
        "transcription_provider": provider,
        "transcription_engine": "",
        "transcription_model": "",
        "transcription_language": app_settings.transcription_language,
    }


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
