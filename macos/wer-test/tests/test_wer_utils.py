"""
Author: L. Saetta
Date last modified: 2026-08-18
License: MIT
Description: Tests language mapping and WER helpers without model execution.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wer_utils import (
    calculate_wer,
    get_fleurs_config,
    iter_indexed_batches,
    normalize_transcript,
    validate_positive,
)


def test_get_fleurs_config_returns_italian_default() -> None:
    """Map the Cohere Italian code to the FLEURS Italian configuration."""
    assert get_fleurs_config("it") == "it_it"


def test_get_fleurs_config_rejects_unknown_language() -> None:
    """Reject a language that is not configured for the evaluation notebook."""
    with pytest.raises(ValueError, match="Unsupported language"):
        get_fleurs_config("xx")


def test_normalize_transcript_removes_case_and_punctuation() -> None:
    """Normalize equivalent Italian transcript variants consistently."""
    assert normalize_transcript("  Ciao, MONDO!  ") == "ciao mondo"


def test_calculate_wer_returns_expected_word_error_rate() -> None:
    """Calculate WER over normalized sentence collections."""
    result = calculate_wer(["ciao mondo", "buona sera"], ["ciao mondo", "buona"])
    assert result == pytest.approx(0.25)


def test_calculate_wer_rejects_invalid_inputs() -> None:
    """Require matching, non-empty reference and hypothesis lists."""
    with pytest.raises(ValueError, match="successful transcription"):
        calculate_wer([], [])
    with pytest.raises(ValueError, match="same length"):
        calculate_wer(["ciao"], [])


def test_validate_positive_rejects_zero() -> None:
    """Reject a non-positive notebook sample-size setting."""
    with pytest.raises(ValueError, match="Sample size"):
        validate_positive(0, "Sample size")


def test_iter_indexed_batches_preserves_record_oriented_rows() -> None:
    """Build batches from individual records instead of collection slices."""
    records = [{"id": 1}, {"id": 2}, {"id": 3}]

    assert list(iter_indexed_batches(records, 2)) == [
        (0, [{"id": 1}, {"id": 2}]),
        (2, [{"id": 3}]),
    ]
