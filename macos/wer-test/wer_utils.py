"""
Author: L. Saetta
Date last modified: 2026-08-18
License: MIT
Description: Provides language mapping, text normalization, and WER helpers.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence

from jiwer import wer

FLEURS_CONFIG_BY_LANGUAGE = {
    "ar": "ar_eg",
    "de": "de_de",
    "el": "el_gr",
    "en": "en_us",
    "es": "es_419",
    "fr": "fr_fr",
    "it": "it_it",
    "ja": "ja_jp",
    "ko": "ko_kr",
    "nl": "nl_nl",
    "pl": "pl_pl",
    "pt": "pt_br",
    "vi": "vi_vn",
    "zh": "cmn_hans_cn",
}


def get_fleurs_config(language: str) -> str:
    """Return the FLEURS configuration name for a Cohere language code.

    Args:
        language: ISO-style Cohere ASR language code, such as ``it``.

    Returns:
        Matching FLEURS configuration name.

    Raises:
        ValueError: If the language is not present in the supported mapping.
    """
    normalized_language = language.lower().strip()
    try:
        return FLEURS_CONFIG_BY_LANGUAGE[normalized_language]
    except KeyError as error:
        supported_languages = ", ".join(sorted(FLEURS_CONFIG_BY_LANGUAGE))
        raise ValueError(
            f"Unsupported language '{language}'. Choose one of: {supported_languages}."
        ) from error


def normalize_transcript(text: str) -> str:
    """Normalize text consistently before word error rate calculation.

    Args:
        text: Raw reference or hypothesis transcript.

    Returns:
        Unicode-normalized, lowercase, punctuation-free text with collapsed
        whitespace.
    """
    normalized = unicodedata.normalize("NFKC", text).lower()
    without_punctuation = "".join(
        " " if unicodedata.category(character).startswith("P") else character
        for character in normalized
    )
    return re.sub(r"\s+", " ", without_punctuation).strip()


def calculate_wer(references: Sequence[str], hypotheses: Sequence[str]) -> float:
    """Calculate corpus WER for matching normalized transcript collections.

    Args:
        references: Reference transcripts after normalization.
        hypotheses: Hypothesis transcripts after normalization.

    Returns:
        Corpus word error rate.

    Raises:
        ValueError: If inputs are empty or have different lengths.
    """
    if not references:
        raise ValueError("At least one successful transcription is required.")
    if len(references) != len(hypotheses):
        raise ValueError("References and hypotheses must have the same length.")
    return float(wer(list(references), list(hypotheses)))


def validate_positive(value: int, name: str) -> int:
    """Validate a strictly positive integer setting.

    Args:
        value: Setting value to validate.
        name: Human-readable setting name for any error message.

    Returns:
        The validated setting value.

    Raises:
        ValueError: If value is not strictly positive.
    """
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value
