"""
Author: L. Saetta
Date last modified: 2026-08-19
License: MIT
Description: Loads validated configuration for the local Demo 02 ASR backend.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MODEL_ID = "CohereLabs/cohere-transcribe-03-2026"
DEFAULT_LANGUAGE = "it"
DEFAULT_MAX_TOKENS = 8192
DEFAULT_MAX_UPLOAD_BYTES = 100 * 1024 * 1024


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the local ASR backend.

    Attributes:
        model_id: Hugging Face model ID or local MLX-compatible model path.
        language: Default ASR language code.
        max_tokens: Maximum transcript tokens generated for one request.
        max_upload_bytes: Maximum accepted audio upload size in bytes.
    """

    model_id: str = DEFAULT_MODEL_ID
    language: str = DEFAULT_LANGUAGE
    max_tokens: int = DEFAULT_MAX_TOKENS
    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES


def _positive_integer(environment_name: str, default: int) -> int:
    """Read a positive integer setting from the process environment.

    Args:
        environment_name: Name of the environment variable to read.
        default: Value used when the environment variable is absent.

    Returns:
        The validated positive integer.

    Raises:
        ValueError: If the configured value is not a positive integer.
    """
    value = os.getenv(environment_name)
    if value is None:
        return default

    try:
        parsed_value = int(value)
    except ValueError as error:
        raise ValueError(f"{environment_name} must be an integer.") from error
    if parsed_value <= 0:
        raise ValueError(f"{environment_name} must be greater than zero.")
    return parsed_value


def load_settings() -> Settings:
    """Load the Demo 02 settings from environment variables.

    Returns:
        Validated backend settings.

    Raises:
        ValueError: If a configured numeric setting is invalid.
    """
    model_id = os.getenv("COHERE_VOICE_MODEL", DEFAULT_MODEL_ID).strip()
    language = os.getenv("COHERE_VOICE_LANGUAGE", DEFAULT_LANGUAGE).strip()
    if not model_id:
        raise ValueError("COHERE_VOICE_MODEL must not be empty.")
    if not language:
        raise ValueError("COHERE_VOICE_LANGUAGE must not be empty.")

    return Settings(
        model_id=model_id,
        language=language,
        max_tokens=_positive_integer("COHERE_VOICE_MAX_TOKENS", DEFAULT_MAX_TOKENS),
        max_upload_bytes=_positive_integer(
            "COHERE_VOICE_MAX_UPLOAD_BYTES", DEFAULT_MAX_UPLOAD_BYTES
        ),
    )
