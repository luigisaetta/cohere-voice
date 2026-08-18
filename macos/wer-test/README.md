# WER test: Cohere Transcribe on FLEURS

This demo measures the word error rate (WER) of the official non-quantized Cohere Transcribe checkpoint through `mlx-audio` on Apple Silicon. The evaluation notebook downloads a deterministic sample from the public [`google/fleurs`](https://huggingface.co/datasets/google/fleurs) dataset, transcribes it locally, compares each hypothesis with the dataset reference, and calculates corpus WER.

The default configuration is Italian: `it` for Cohere Transcribe and `it_it` for FLEURS. It uses the `test` split and 100 samples. FLEURS provides normalized transcripts in its `transcription` field and 16 kHz audio, making it suitable for this small, reproducible ASR evaluation.

## Setup

Complete the [macOS runtime setup](../README.md), including Hugging Face authentication and the official Cohere model download. Then install the notebook and evaluation dependencies:

```bash
conda activate cohere-voice
python -m pip install -r macos/requirements.txt
python -m ipykernel install --user --name cohere-voice --display-name "Python (cohere-voice)"
```

Start Jupyter from the repository root:

```bash
jupyter lab
```

Open `macos/wer-test/wer_evaluation.ipynb` and select the `cohere-voice` kernel. Run all cells in order.

## What the notebook does

1. Sets the language, dataset split, sample size, random seed, and MLX batch size.
2. Streams only the selected FLEURS language configuration from the Hugging Face Hub and draws a deterministic sample.
3. Loads `CohereLabs/cohere-transcribe-03-2026` once through `mlx-audio`.
4. Transcribes the samples locally with MLX and Metal.
5. Normalizes reference and hypothesis text equally, then calculates corpus and per-sample WER with `jiwer`.
6. Displays a results table and writes timestamped CSV and JSON results under `macos/wer-test/output/`.

The notebook records individual inference failures and excludes only failed rows from the aggregate WER. It reports the count, so the result remains auditable.

## Change the evaluation

Edit the first settings cell in the notebook:

```python
LANGUAGE = "it"
SAMPLE_SIZE = 100
SEED = 42
BATCH_SIZE = 1
```

The supported language codes are `ar`, `de`, `el`, `en`, `es`, `fr`, `it`, `ja`, `ko`, `nl`, `pl`, `pt`, `vi`, and `zh`. The notebook maps each code to its FLEURS configuration. Begin with batch size `1`; increase it only after confirming that the Mac has sufficient unified memory.

## Interpreting results

WER is a word-level edit-distance ratio after Unicode normalization, lowercasing, punctuation removal, and whitespace collapse. Lower is better; `0.0` indicates an exact match after this normalization.

This is a sample-based local measurement, not a full benchmark or a claim of official performance. Keep the output files for the configuration, selected dataset records, reference text, hypothesis text, and failure information. Do not commit those output files.
