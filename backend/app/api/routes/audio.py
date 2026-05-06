from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["audio"])

TTS_OUTPUT_DIR = (Path(__file__).resolve().parents[3] / "storage" / "tts_outputs").resolve()


@router.get("/api/audio/{filename}")
def get_generated_audio(filename: str) -> FileResponse:
    if not filename or Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    if Path(filename).suffix.lower() != ".mp3":
        raise HTTPException(status_code=400, detail="Only .mp3 files are supported.")

    resolved_path = (TTS_OUTPUT_DIR / filename).resolve()
    try:
        resolved_path.relative_to(TTS_OUTPUT_DIR)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid audio path.") from exc

    if not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found.")

    return FileResponse(path=resolved_path, media_type="audio/mpeg", filename=filename)
