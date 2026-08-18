# Specification: macOS WER evaluation notebook

## Purpose

Provide a reproducible Jupyter notebook that measures the word error rate (WER) of the official non-quantized `CohereLabs/cohere-transcribe-03-2026` checkpoint on a language-specific speech dataset from the Hugging Face Hub, using `mlx-audio` on Apple Silicon.

The first implementation is located at `macos/wer-test/` and uses the `google/fleurs` dataset. Its default configuration is Italian (`it_it`) and its default split is `test`.

## Scope

The notebook must:

1. Define editable settings for the Cohere model ID, language (default `it`), FLEURS configuration, split (default `test`), sample size (default `100`), random seed, and batch size.
2. Map Cohere language codes to their corresponding FLEURS language configurations, including Italian (`it` → `it_it`).
3. Load only the selected dataset configuration and sample records through Hugging Face Datasets streaming mode.
4. Select a deterministic shuffled sample using the configured seed.
5. Load the Cohere model once through `mlx-audio` and run all inference locally through MLX and Metal.
6. Transcribe each selected sample with the configured language.
7. Compare normalized reference and hypothesis text, calculate corpus WER using `jiwer`, and display a per-sample results table plus an aggregate summary.
8. Save the detailed results and summary as CSV and JSON files under `macos/wer-test/output/`.

## Data and metric behaviour

* Dataset: `google/fleurs` from the Hugging Face Hub.
* Reference field: `transcription`, the dataset's normalized transcript field.
* Audio field: `audio`, passed to the loaded MLX model as a waveform and its original sample rate.
* The notebook normalizes both references and hypotheses consistently before scoring: Unicode normalization, lowercasing, punctuation removal, and whitespace collapse.
* WER is reported as the standard word-level edit-distance ratio. The notebook must retain original, unnormalized reference and hypothesis strings in its detailed output for auditability.
* The notebook must make clear that this is a sample estimate, not a benchmark result for the full dataset.

## Dependencies and runtime

* Python 3.11 or later in the `cohere-voice` Conda environment.
* Apple Silicon with Metal available.
* Existing macOS runtime requirements: `mlx-audio` and `sentencepiece`.
* New evaluation requirements: `jupyterlab`, `ipykernel`, `datasets`, `jiwer`, and `pandas`.
* Register the environment as the `cohere-voice` Jupyter kernel before opening the notebook.
* Hugging Face authentication is required for the gated Cohere model. The selected FLEURS subset is public.

## Error handling

* Reject unknown language codes before dataset loading.
* Reject a non-positive sample size or batch size.
* Record per-sample inference failures in the detailed output and exclude those records from the aggregate WER, reporting the failure count.
* Fail clearly when no successful transcripts are available for WER computation.

## Acceptance criteria

* `macos/wer-test/wer_evaluation.ipynb` can be launched in Jupyter using the `cohere-voice` kernel.
* Default settings target `google/fleurs`, `it_it`, the `test` split, and 100 records.
* A successful run loads the model once, produces hypotheses, calculates WER, and writes a timestamped CSV plus JSON summary under the ignored output directory.
* The notebook never uploads source audio or transcripts to an external inference service.
* Unit tests cover text normalization, WER calculation, language configuration selection, and invalid configuration handling without downloading a model or dataset.
* Documentation explains setup, expected runtime characteristics, results, limitations, and how to change language and sample size.
