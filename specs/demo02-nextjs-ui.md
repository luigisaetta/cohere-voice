# Demo 02: local Next.js recording UI

## Purpose

Provide a macOS-only graphical demonstration that records audio from a browser-selected
input device and transcribes it locally with the non-quantized
`CohereLabs/cohere-transcribe-03-2026` model through `mlx-audio`.

## Architecture

The demo has two separate local processes:

```text
Browser -> Next.js frontend and route handler -> MLX Audio OpenAI-compatible API -> MLX
```

* The Next.js frontend owns device enumeration, microphone permission, recording, and
  presentation of the transcript.
* The Next.js route handler proxies the audio upload to the local MLX Audio API server.
  The browser therefore never needs to access the backend origin directly.
* The MLX Audio server is launched with the `cohere-voice` Conda environment. It uses
  the project's upstream OpenAI-compatible `POST /v1/audio/transcriptions` endpoint.
* The Next.js route handler maps the browser's `audio` field to the OpenAI-compatible
  `file` field and supplies the configured model, language, `max_tokens`, and JSON
  response format.

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
7. The integration must use the MLX Audio OpenAI-compatible
   `POST /v1/audio/transcriptions` endpoint and its `GET /v1/models` model-management
   endpoint. No project-owned FastAPI application is required.
8. The route handler must translate the completed OpenAI-compatible JSON response into
   the UI's transcript, model ID, language, and filename response.
9. The MLX Audio URL, model ID, and maximum token count must be configurable through
   documented environment variables.

## Non-functional requirements

* Runs only on Apple Silicon macOS because MLX and Metal are required.
* The initial model load can take time; later requests reuse the in-memory model.
* Browser-recorded WebM, MP4/M4A, OGG, WAV, and MPEG audio are accepted. FFmpeg must be
  available in the active Conda environment for the compressed browser formats.
* Tests must not download model files or require Metal. The frontend must type-check
  and build against the OpenAI-compatible proxy contract.

## Acceptance checks

* `npm run check` and `npm run build` pass in `macos/demo02/frontend` after its
  dependencies have been installed.
* A user can select an input device, make a short recording, stop it, and see the
  Cohere transcript in the UI when the Next.js app and the local MLX Audio server run.
