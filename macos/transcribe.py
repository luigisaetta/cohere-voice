"""
Author: L. Saetta
Date last modified: 2026-08-18
License: MIT
Description: Runs local Cohere Transcribe ASR inference through mlx-audio on macOS.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

DEFAULT_MODEL = "CohereLabs/cohere-transcribe-03-2026"
OUTPUT_FORMATS = ("txt", "json", "srt", "vtt")


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command-line arguments for a local transcription.

    Args:
        arguments: Optional argument sequence. When omitted, arguments are read
            from the command line.

    Returns:
        Parsed transcription settings.
    """
    parser = argparse.ArgumentParser(
        description="Transcribe local audio with Cohere Transcribe through MLX Audio."
    )
    parser.add_argument("audio", type=Path, help="Path to the source audio file.")
    parser.add_argument(
        "--language",
        default="it",
        help="Cohere Transcribe language code, for example it, en, fr, or de.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory where the transcript is saved (default: output).",
    )
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default="txt",
        help="Transcript format (default: txt).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Hugging Face model ID or local model path.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8192,
        help="Maximum number of transcript tokens to generate.",
    )
    parser.add_argument(
        "--max-parallel-segments",
        type=int,
        help="Maximum audio segments processed concurrently; omit for automatic sizing.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed runtime information from mlx-audio.",
    )
    return parser.parse_args(arguments)


def build_command(settings: argparse.Namespace, output_stem: Path) -> list[str]:
    """Build the mlx-audio command for the requested transcription.

    Args:
        settings: Parsed transcription settings.
        output_stem: Destination path without the output-file extension.

    Returns:
        Command ready to run in the active Python environment.
    """
    command = [
        sys.executable,
        "-m",
        "mlx_audio.stt.generate",
        "--model",
        settings.model,
        "--audio",
        str(settings.audio),
        "--output-path",
        str(output_stem),
        "--format",
        settings.format,
        "--language",
        settings.language,
        "--max-tokens",
        str(settings.max_tokens),
    ]
    if settings.max_parallel_segments is not None:
        command.extend(["--max-parallel-segments", str(settings.max_parallel_segments)])
    if settings.verbose:
        command.append("--verbose")
    return command


def transcribe(settings: argparse.Namespace) -> Path:
    """Validate input audio and run MLX Audio transcription.

    Args:
        settings: Parsed transcription settings.

    Returns:
        Path to the generated transcript.

    Raises:
        FileNotFoundError: If the requested source audio does not exist.
        subprocess.CalledProcessError: If mlx-audio fails to transcribe the audio.
    """
    audio_path = settings.audio.expanduser().resolve()
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_dir = settings.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_stem = output_dir / audio_path.stem
    settings.audio = audio_path

    subprocess.run(build_command(settings, output_stem), check=True)
    return output_stem.with_suffix(f".{settings.format}")


def main() -> None:
    """Run the command-line transcription demo."""
    settings = parse_arguments()
    transcript_path = transcribe(settings)
    print(f"Transcript saved to: {transcript_path}")


if __name__ == "__main__":
    main()
