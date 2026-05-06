import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE_PATH)


@dataclass(frozen=True)
class AppSettings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    whisper_model: str = "whisper-1"
    chat_model: str = "gpt-4o-mini"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"


app_settings = AppSettings()
