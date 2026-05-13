from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterator
from uuid import uuid4
import re
import shutil

import requests
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from src.config.env import BASE_DIR, settings
from src.utils import ConflictError


DRIVE_FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
LOCAL_ID_PREFIX = "local:"


@dataclass
class DriveFileUploadResult:
    file_id: str
    mime_type: str | None
    size: int | None


@dataclass
class DriveStreamResult:
    status_code: int
    headers: dict[str, str]
    chunks: Iterator[bytes]


class DriveService:
    def __init__(self):
        self.local_root = BASE_DIR / settings.LOCAL_MEDIA_ROOT
        self.local_root.mkdir(parents=True, exist_ok=True)
        self.credentials = None
        self.drive = None

        credentials_path = self._credentials_path()
        if credentials_path is None or not credentials_path.exists():
            return

        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=DRIVE_SCOPES,
        )
        self.drive = build("drive", "v3", credentials=self.credentials)

    @property
    def using_google_drive(self) -> bool:
        return self.drive is not None and self.credentials is not None

    def create_folder(self, name: str, parent_folder_id: str | None = None) -> str:
        if not self.using_google_drive:
            return self._create_local_folder(name, parent_folder_id)

        parent_folder_id = parent_folder_id or settings.GOOGLE_DRIVE_ROOT_FOLDER_ID
        if not parent_folder_id:
            raise ConflictError("Falta configurar GOOGLE_DRIVE_ROOT_FOLDER_ID")

        metadata = {
            "name": name,
            "mimeType": DRIVE_FOLDER_MIME_TYPE,
            "parents": [parent_folder_id],
        }

        folder = (
            self.drive.files()
            .create(
                body=metadata,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )
        return folder["id"]

    def upload_video(
        self,
        file: BinaryIO,
        filename: str,
        mime_type: str,
        parent_folder_id: str,
    ) -> DriveFileUploadResult:
        if not self.using_google_drive or self._is_local_id(parent_folder_id):
            return self._upload_local_video(file, filename, mime_type, parent_folder_id)

        file.seek(0)
        metadata = {
            "name": filename,
            "parents": [parent_folder_id],
        }
        media = MediaIoBaseUpload(
            file,
            mimetype=mime_type,
            resumable=True,
        )

        created = (
            self.drive.files()
            .create(
                body=metadata,
                media_body=media,
                fields="id,mimeType,size",
                supportsAllDrives=True,
            )
            .execute()
        )

        size = created.get("size")
        return DriveFileUploadResult(
            file_id=created["id"],
            mime_type=created.get("mimeType"),
            size=int(size) if size is not None else None,
        )

    def stream_file(
        self,
        file_id: str,
        range_header: str | None = None,
        fallback_mime_type: str = "video/mp4",
    ) -> DriveStreamResult:
        if self._is_local_id(file_id):
            return self._stream_local_file(file_id, range_header, fallback_mime_type)

        if not self.using_google_drive:
            raise ConflictError("El archivo no es local y Google Drive no esta configurado")

        if not self.credentials.valid:
            self.credentials.refresh(GoogleAuthRequest())

        headers = {"Authorization": f"Bearer {self.credentials.token}"}
        if range_header:
            headers["Range"] = range_header

        response = requests.get(
            (
                "https://www.googleapis.com/drive/v3/files/"
                f"{file_id}?alt=media&supportsAllDrives=true"
            ),
            headers=headers,
            stream=True,
        )

        if response.status_code >= 400:
            response.close()
            raise ConflictError("No se pudo obtener el video desde Google Drive")

        response_headers = {
            "Accept-Ranges": response.headers.get("Accept-Ranges", "bytes"),
            "Content-Type": response.headers.get("Content-Type", fallback_mime_type),
        }
        for header_name in ("Content-Length", "Content-Range"):
            value = response.headers.get(header_name)
            if value:
                response_headers[header_name] = value

        def iter_chunks():
            try:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        yield chunk
            finally:
                response.close()

        return DriveStreamResult(
            status_code=response.status_code,
            headers=response_headers,
            chunks=iter_chunks(),
        )

    def _credentials_path(self) -> Path | None:
        credentials_file = settings.GOOGLE_DRIVE_CREDENTIALS_FILE
        if not credentials_file:
            return None

        credentials_path = Path(credentials_file)
        if not credentials_path.is_absolute():
            credentials_path = BASE_DIR / credentials_path
        return credentials_path

    def _create_local_folder(self, name: str, parent_folder_id: str | None = None) -> str:
        parent_path = self._local_path_from_id(parent_folder_id) if parent_folder_id else self.local_root
        folder_name = f"{self._safe_name(name)}-{uuid4().hex[:8]}"
        folder_path = parent_path / folder_name
        folder_path.mkdir(parents=True, exist_ok=False)
        return self._local_id_from_path(folder_path)

    def _upload_local_video(
        self,
        file: BinaryIO,
        filename: str,
        mime_type: str,
        parent_folder_id: str,
    ) -> DriveFileUploadResult:
        parent_path = self._local_path_from_id(parent_folder_id)
        parent_path.mkdir(parents=True, exist_ok=True)

        safe_filename = f"{uuid4().hex[:8]}-{self._safe_name(filename)}"
        destination = parent_path / safe_filename

        file.seek(0)
        with destination.open("wb") as output:
            shutil.copyfileobj(file, output)

        return DriveFileUploadResult(
            file_id=self._local_id_from_path(destination),
            mime_type=mime_type,
            size=destination.stat().st_size,
        )

    def _stream_local_file(
        self,
        file_id: str,
        range_header: str | None,
        fallback_mime_type: str,
    ) -> DriveStreamResult:
        path = self._local_path_from_id(file_id)
        if not path.is_file():
            raise ConflictError("No se encontro el video local")

        file_size = path.stat().st_size
        start = 0
        end = file_size - 1
        status_code = 200

        if range_header:
            match = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if match:
                status_code = 206
                if match.group(1):
                    start = int(match.group(1))
                if match.group(2):
                    end = min(int(match.group(2)), file_size - 1)

        content_length = max(0, end - start + 1)
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Type": fallback_mime_type,
            "Content-Length": str(content_length),
        }
        if status_code == 206:
            headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

        def iter_file():
            with path.open("rb") as video:
                video.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk = video.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        return DriveStreamResult(
            status_code=status_code,
            headers=headers,
            chunks=iter_file(),
        )

    def _local_path_from_id(self, file_id: str | None) -> Path:
        if not file_id or not self._is_local_id(file_id):
            raise ConflictError("El recurso local no tiene un identificador valido")

        relative_path = file_id[len(LOCAL_ID_PREFIX) :]
        path = (self.local_root / relative_path).resolve()
        local_root = self.local_root.resolve()
        if not path.is_relative_to(local_root):
            raise ConflictError("Ruta local invalida")
        return path

    def _local_id_from_path(self, path: Path) -> str:
        relative_path = path.resolve().relative_to(self.local_root.resolve())
        return f"{LOCAL_ID_PREFIX}{relative_path.as_posix()}"

    def _is_local_id(self, file_id: str | None) -> bool:
        return bool(file_id and file_id.startswith(LOCAL_ID_PREFIX))

    def _safe_name(self, value: str) -> str:
        value = Path(value).name.strip()
        value = re.sub(r"[^a-zA-Z0-9._ -]+", "", value)
        value = re.sub(r"\s+", "-", value)
        return value or "archivo"
