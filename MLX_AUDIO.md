# Using Cohere Transcribe with MLX Audio

This guide explains how the macOS examples run the official Cohere Transcribe checkpoint locally through [`mlx-audio`](https://github.com/Blaizzy/mlx-audio).

## What is loaded

The examples use the official non-quantized model repository:

```text
CohereLabs/cohere-transcribe-03-2026
```

It is the original Cohere BF16 checkpoint, including `model.safetensors`; it is not a community-converted `*-mlx` repository and it is not a 4-bit or 8-bit variant. `mlx-audio` has support for Cohere ASR and loads this model locally through Apple MLX and Metal on Apple Silicon.

The model is gated on Hugging Face. Accept access on the [model card](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026), then authenticate and download it before running a demo:

```bash
conda activate cohere-voice
hf auth login
hf download CohereLabs/cohere-transcribe-03-2026
```

The download is stored in the Hugging Face cache, outside the repository. The model weights occupy roughly 4 GB. Once cached, inference is local: the examples do not send audio to an external transcription service.

## Runtime setup

On an Apple Silicon Mac, install the macOS runtime dependencies in the repository Conda environment:

```bash
conda activate cohere-voice
python -m pip install -r macos/requirements.txt
```

`mlx-audio` provides the MLX/Metal ASR runtime. `sentencepiece` is required by its Cohere tokenizer implementation.

## How the examples use MLX Audio

The repository keeps application workflow separate from the ASR runtime:

```text
microphone or audio file
        |
        v
macos.demo01.record_and_transcribe / macos.transcribe
        |
        v
python -m mlx_audio.stt.generate
        |
        v
CohereLabs/cohere-transcribe-03-2026 on MLX + Metal
        |
        v
text, JSON, SRT, or VTT transcript
```

`macos/transcribe.py` is the shared command-line adapter. It validates the source audio, builds a command for `mlx_audio.stt.generate`, and requests the Cohere model by its official Hugging Face ID. It passes the language, output format, output location, maximum token count, and optional segment concurrency to `mlx-audio`.

`macos/demo01/record_and_transcribe.py` adds the microphone workflow. It records the selected macOS input device with `sounddevice`, writes a 16 kHz mono 16-bit WAV file, then calls the same shared adapter. The default input is the macOS system input; select the Bose QC35 II there or specify its name/index with `--device`.

## Run the demos

Transcribe an existing audio file:

```bash
python -m macos.transcribe path/to/audio.wav --language it --output-dir macos/output
```

Record and transcribe ten seconds from the default macOS input:

```bash
python -m macos.demo01.record_and_transcribe --duration 10 --language it
```

List available input devices, then select the Bose headset explicitly if necessary:

```bash
python -m macos.demo01.record_and_transcribe --list-devices
python -m macos.demo01.record_and_transcribe \
  --device "Bose QC35 II" \
  --duration 10 \
  --language it
```

See [macos/README.md](macos/README.md) for the macOS runtime and [macos/demo01/README.md](macos/demo01/README.md) for recording options and output details.

For sample-based WER measurement, use the [macOS WER test notebook](macos/wer-test/README.md). It loads a language-specific FLEURS sample from Hugging Face, uses the same local MLX runtime, and compares hypotheses with the dataset references.

## Operational notes

* Apple Silicon and a Metal-capable macOS session are required for this runtime.
* The official model is large; start with short recordings and reduce `--max-parallel-segments` to `1` if unified-memory pressure occurs.
* Specify `--language` explicitly. The examples default to Italian (`it`).
* Do not commit Hugging Face credentials, model caches, WAV recordings, or generated transcripts.
