from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Voice Agent Demo Backend"
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)


settings = Settings()
