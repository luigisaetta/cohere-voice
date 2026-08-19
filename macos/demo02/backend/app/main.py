"""
Author: L. Saetta
Date last modified: 2026-08-19
License: MIT
Description: Exposes health, model, and local audio-transcription HTTP endpoints.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .service import TranscriptionService
from .settings import Settings, load_settings

ALLOWED_AUDIO_SUFFIXES = {".m4a", ".mp3", ".mp4", ".mpeg", ".ogg", ".wav", ".webm"}
UPLOAD_CHUNK_SIZE = 1024 * 1024


class HealthResponse(BaseModel):
    """Represent readiness information for the local ASR backend."""

    status: str
    model_id: str
    model_loaded: bool


class ModelResponse(BaseModel):
    """Represent the model configuration exposed to the local UI."""

    default_model_id: str
    default_language: str


class TranscriptionResponse(BaseModel):
    """Represent a completed local transcription."""

    transcript: str
    model_id: str
    language: str
    filename: str


def _suffix_for_upload(filename: str | None) -> str:
    """Validate an uploaded audio filename and return its suffix.

    Args:
        filename: Client-provided filename, if any.

    Returns:
        Lowercase filename suffix accepted by the backend.

    Raises:
        HTTPException: If the file has no supported audio suffix.
    """
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_AUDIO_SUFFIXES:
        allowed_formats = ", ".join(sorted(ALLOWED_AUDIO_SUFFIXES))
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio format. Use one of: {allowed_formats}.",
        )
    return suffix


async def _write_upload(
    upload: UploadFile, destination: Path, maximum_bytes: int
) -> None:
    """Persist an upload while enforcing the configured size limit.

    Args:
        upload: Uploaded browser audio file.
        destination: Temporary destination path.
        maximum_bytes: Maximum accepted byte count.

    Raises:
        HTTPException: If the upload is empty or exceeds the configured limit.
    """
    bytes_written = 0
    with destination.open("wb") as audio_file:
        while chunk := await upload.read(UPLOAD_CHUNK_SIZE):
            bytes_written += len(chunk)
            if bytes_written > maximum_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"Audio upload exceeds the {maximum_bytes} byte limit.",
                )
            audio_file.write(chunk)
    if bytes_written == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio upload is empty.",
        )


def _create_application(settings: Settings, service: TranscriptionService) -> FastAPI:
    """Create the FastAPI application with explicitly supplied dependencies.

    Args:
        settings: Validated backend settings.
        service: Local transcription service to use for requests.

    Returns:
        Configured FastAPI application.
    """
    application = FastAPI(title="Cohere Voice Demo 02 Backend", version="0.1.0")
    application.state.settings = settings
    application.state.service = service

    @application.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Report backend availability without forcing the model to load."""
        return HealthResponse(
            status="ok",
            model_id=service.model_id,
            model_loaded=service.is_loaded,
        )

    @application.get("/models", response_model=ModelResponse)
    def models() -> ModelResponse:
        """Return the locally configured default ASR model."""
        return ModelResponse(
            default_model_id=service.model_id,
            default_language=service.default_language,
        )

    @application.post("/transcribe", response_model=TranscriptionResponse)
    async def transcribe(
        audio: Annotated[UploadFile, File(description="Recorded audio file")],
        language: Annotated[str | None, Form()] = None,
    ) -> TranscriptionResponse:
        """Transcribe one uploaded audio recording and delete it afterwards."""
        suffix = _suffix_for_upload(audio.filename)
        requested_language = (language or service.default_language).strip()
        if not requested_language:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language must not be empty.",
            )

        descriptor, temporary_name = tempfile.mkstemp(
            prefix="cohere-voice-", suffix=suffix
        )
        os.close(descriptor)
        temporary_path = Path(temporary_name)
        try:
            await _write_upload(audio, temporary_path, settings.max_upload_bytes)
            transcript = service.transcribe(temporary_path, requested_language)
        except HTTPException:
            raise
        except (FileNotFoundError, RuntimeError) as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error
        except Exception as error:  # pragma: no cover - protects local model internals.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Local transcription failed. Check the backend console for details.",
            ) from error
        finally:
            await audio.close()
            temporary_path.unlink(missing_ok=True)

        return TranscriptionResponse(
            transcript=transcript,
            model_id=service.model_id,
            language=requested_language,
            filename=audio.filename or f"recording{suffix}",
        )

    @application.exception_handler(ValueError)
    async def configuration_error(_, error: ValueError) -> JSONResponse:
        """Return invalid backend configuration as a non-sensitive JSON error."""
        return JSONResponse(status_code=500, content={"detail": str(error)})

    return application


def create_app(
    settings: Settings | None = None, service: TranscriptionService | None = None
) -> FastAPI:
    """Create the Demo 02 FastAPI application.

    Args:
        settings: Optional settings override, primarily for tests.
        service: Optional transcription-service override, primarily for tests.

    Returns:
        A configured FastAPI application.
    """
    effective_settings = settings or load_settings()
    effective_service = service or TranscriptionService(effective_settings)
    return _create_application(effective_settings, effective_service)


app = create_app()
