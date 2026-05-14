from dataclasses import dataclass
from pathlib import Path
import json
import shutil
import subprocess
import tempfile

from fastapi import UploadFile

from src.services.storage_service import StorageFileUploadResult, StorageService
from src.utils import ConflictError


QUALITY_HEIGHTS = {
    "HD": 720,
    "1440p": 1440,
    "4K": 2160,
}
QUALITY_PRIORITY = {
    "HD": 1,
    "1440p": 2,
    "4K": 3,
}


@dataclass
class ProcessedVideoVariants:
    max_quality: str
    max_variant: StorageFileUploadResult
    variants: dict[str, StorageFileUploadResult]
    duration_min: float


class VideoProcessingService:
    def __init__(self, storage: StorageService | None = None):
        self.storage = storage or StorageService()

    def process_and_upload_variants(
        self,
        video_file: UploadFile,
        parent_folder_id: str,
    ) -> ProcessedVideoVariants:
        self._validate_tools()

        with tempfile.TemporaryDirectory(prefix="titoflix-video-") as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "source"
            video_file.file.seek(0)
            with source_path.open("wb") as destination:
                shutil.copyfileobj(video_file.file, destination)

            metadata = self._probe_video_metadata(source_path)
            source_height = metadata["height"]
            duration_min = round(metadata["duration_seconds"] / 60, 2)
            variants: dict[str, StorageFileUploadResult] = {}

            for quality, target_height in QUALITY_HEIGHTS.items():
                output_path = temp_path / f"{quality}.mp4"
                self._transcode(source_path, output_path, min(source_height, target_height))

                variants[quality] = self.storage.upload_video_variant(
                    file_path=output_path,
                    parent_folder_id=parent_folder_id,
                    quality=quality,
                    mime_type="video/mp4",
                )

            max_quality = max(variants, key=lambda quality: QUALITY_PRIORITY[quality])
            return ProcessedVideoVariants(
                max_quality=max_quality,
                max_variant=variants[max_quality],
                variants=variants,
                duration_min=max(duration_min, 0.01),
            )

    def _validate_tools(self) -> None:
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise ConflictError("FFmpeg no esta disponible en el backend")

    def _probe_video_metadata(self, source_path: Path) -> dict[str, float | int]:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=height:format=duration",
            "-of",
            "json",
            str(source_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise ConflictError("No se pudo leer la resolucion del video")

        data = json.loads(result.stdout or "{}")
        streams = data.get("streams") or []
        height = streams[0].get("height") if streams else None
        if not isinstance(height, int) or height < 1:
            raise ConflictError("El video no tiene una pista de imagen valida")

        try:
            duration_seconds = float((data.get("format") or {}).get("duration") or 0)
        except (TypeError, ValueError):
            duration_seconds = 0
        if duration_seconds <= 0:
            raise ConflictError("No se pudo leer la duracion del video")

        return {
            "height": height,
            "duration_seconds": duration_seconds,
        }

    def _transcode(self, source_path: Path, output_path: Path, target_height: int) -> None:
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-vf",
            f"scale=-2:min(ih\\,{target_height})",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise ConflictError("No se pudo convertir el video con FFmpeg")
