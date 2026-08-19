# Demo 02: local Next.js recording UI

## Purpose

Provide a macOS-only graphical demonstration that records audio from a browser-selected
input device and transcribes it locally with the non-quantized
`CohereLabs/cohere-transcribe-03-2026` model through `mlx-audio`.

## Architecture

The demo has two separate local processes:

```text
Browser -> Next.js frontend and route handler -> FastAPI ASR backend -> mlx-audio / MLX
```

* The Next.js frontend owns device enumeration, microphone permission, recording, and
  presentation of the transcript.
* The Next.js route handler proxies the audio upload to the local FastAPI backend. The
  browser therefore never needs to access the backend origin directly.
* The FastAPI backend is launched with the `cohere-voice` Conda environment. It loads
  the ASR model lazily once and retains it in process memory for later requests.
* Temporary uploaded audio is removed once each transcription request completes.

No audio or transcript is uploaded to a remote service after model files have been
downloaded from Hugging Face.

## Functional requirements

1. The UI must show a sidebar with the active ASR model. The default is the official
   Cohere checkpoint.
2. The UI must enumerate browser-visible audio-input devices after microphone access
   has been granted and allow one of them to be selected.
3. The sidebar must provide a language listbox. Italian (`it`) is the default and the
   available choices are English (`en`), French (`fr`), Arabic (`ar`), and Dutch (`nl`).
4. The UI must provide a start-recording control and a stop-recording control.
5. Stopping the recording must upload the captured audio and automatically start ASR.
6. The central view must show clear recording/transcribing/error states and present
   the completed transcript in an editable text area.
7. The backend must expose `GET /health`, `GET /models`, and `POST /transcribe`.
8. `POST /transcribe` must accept a multipart `audio` file plus an optional language,
   reject absent, empty, unsupported, or oversized uploads with a clear client error,
   and return the transcript, model ID, language, and audio filename.
9. The backend default model, language, maximum tokens, and maximum upload size must
   be configurable through documented environment variables.

## Non-functional requirements

* Runs only on Apple Silicon macOS because MLX and Metal are required.
* The initial model load can take time; later requests reuse the in-memory model.
* Browser-recorded WebM, MP4/M4A, OGG, WAV, and MPEG audio are accepted. FFmpeg must be
  available in the active Conda environment for the compressed browser formats; when it
  is absent, the backend must return the macOS Conda installation command clearly.
* Unit tests must mock model loading and inference. They must not download model files
  or require Metal.

## Acceptance checks

* `pytest macos/demo02/backend/tests` passes in the `cohere-voice` environment.
* `black --check macos/demo02/backend` and `pylint macos/demo02/backend/app` pass.
* `npm run check` and `npm run build` pass in `macos/demo02/frontend` after its
  dependencies have been installed.
* A user can select an input device, make a short recording, stop it, and see the
  Cohere transcript in the UI when both local services are running.
