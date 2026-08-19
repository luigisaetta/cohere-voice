#!/usr/bin/env bash
# Starts the local MLX Audio OpenAI-compatible API server for Demo 02.

set -euo pipefail

SERVER_HOST="${MLX_AUDIO_HOST:-127.0.0.1}"
SERVER_PORT="${MLX_AUDIO_PORT:-8000}"
ALLOWED_ORIGINS="${MLX_AUDIO_ALLOWED_ORIGINS:-http://localhost:3000}"

if ! command -v mlx_audio.server >/dev/null 2>&1; then
  echo "mlx_audio.server was not found. Activate the cohere-voice Conda environment first." >&2
  exit 1
fi

echo "Starting MLX Audio OpenAI-compatible API at http://${SERVER_HOST}:${SERVER_PORT}"
exec mlx_audio.server \
  --host "${SERVER_HOST}" \
  --port "${SERVER_PORT}" \
  --allowed-origins "${ALLOWED_ORIGINS}"
