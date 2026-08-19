# Demo 02: local recording UI with Next.js

`demo02` provides a graphical, local-only transcription workflow for Apple Silicon
macOS. A Next.js interface lets the user grant microphone access, select a browser-visible
input device, record audio, and read or edit the resulting transcript. A separate server
provided by `mlx-audio` runs in the `cohere-voice` Conda environment and invokes
the official, non-quantized `CohereLabs/cohere-transcribe-03-2026` checkpoint.

## Architecture

```text
Browser microphone -> Next.js UI -> Next.js /api/transcribe proxy -> MLX Audio API -> MLX
```

The browser is responsible only for device selection and recording. The Next.js route
handler forwards the audio to the `mlx-audio` server, so the browser never contacts the
API process directly and no browser CORS configuration is required. The MLX Audio server
implements the OpenAI-compatible Audio Transcriptions API at
`POST /v1/audio/transcriptions`; Demo 02 uses this upstream API rather than maintaining a
project-owned FastAPI backend. The server loads the model on demand and reuses it for
subsequent requests.

After model artefacts are downloaded from Hugging Face, audio and transcripts stay on the
Mac. Upload decoding and in-memory model management are handled by MLX Audio.

## Prerequisites

* Apple Silicon macOS with Metal available.
* Conda environment `cohere-voice`.
* Node.js 20.9 or later and npm.
* FFmpeg available in the `cohere-voice` environment. Browser recordings are normally
  WebM or MP4/M4A and require it for decoding.
* Browser microphone permission. Chrome and Safari can expose different audio formats;
  the MLX Audio server accepts browser-recorded WebM, MP4/M4A, OGG, WAV, and MPEG files.
* Access approval for Cohere's gated model, Hugging Face authentication, and a local
  model download as documented in the [parent macOS guide](../README.md).

Install the Python runtime from the repository root:

```bash
conda activate cohere-voice
python -m pip install -r macos/requirements.txt
conda install -n cohere-voice -c conda-forge ffmpeg
```

The Conda command is the recommended macOS setup for this repository because the backend
is started from that environment. If FFmpeg is already managed through Homebrew, `brew
install ffmpeg` is also valid, provided its executable is visible in the environment's
`PATH`. The Linux command shown by the upstream `mlx-audio` error does not apply here.

Install the frontend dependencies once:

```bash
cd macos/demo02/frontend
npm install
```

## Run the demo

Use two terminals from the repository root.

Terminal 1 starts the MLX Audio OpenAI-compatible API server in the Conda environment:

```bash
conda activate cohere-voice
./macos/demo02/backend/start_server.sh
```

The script binds only to `127.0.0.1`, exposes port `8000` by default, and restricts API
CORS to `http://localhost:3000`. It accepts `MLX_AUDIO_HOST`, `MLX_AUDIO_PORT`, and
`MLX_AUDIO_ALLOWED_ORIGINS` when a different local setup is needed.

Terminal 2 starts the Next.js frontend:

```bash
cd macos/demo02/frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Select **Refresh** in the sidebar
to grant browser microphone permission and populate the input-device list. Choose the
desired microphone and transcription language, press **Start recording**, then **Stop
recording**. The UI sends the recording to the local backend automatically and displays
the transcript in the central text area. Italian (`it`) is selected by default; English
(`en`), French (`fr`), Arabic (`ar`), and Dutch (`nl`) are also available.

If the browser does not show the intended headset microphone, ensure it is connected and
enabled in **System Settings → Sound → Input**, then use **Refresh** again. A browser may
require its own microphone permission even when macOS has granted it to another app.

## Configuration

The backend has safe defaults and accepts the following optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `ASR_BACKEND_URL` | `http://127.0.0.1:8000` | MLX Audio API URL used only by the Next.js server route handler. |
| `ASR_MODEL_ID` | `CohereLabs/cohere-transcribe-03-2026` | Model ID supplied to the OpenAI-compatible transcription request. |
| `ASR_MAX_TOKENS` | `8192` | Maximum transcript tokens supplied to the API request. |
| `MLX_AUDIO_HOST` | `127.0.0.1` | Network interface used by the backend start script. |
| `MLX_AUDIO_PORT` | `8000` | Port used by the backend start script. |
| `MLX_AUDIO_ALLOWED_ORIGINS` | `http://localhost:3000` | CORS origin permitted by the MLX Audio server. |

To change `ASR_BACKEND_URL`, copy `frontend/.env.local.example` to `frontend/.env.local`
and edit the value. Do not expose a Hugging Face token or other credentials in that file.

## MLX Audio OpenAI-compatible API

The backend is MLX Audio's own server, not an application maintained in this repository.
The relevant upstream endpoints are:

* `POST /v1/audio/transcriptions`: receives multipart `file`, `model`, `language`, and
  `max_tokens` fields. Demo 02 additionally requests the OpenAI-compatible JSON response
  format and maps its `text` result to the UI transcript.
* `GET /v1/models`: lists models managed by the MLX Audio server.

The Next.js route handler validates that a browser recording is present, forwards the
request server-side, and reports API connection or response errors in the UI.

## Development checks

```bash
conda activate cohere-voice
mlx_audio.server --help

cd macos/demo02/frontend
npm run check
npm run build
```

See [the Demo 02 specification](../../specs/demo02-nextjs-ui.md) for the accepted
architecture and requirements.
