# macOS demos: Cohere Transcribe with MLX Audio

This demo runs the original, non-quantized `CohereLabs/cohere-transcribe-03-2026` checkpoint locally on an Apple Silicon Mac through `mlx-audio`. It is an offline batch-transcription demo: after the model is downloaded, transcription does not send audio to an external service.

## Prerequisites

* macOS on Apple Silicon with Metal available.
* The `cohere-voice` Conda environment.
* Access approval for the gated Cohere model on Hugging Face, followed by `hf auth login` in the same user account.
* Enough unified memory for the 2B-parameter BF16 model and the audio workload. Begin with short audio files.

Install the pinned runtime from the repository root:

```bash
conda activate cohere-voice
python -m pip install -r macos/requirements.txt
```

`sentencepiece` is installed alongside `mlx-audio` because it is required to load the Cohere Transcribe tokenizer.

Download the official Cohere BF16 model before the first transcription:

```bash
hf download CohereLabs/cohere-transcribe-03-2026
```

See the repository-level [MLX Audio guide](../MLX_AUDIO.md) for how this checkpoint is loaded by `mlx-audio`.

## Available demos

* [Demo 01: record and transcribe](demo01/README.md) records from the macOS input device (including a Bose headset selected as the system input), then transcribes the resulting WAV file.
* [WER test](wer-test/README.md) evaluates sample WER on a language-specific Hugging Face dataset from a Jupyter notebook.
* `transcribe.py` is the shared command-line component for transcribing an existing audio file.

## Transcribe an existing audio file

```bash
python -m macos.transcribe path/to/audio.wav --language it --output-dir macos/output
```

The default model is the Cohere BF16 checkpoint and the default output is a UTF-8 text file. The first invocation downloads model artefacts into the Hugging Face cache. The generated file for the example above is `macos/output/audio.txt`.

Use JSON, SRT, or VTT output when needed:

```bash
python -m macos.transcribe path/to/audio.m4a --language en --format json
```

For long audio, leave segment parallelism automatic initially. If memory pressure occurs, lower the concurrency explicitly:

```bash
python -m macos.transcribe path/to/audio.wav --language it --max-parallel-segments 1
```

## Notes

* The model expects 16 kHz mono audio internally; `mlx-audio` performs audio loading and preprocessing.
* `--language` should be one of the languages supported by the Cohere model. Specify it explicitly rather than relying on language detection.
* Do not commit downloaded model files, Hugging Face credentials, source recordings, or generated transcripts.
