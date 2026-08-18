# Demo 01: record and transcribe on macOS

`demo01` is an end-to-end local ASR demo for Apple Silicon. It records from the macOS input device, writes a 16 kHz mono WAV file, then transcribes it with the original non-quantized Cohere Transcribe model through `mlx-audio`.

## Setup

Follow the runtime setup in the [parent macOS guide](../README.md). Before the first transcription, accept access to the gated Cohere model on Hugging Face, authenticate, and download the official BF16 checkpoint:

```bash
conda activate cohere-voice
hf auth login
hf download CohereLabs/cohere-transcribe-03-2026
```

To use Bose headphones, first select the Bose microphone as the Mac's input in **System Settings → Sound → Input**. The demo then uses it automatically when no `--device` option is provided.

List input devices visible to the active user:

```bash
python -m macos.demo01.record_and_transcribe --list-devices
```

If Bose is listed, pass its index or device name explicitly when required:

```bash
python -m macos.demo01.record_and_transcribe --device 2 --duration 8 --language it
```

## Run the demo

Record for 10 seconds from the default macOS input and produce a transcript:

```bash
python -m macos.demo01.record_and_transcribe --duration 10 --language it
```

The recording and transcript are written under `macos/demo01/output/`, using a timestamped filename. To choose a stable filename or request JSON output:

```bash
python -m macos.demo01.record_and_transcribe \
  --device "Bose QC35 II" \
  --duration 15 \
  --language it \
  --recording-name bose-test \
  --format json
```

Audio remains local after model download; do not commit the generated WAV files or transcripts. See the repository-level [MLX Audio guide](../../MLX_AUDIO.md) for the complete model-loading flow.
