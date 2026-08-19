# Demo 02: local recording UI with Next.js

`demo02` provides a graphical, local-only transcription workflow for Apple Silicon
macOS. A Next.js interface lets the user grant microphone access, select a browser-visible
input device, record audio, and read or edit the resulting transcript. A separate FastAPI
backend runs `mlx-audio` in the `cohere-voice` Conda environment and invokes the official,
non-quantized `CohereLabs/cohere-transcribe-03-2026` checkpoint.

## Architecture

```text
Browser microphone -> Next.js UI -> Next.js /api/transcribe proxy -> FastAPI -> mlx-audio / MLX
```

The browser is responsible only for device selection and recording. The Next.js route
handler forwards the audio to the FastAPI process, so the browser never contacts the
Python server directly and no CORS configuration is required. The Python process loads
the model lazily at its first transcription and reuses it for subsequent requests.

After model artefacts are downloaded from Hugging Face, audio and transcripts stay on the
Mac. Each backend upload is stored in a temporary file only for the duration of inference
and is deleted before the HTTP response is returned.

## Prerequisites

* Apple Silicon macOS with Metal available.
* Conda environment `cohere-voice`.
* Node.js 20.9 or later and npm.
* Browser microphone permission. Chrome and Safari can expose different audio formats;
  the backend accepts browser-recorded WebM, MP4/M4A, OGG, WAV, and MPEG files.
* Access approval for Cohere's gated model, Hugging Face authentication, and a local
  model download as documented in the [parent macOS guide](../README.md).

Install the Python runtime from the repository root:

```bash
conda activate cohere-voice
python -m pip install -r macos/requirements.txt
```

Install the frontend dependencies once:

```bash
cd macos/demo02/frontend
npm install
```

## Run the demo

Use two terminals from the repository root.

Terminal 1 starts the Python ASR backend in the Conda environment:

```bash
conda activate cohere-voice
uvicorn macos.demo02.backend.app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2 starts the Next.js frontend:

```bash
cd macos/demo02/frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Select **Refresh** in the sidebar
to grant browser microphone permission and populate the input-device list. Choose the
desired microphone, press **Start recording**, then **Stop recording**. The UI sends the
recording to the local backend automatically and displays the transcript in the central
text area.

If the browser does not show the intended headset microphone, ensure it is connected and
enabled in **System Settings → Sound → Input**, then use **Refresh** again. A browser may
require its own microphone permission even when macOS has granted it to another app.

## Configuration

The backend has safe defaults and accepts the following optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `COHERE_VOICE_MODEL` | `CohereLabs/cohere-transcribe-03-2026` | Hugging Face model ID or local MLX-compatible path. |
| `COHERE_VOICE_LANGUAGE` | `it` | Default ASR language sent to MLX Audio. |
| `COHERE_VOICE_MAX_TOKENS` | `8192` | Maximum generated transcript tokens per request. |
| `COHERE_VOICE_MAX_UPLOAD_BYTES` | `104857600` | Maximum browser audio upload size in bytes (100 MiB). |
| `ASR_BACKEND_URL` | `http://127.0.0.1:8000` | Backend URL used only by the Next.js server route handler. |

To change `ASR_BACKEND_URL`, copy `frontend/.env.local.example` to `frontend/.env.local`
and edit the value. Do not expose a Hugging Face token or other credentials in that file.

## Local backend endpoints

* `GET /health` returns backend availability and whether the model is already loaded.
* `GET /models` returns the configured default model and language.
* `POST /transcribe` receives multipart form data with an `audio` file and optional
  `language` string. It returns the transcript, model ID, language, and original filename.

The backend rejects missing, empty, unsupported, or oversized uploads. Model loading and
inference failures are reported without exposing Python internals to the browser.

## Development checks

```bash
conda activate cohere-voice
pytest macos/demo02/backend/tests
black --check macos/demo02/backend
pylint macos/demo02/backend/app

cd macos/demo02/frontend
npm run check
npm run build
```

See [the Demo 02 specification](../../specs/demo02-nextjs-ui.md) for the accepted
architecture and requirements.
