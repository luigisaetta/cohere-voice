# AGENTS.md

This repository contains experiments, demos, and implementation guidance for Cohere's automatic speech recognition (ASR) models from Hugging Face, initially centred on [`CohereLabs/cohere-transcribe-03-2026`](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026).

## Repository purpose

Keep the repository focused on evaluating, demonstrating, and developing practical integrations for Cohere ASR models. Examples should make transcription behaviour, model configuration, input-audio assumptions, and output handling clear and reproducible.

Avoid unrelated AI demos, frameworks, deployment targets, or abstractions unless explicitly required by the requested work.

## Language and documentation

* All documentation, source-code comments, and Markdown files must be written in English.
* Keep documentation practical, accurate, and aligned with the implementation.
* Document prerequisites, model identifiers and revisions, audio formats, runtime requirements, configuration, and expected output for each demo.
* Do not claim model capabilities, language support, performance, licence terms, or configuration options unless verified by the implementation or authoritative Cohere/Hugging Face documentation.
* Never include real speech recordings or transcripts containing sensitive or personally identifiable information in the repository.

## Codex working rules

When working in this repository, Codex should:

* Inspect the existing project structure before editing.
* Prefer small, coherent changes over broad rewrites.
* Reuse existing modules, helpers, configuration patterns, and test fixtures before adding new ones.
* Preserve user changes already present in the working tree.
* Avoid speculative changes that are not requested by the user.
* Do not create commits unless explicitly asked.
* Do not add production dependencies without a clear reason.
* Do not run destructive commands or discard existing changes unless explicitly requested.
* Do not hard-code Hugging Face tokens, API keys, credentials, private URLs, local machine paths, or personally identifiable data.
* Use environment variables and `.env` files excluded from version control for secrets; document required variable names and safe placeholder values.
* When uncertain, document the assumption, leave a clear TODO, or ask for clarification.

## Python environment

Use the `cohere-voice` Conda environment for local development, examples, and tests.

If an environment definition exists, prefer it for setup. Activate `cohere-voice` before running checks, and do not assume globally installed Python packages are available.

## Python code conventions

Every Python source file must start with a multiline header using this format:

```python
"""
Author: L. Saetta
Date last modified: YYYY-MM-DD
License: MIT
Description: Brief description of the responsibilities and functions contained in this file.
"""
```

Use the actual modification date when creating or updating a Python source file.

All generated Python code must include accurate docstrings for modules, classes, methods, and functions where applicable. Use Google-style Python docstrings, describing purpose, arguments, return values, raised exceptions, and relevant side effects.

## ASR design expectations

* Keep model loading, audio decoding/preprocessing, inference, and output formatting separated where practical.
* Make audio assumptions explicit: supported formats, sample rate, channels, bit depth where relevant, and resampling or normalization behaviour.
* Pin and document the exact Hugging Face model identifier and revision whenever reproducibility matters.
* Design examples to run without network access after model artefacts have been downloaded, where feasible.
* Handle malformed, empty, unsupported, or excessively long audio inputs with clear errors.
* Keep inference examples deterministic and easy to test; make decoding parameters visible.
* Do not silently upload local audio, transcripts, or credentials to external services.

## Testing expectations

New behaviour should include appropriate automated tests using the project-standard framework.

Tests should cover configuration loading, audio-input validation, preprocessing boundaries, successful transcription flow, output formatting, and error handling. Mock model downloads and inference in unit tests; real model execution should be clearly marked as an optional integration test.

Use small synthetic or openly licensed test audio only. Do not commit large model artefacts, generated caches, or private audio samples.

## Required checks

Run relevant formatting, linting, and test commands before considering work complete. Use the project-standard tools when they exist; otherwise prefer `black`, `pylint`, and `pytest` for Python projects.

If a check cannot be run because the Conda environment, model artefacts, or dependencies are missing, state this clearly in the final summary.

## Dependency policy

Before adding a dependency, check whether the repository or standard library already provides an equivalent. Add any necessary dependency to the appropriate environment or requirements file, explain why it is needed, and update setup documentation when installation changes.

Do not introduce new frameworks unless required by the requested work.

## Definition of done

A change is done only when:

* The implementation is scoped to the repository purpose.
* Relevant tests and checks have been considered and run where available.
* Documentation and setup instructions reflect changed behaviour.
* Model, audio, and configuration assumptions are explicit.
* Any inability to run checks has been clearly documented.
