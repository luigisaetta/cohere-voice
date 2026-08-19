"""
Author: L. Saetta
Date last modified: 2026-08-19
License: MIT
Description: Tests the public HTTP contract of the Demo 02 FastAPI backend.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from macos.demo02.backend.app.main import create_app  # noqa: E402
from macos.demo02.backend.app.service import TranscriptionService  # noqa: E402
from macos.demo02.backend.app.settings import Settings  # noqa: E402


def build_client(monkeypatch: MonkeyPatch) -> tuple[TestClient, Mock]:
    """Build a client with a mocked model loader.

    Returns:
        Test client and the model loader mock used by its service.
    """
    monkeypatch.setattr(
        "macos.demo02.backend.app.service.shutil.which", lambda _: "/usr/bin/ffmpeg"
    )
    model = Mock()
    model.generate.return_value = Mock(text="A local transcript.")
    model_loader = Mock(return_value=model)
    settings = Settings(max_upload_bytes=32)
    service = TranscriptionService(settings, model_loader=model_loader)
    return TestClient(create_app(settings, service)), model_loader


def test_health_does_not_load_model(monkeypatch: MonkeyPatch) -> None:
    """Health reports the configured model without triggering a model download."""
    client, model_loader = build_client(monkeypatch)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["model_loaded"] is False
    model_loader.assert_not_called()


def test_models_returns_default_model_configuration(monkeypatch: MonkeyPatch) -> None:
    """Models endpoint exposes the current default model and language."""
    client, _ = build_client(monkeypatch)

    response = client.get("/models")

    assert response.status_code == 200
    assert response.json() == {
        "default_model_id": "CohereLabs/cohere-transcribe-03-2026",
        "default_language": "it",
    }


def test_transcribe_uploads_audio_and_returns_transcript(
    monkeypatch: MonkeyPatch,
) -> None:
    """A valid recording is transcribed through the injected local service."""
    client, model_loader = build_client(monkeypatch)

    response = client.post(
        "/transcribe",
        data={"language": "it"},
        files={"audio": ("recording.webm", b"test audio", "audio/webm")},
    )

    assert response.status_code == 200
    assert response.json()["transcript"] == "A local transcript."
    assert response.json()["filename"] == "recording.webm"
    model_loader.assert_called_once()


def test_transcribe_rejects_unsupported_audio_format(monkeypatch: MonkeyPatch) -> None:
    """Unsupported audio filename suffixes receive a clear client error."""
    client, _ = build_client(monkeypatch)

    response = client.post(
        "/transcribe",
        files={"audio": ("recording.txt", b"not audio", "text/plain")},
    )

    assert response.status_code == 415
    assert "Unsupported audio format" in response.json()["detail"]


def test_transcribe_rejects_empty_or_oversized_audio(monkeypatch: MonkeyPatch) -> None:
    """Empty and overly large uploads are rejected before model inference."""
    client, _ = build_client(monkeypatch)

    empty_response = client.post(
        "/transcribe", files={"audio": ("recording.webm", b"", "audio/webm")}
    )
    oversized_response = client.post(
        "/transcribe", files={"audio": ("recording.webm", b"x" * 33, "audio/webm")}
    )

    assert empty_response.status_code == 400
    assert oversized_response.status_code == 413


def test_transcribe_explains_when_ffmpeg_is_missing(monkeypatch: MonkeyPatch) -> None:
    """Browser audio reports the macOS ffmpeg installation command when unavailable."""
    client, _ = build_client(monkeypatch)
    monkeypatch.setattr("macos.demo02.backend.app.service.shutil.which", lambda _: None)

    response = client.post(
        "/transcribe",
        files={"audio": ("recording.webm", b"test audio", "audio/webm")},
    )

    assert response.status_code == 422
    assert (
        "conda install -n cohere-voice -c conda-forge ffmpeg"
        in response.json()["detail"]
    )
