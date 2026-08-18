"""
Author: L. Saetta
Date last modified: 2026-08-18
License: MIT
Description: Records microphone audio on macOS, then transcribes it with MLX Audio.
"""

from __future__ import annotations

import argparse
import subprocess
import wave
from datetime import datetime
from pathlib import Path
from typing import Sequence

import numpy as np
import sounddevice as sd

from macos.transcribe import (
    build_command,
    parse_arguments as parse_transcribe_arguments,
)

SAMPLE_RATE = 16_000
CHANNELS = 1
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the end-to-end recording demo.

    Args:
        arguments: Optional argument sequence. When omitted, arguments are read
            from the command line.

    Returns:
        Parsed recording and transcription settings.
    """
    parser = argparse.ArgumentParser(
        description="Record audio on macOS and transcribe it with Cohere Transcribe."
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List input devices, then exit without recording.",
    )
    parser.add_argument(
        "--device",
        help="Input device ID or name. Omit to use the macOS default input device.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=10.0,
        help="Recording duration in seconds (default: 10).",
    )
    parser.add_argument(
        "--language",
        default="it",
        help="Cohere Transcribe language code (default: it).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the recorded WAV and transcript.",
    )
    parser.add_argument(
        "--recording-name",
        help="Output filename stem. Defaults to a timestamped recording name.",
    )
    parser.add_argument(
        "--format",
        choices=("txt", "json", "srt", "vtt"),
        default="txt",
        help="Transcript format (default: txt).",
    )
    parser.add_argument(
        "--max-parallel-segments",
        type=int,
        help="Maximum audio segments processed in parallel during transcription.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information from mlx-audio.",
    )
    return parser.parse_args(arguments)


def list_input_devices() -> list[tuple[int, str]]:
    """Return available input devices with their SoundDevice indexes.

    Returns:
        Input-device indexes and names available to the current macOS user.
    """
    devices = sd.query_devices()
    return [
        (index, device["name"])
        for index, device in enumerate(devices)
        if device["max_input_channels"] > 0
    ]


def print_input_devices() -> None:
    """Print audio input devices in a format suitable for command-line selection."""
    for index, name in list_input_devices():
        print(f"{index}: {name}")


def write_wav(audio: np.ndarray, output_path: Path) -> None:
    """Write a floating-point waveform as mono 16-bit PCM WAV audio.

    Args:
        audio: Waveform samples in the conventional -1.0 to 1.0 range.
        output_path: Destination WAV file.
    """
    pcm_audio = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    # `wave.open(..., "wb")` returns Wave_write at runtime; Pylint infers its
    # wider read/write union and cannot resolve the write-only methods.
    # pylint: disable=no-member
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm_audio.tobytes())
    # pylint: enable=no-member


def record_audio(duration: float, device: str | None, output_path: Path) -> Path:
    """Record mono microphone audio and save it as a 16 kHz WAV file.

    Args:
        duration: Recording length in seconds. It must be positive.
        device: Optional SoundDevice input device ID or name.
        output_path: Destination WAV file.

    Returns:
        The saved WAV path.

    Raises:
        ValueError: If duration is not positive.
        sounddevice.PortAudioError: If the selected input device cannot record.
    """
    if duration <= 0:
        raise ValueError("Recording duration must be greater than zero.")

    input_device: int | str | None = (
        int(device) if device is not None and device.isdecimal() else device
    )
    frame_count = int(duration * SAMPLE_RATE)
    print(f"Recording for {duration:.1f} seconds. Speak now...")
    audio = sd.rec(
        frame_count,
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        device=input_device,
    )
    sd.wait()
    write_wav(audio, output_path)
    return output_path


def build_transcription_settings(
    settings: argparse.Namespace, recording_path: Path
) -> argparse.Namespace:
    """Adapt recording settings to the shared MLX Audio transcription interface.

    Args:
        settings: Parsed recording-demo settings.
        recording_path: WAV file created by the recording phase.

    Returns:
        Settings accepted by the shared transcription command builder.
    """
    arguments = [
        str(recording_path),
        "--language",
        settings.language,
        "--output-dir",
        str(settings.output_dir),
        "--format",
        settings.format,
    ]
    if settings.max_parallel_segments is not None:
        arguments.extend(
            ["--max-parallel-segments", str(settings.max_parallel_segments)]
        )
    if settings.verbose:
        arguments.append("--verbose")
    return parse_transcribe_arguments(arguments)


def run_demo(settings: argparse.Namespace) -> tuple[Path, Path]:
    """Record audio and run a local Cohere Transcribe inference.

    Args:
        settings: Parsed recording-demo settings.

    Returns:
        Paths to the recorded WAV file and generated transcript.

    Raises:
        ValueError: If the recording duration is invalid.
        subprocess.CalledProcessError: If mlx-audio transcription fails.
    """
    output_dir = settings.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    recording_name = settings.recording_name or datetime.now().strftime(
        "recording_%Y%m%d_%H%M%S"
    )
    recording_path = output_dir / f"{recording_name}.wav"
    record_audio(settings.duration, settings.device, recording_path)

    transcription_settings = build_transcription_settings(settings, recording_path)
    output_stem = output_dir / recording_path.stem
    subprocess.run(build_command(transcription_settings, output_stem), check=True)
    return recording_path, output_stem.with_suffix(f".{settings.format}")


def main() -> None:
    """Run the recording and transcription command-line demo."""
    settings = parse_arguments()
    if settings.list_devices:
        print_input_devices()
        return

    recording_path, transcript_path = run_demo(settings)
    print(f"Recording saved to: {recording_path}")
    print(f"Transcript saved to: {transcript_path}")


if __name__ == "__main__":
    main()
