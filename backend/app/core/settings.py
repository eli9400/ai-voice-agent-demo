import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE_PATH)


@dataclass(frozen=True)
class AppSettings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    transcription_provider: str = os.getenv("TRANSCRIPTION_PROVIDER", "ivrit")
    whisper_model: str = "whisper-1"
    transcription_language: str = os.getenv("TRANSCRIPTION_LANGUAGE", "he")
    ivrit_engine: str = os.getenv("IVRIT_ENGINE", "faster-whisper")
    ivrit_model: str = os.getenv("IVRIT_MODEL", "ivrit-ai/whisper-large-v3-turbo-ct2")
    ivrit_device: str = os.getenv("IVRIT_DEVICE", "cpu")
    ivrit_compute_type: str = os.getenv("IVRIT_COMPUTE_TYPE", "")
    ivrit_initial_prompt: str = os.getenv("IVRIT_INITIAL_PROMPT", "שלום, היי, תודה, בבקשה.")
    chat_model: str = "gpt-4o-mini"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"


app_settings = AppSettings()
