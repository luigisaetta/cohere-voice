"""
Author: L. Saetta
Date last modified: 2026-08-19
License: MIT
Description: Loads MLX Audio models lazily and runs local audio transcription.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from mlx_audio.stt.utils import load_model

from .settings import Settings

ModelLoader = Callable[[str], Any]


class TranscriptionService:
    """Own a lazily loaded MLX Audio model for local ASR requests.

    Args:
        settings: Validated backend settings.
        model_loader: Callable that loads an MLX Audio model. Injectable for tests.
    """

    def __init__(
        self, settings: Settings, model_loader: ModelLoader = load_model
    ) -> None:
        self._settings = settings
        self._model_loader = model_loader
        self._model: Any | None = None

    @property
    def model_id(self) -> str:
        """Return the configured model identifier."""
        return self._settings.model_id

    @property
    def default_language(self) -> str:
        """Return the configured default language code."""
        return self._settings.language

    @property
    def is_loaded(self) -> bool:
        """Return whether the ASR model is currently held in memory."""
        return self._model is not None

    def transcribe(self, audio_path: Path, language: str | None = None) -> str:
        """Transcribe one local audio file with the configured model.

        Args:
            audio_path: Existing audio file to pass to MLX Audio.
            language: Optional language code overriding the configured default.

        Returns:
            The model transcript with surrounding whitespace removed.

        Raises:
            FileNotFoundError: If the source audio file does not exist.
            RuntimeError: If the model returns no transcript text.
        """
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self._model is None:
            self._model = self._model_loader(self._settings.model_id)

        output = self._model.generate(
            str(audio_path),
            language=language or self._settings.language,
            max_tokens=self._settings.max_tokens,
        )
        transcript = str(output.text).strip()
        if not transcript:
            raise RuntimeError("The ASR model returned an empty transcript.")
        return transcript
