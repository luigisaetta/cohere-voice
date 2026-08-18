"""
Author: L. Saetta
Date last modified: 2026-08-18
License: MIT
Description: Tests recording orchestration and device discovery without microphone access.
"""

from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np
import pytest

from macos.demo01.record_and_transcribe import (
    SAMPLE_RATE,
    build_transcription_settings,
    list_input_devices,
    parse_arguments,
    record_audio,
    run_demo,
)


def test_list_input_devices_filters_output_only_devices(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return only SoundDevice entries with at least one input channel."""
    monkeypatch.setattr(
        "sounddevice.query_devices",
        lambda: [
            {"name": "Bose Headphones", "max_input_channels": 1},
            {"name": "Mac Speakers", "max_input_channels": 0},
        ],
    )

    assert list_input_devices() == [(0, "Bose Headphones")]


def test_record_audio_writes_a_16khz_mono_wav(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Record synthetic samples without requiring a physical microphone."""
    recorded_arguments: dict[str, object] = {}

    def fake_rec(*args: object, **kwargs: object) -> np.ndarray:
        recorded_arguments["frames"] = args[0]
        recorded_arguments.update(kwargs)
        return np.array([[0.0], [0.5], [-0.5]], dtype=np.float32)

    monkeypatch.setattr("sounddevice.rec", fake_rec)
    monkeypatch.setattr("sounddevice.wait", lambda: None)
    output_path = tmp_path / "recording.wav"

    result = record_audio(1.0, "Bose Headphones", output_path)

    assert result == output_path
    assert recorded_arguments["frames"] == SAMPLE_RATE
    assert recorded_arguments["samplerate"] == SAMPLE_RATE
    assert recorded_arguments["channels"] == 1
    with wave.open(str(output_path), "rb") as wav_file:
        assert wav_file.getframerate() == SAMPLE_RATE
        assert wav_file.getnchannels() == 1


def test_record_audio_rejects_invalid_duration(tmp_path: Path) -> None:
    """Reject an invalid duration before accessing an audio device."""
    with pytest.raises(ValueError, match="greater than zero"):
        record_audio(0, None, tmp_path / "recording.wav")


def test_run_demo_records_then_invokes_mlx_audio(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run the full workflow while mocking the microphone and ASR runtime."""
    settings = parse_arguments(
        [
            "--duration",
            "2",
            "--recording-name",
            "bose-test",
            "--output-dir",
            str(tmp_path),
            "--format",
            "json",
        ]
    )
    monkeypatch.setattr(
        "macos.demo01.record_and_transcribe.record_audio",
        lambda duration, device, output_path: output_path,
    )
    captured_command: list[str] = []

    def fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        captured_command.extend(command)
        assert check is True
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    recording_path, transcript_path = run_demo(settings)

    assert recording_path == tmp_path / "bose-test.wav"
    assert transcript_path == tmp_path / "bose-test.json"
    assert "mlx_audio.stt.generate" in captured_command


def test_build_transcription_settings_preserves_demo_options() -> None:
    """Pass output and language options from recording to transcription."""
    settings = parse_arguments(
        ["--language", "en", "--format", "vtt", "--max-parallel-segments", "1"]
    )

    transcription_settings = build_transcription_settings(settings, Path("sample.wav"))

    assert transcription_settings.language == "en"
    assert transcription_settings.format == "vtt"
    assert transcription_settings.max_parallel_segments == 1
