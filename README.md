# Cohere Voice

[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Pylint](https://img.shields.io/badge/linting-pylint-4B8BBE.svg)](https://pylint.readthedocs.io/)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![Python >= 3.11](https://img.shields.io/badge/python-%3E%3D3.11-3776AB.svg)](https://www.python.org/)

`cohere-voice` is an experimental workspace for evaluating and building demonstrations around Cohere's automatic speech recognition (ASR) models distributed through Hugging Face. The initial focus is [Cohere Transcribe 03-2026](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026).

The project will contain small, reproducible examples that make it easy to understand the complete transcription path: loading a model, preparing audio, running inference, and handling the resulting transcript. It is intended for prototyping and technical evaluation rather than as a production-ready speech service.

## Goals

* Evaluate the model on representative, non-sensitive audio samples.
* Create clear local demos for audio transcription workflows.
* Document model, audio, runtime, and decoding assumptions so results can be reproduced.
* Establish testable building blocks for future integrations.

## Getting started

Use the repository's Conda environment:

```bash
conda activate cohere-voice
```

The development-quality tools are available in this environment:

```bash
black --check .
pylint .
pytest
```

Install model-specific dependencies and follow the model-card guidance when adding a demo. Do not commit Hugging Face access tokens, private recordings, transcripts containing personal data, downloaded model artefacts, or runtime caches.

## Platform demos

* [macOS / Apple Silicon](macos/README.md): local transcription with `mlx-audio` and the non-quantized Cohere checkpoint, including [Demo 01](macos/demo01/README.md) for microphone recording followed by transcription.
* [Linux](linux/README.md): reserved for the Linux-specific implementation.

## Project conventions

* Python 3.11 or later is required.
* Documentation and source-code comments are written in English.
* Unit tests should mock model downloads and inference; tests that run a real model must be clearly marked as integration tests.
* Use small synthetic or openly licensed audio samples only.

See [AGENTS.md](AGENTS.md) for the complete development and contribution rules.
