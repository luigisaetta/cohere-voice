# Cohere Voice

[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Pylint](https://img.shields.io/badge/linting-pylint-4B8BBE.svg)](https://pylint.readthedocs.io/)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![Python >= 3.11](https://img.shields.io/badge/python-%3E%3D3.11-3776AB.svg)](https://www.python.org/)

`cohere-voice` is an experimental workspace for evaluating and building local automatic speech recognition (ASR) demonstrations around Cohere models distributed through Hugging Face. The initial focus is [Cohere Transcribe 03-2026](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026).

It contains reproducible macOS examples for microphone recording, a browser-based Next.js UI, WER evaluation, and integration through MLX Audio's OpenAI-compatible local API. After model artefacts have been downloaded, recordings are processed locally on Apple Silicon; no audio is sent to a cloud transcription service. The project is intended for prototyping and technical evaluation rather than as a production-ready speech service.

## Goals

* Evaluate the model on representative, non-sensitive audio samples.
* Create clear local demos for audio transcription workflows.
* Document model, audio, runtime, and decoding assumptions so results can be reproduced.
* Establish testable building blocks for future integrations.

## What you can try

* Record from a macOS microphone or headset and transcribe locally with Cohere Transcribe.
* Use the browser UI to select an input device, language, and either Cohere Transcribe or Qwen3-ASR.
* Measure sampled WER on the public Hugging Face FLEURS dataset from a Jupyter notebook.
* Send recordings through MLX Audio's local OpenAI-compatible transcription API.

## Current scope

The working examples currently target **Apple Silicon macOS** because they run through
MLX and Metal. Node.js 20.9 or later is required only for the Demo 02 browser UI, and
FFmpeg is required for browser-recorded WebM or M4A/MP4 audio. The Linux folder is a
placeholder for future work, not a runnable demo.

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

## Quick start: Demo 02 browser UI

Demo 02 is the fastest way to try local transcription with a graphical interface. Install
the macOS runtime and download the gated Cohere model first:

```bash
conda activate cohere-voice
python -m pip install -r macos/requirements.txt
conda install -n cohere-voice -c conda-forge ffmpeg
hf auth login
hf download CohereLabs/cohere-transcribe-03-2026
```

Start the local MLX Audio API in one terminal:

```bash
conda activate cohere-voice
./macos/demo02/backend/start_server.sh
```

In a second terminal, start the Next.js interface and open `http://localhost:3000`:

```bash
cd macos/demo02/frontend
npm install
npm run dev
```

See [Demo 02](macos/demo02/README.md) for browser microphone permissions, supported
languages, model selection, and configuration.

## Download the model

The Cohere checkpoint is gated on Hugging Face. First accept the model's access conditions on its [model card](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026), then authenticate and download the non-quantized BF16 checkpoint from the command line:

```bash
conda activate cohere-voice
python -m pip install -r macos/requirements.txt  # Apple Silicon demos
hf auth login
hf download CohereLabs/cohere-transcribe-03-2026
```

The model weights and supporting files are stored in the local Hugging Face cache. The checkpoint includes roughly 4 GB of weights; do not commit model artefacts, Hugging Face access tokens, private recordings, transcripts containing personal data, or runtime caches.

This is the official Cohere BF16 checkpoint, not a community-converted `*-mlx` repository and not a quantized variant. It is nevertheless supported directly by `mlx-audio`, which runs it locally through MLX and Metal on Apple Silicon.

For the complete runtime architecture and how the examples invoke `mlx-audio`, see [MLX_AUDIO.md](MLX_AUDIO.md).

## Model licence and permitted use

According to the [official model card](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026), Cohere Transcribe is licensed under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), which permits commercial use, modification, and redistribution subject to its notice and licence requirements. Model access remains gated on Hugging Face, so review and accept the current access conditions before downloading it.

The model licence does not replace obligations that apply to the audio and transcripts you process. In particular, commercial voice workloads should account for consent, privacy, data-protection, and other applicable legal requirements.

## Platform demos

The table below is the growing catalogue of repository examples. Each entry links to
its dedicated folder, which contains the prerequisites and detailed instructions.

| Platform | Example | What it demonstrates | Entry point | Documentation |
| --- | --- | --- | --- | --- |
| macOS / Apple Silicon | Demo 01 — record and transcribe | Records Italian audio from a selected macOS input device, such as a Bose QC35 II headset, then transcribes it locally with the non-quantized Cohere checkpoint through `mlx-audio`. | [`record_and_transcribe.py`](macos/demo01/record_and_transcribe.py) | [Demo 01 folder](macos/demo01/) |
| macOS / Apple Silicon | Demo 02 — local recording UI | Provides a browser microphone interface with device selection, start/stop recording, and a transcript text area. The Next.js frontend proxies recordings to MLX Audio's OpenAI-compatible local API. | [Next.js UI](macos/demo02/frontend/app/page.tsx) | [Demo 02 folder](macos/demo02/) |
| macOS / Apple Silicon | WER test | Downloads a deterministic Italian sample from Hugging Face FLEURS, runs local Cohere Transcribe inference, and calculates Word Error Rate (WER) against the dataset references. | [`wer_evaluation.ipynb`](macos/wer-test/wer_evaluation.ipynb) | [WER test folder](macos/wer-test/) |
| Linux | Planned demos | Reserved for future Linux-specific implementations; not yet runnable. | — | [Linux folder](linux/) |

See [the MLX Audio guide](MLX_AUDIO.md) for the shared macOS runtime architecture.

## Run Demo 01 on macOS

After selecting the desired microphone as the macOS input device, record and transcribe 10 seconds of Italian audio with:

```bash
conda activate cohere-voice
python -m macos.demo01.record_and_transcribe --duration 10 --language it
```

To list devices or use a Bose QC35 II explicitly:

```bash
python -m macos.demo01.record_and_transcribe --list-devices
python -m macos.demo01.record_and_transcribe \
  --device "Bose QC35 II" \
  --duration 10 \
  --language it
```

See the [Demo 01 guide](macos/demo01/README.md) for output formats and additional options.

## Project conventions

* Python 3.11 or later is required.
* Documentation and source-code comments are written in English.
* Unit tests should mock model downloads and inference; tests that run a real model must be clearly marked as integration tests.
* Use small synthetic or openly licensed audio samples only.

See [AGENTS.md](AGENTS.md) for the complete development and contribution rules.

## Citation

If you use this project or its macOS examples, please cite MLX Audio:

```bibtex
@misc{mlx-audio,
  author = {Canuma, Prince},
  title = {MLX Audio},
  year = {2025},
  howpublished = {\url{https://github.com/Blaizzy/mlx-audio}},
  note = {Audio processing library for Apple Silicon with TTS, STT, and STS capabilities.}
}
```
