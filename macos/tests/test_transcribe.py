"""
Author: L. Saetta
Date last modified: 2026-08-18
License: MIT
Description: Tests command construction and input validation for the macOS ASR demo.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from macos.transcribe import build_command, parse_arguments, transcribe


def test_build_command_uses_mlx_audio_and_requested_options() -> None:
    """Build a command that preserves core ASR settings."""
    settings = parse_arguments(
        [
            "sample.wav",
            "--language",
            "en",
            "--format",
            "json",
            "--max-parallel-segments",
            "1",
            "--verbose",
        ]
    )

    command = build_command(settings, Path("output/sample"))

    assert command[:3] == [sys.executable, "-m", "mlx_audio.stt.generate"]
    assert command[command.index("--language") + 1] == "en"
    assert command[command.index("--format") + 1] == "json"
    assert command[command.index("--max-parallel-segments") + 1] == "1"
    assert command[-1] == "--verbose"


def test_transcribe_rejects_missing_audio(tmp_path: Path) -> None:
    """Reject a non-existent audio file before invoking mlx-audio."""
    settings = parse_arguments(
        [str(tmp_path / "missing.wav"), "--output-dir", str(tmp_path / "output")]
    )

    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        transcribe(settings)


def test_transcribe_invokes_mlx_audio_and_returns_output_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run the external runtime with a generated output stem."""
    audio_path = tmp_path / "sample.wav"
    audio_path.touch()
    settings = parse_arguments(
        [str(audio_path), "--format", "srt", "--output-dir", str(tmp_path / "output")]
    )
    captured_command: list[str] = []

    def fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        captured_command.extend(command)
        assert check is True
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    transcript_path = transcribe(settings)

    assert transcript_path == tmp_path / "output" / "sample.srt"
    assert captured_command[:3] == [sys.executable, "-m", "mlx_audio.stt.generate"]
