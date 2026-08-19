import { NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";
const DEFAULT_MODEL_ID = "CohereLabs/cohere-transcribe-03-2026";
const DEFAULT_MAX_TOKENS = "8192";
const BACKEND_TIMEOUT_MS = 15 * 60 * 1000;

function backendUrl(): string {
  return (process.env.ASR_BACKEND_URL ?? DEFAULT_BACKEND_URL).replace(/\/$/, "");
}

export async function POST(request: Request): Promise<NextResponse> {
  const formData = await request.formData();
  const audio = formData.get("audio");

  if (!(audio instanceof File)) {
    return NextResponse.json({ detail: "A recorded audio file is required." }, { status: 400 });
  }

  const language = formData.get("language");
  const mlxAudioFormData = new FormData();
  mlxAudioFormData.append("file", audio, audio.name);
  mlxAudioFormData.append("model", process.env.ASR_MODEL_ID ?? DEFAULT_MODEL_ID);
  mlxAudioFormData.append("max_tokens", process.env.ASR_MAX_TOKENS ?? DEFAULT_MAX_TOKENS);
  mlxAudioFormData.append("response_format", "json");
  if (typeof language === "string" && language.trim()) {
    mlxAudioFormData.append("language", language.trim());
  }

  try {
    const backendResponse = await fetch(`${backendUrl()}/v1/audio/transcriptions`, {
      method: "POST",
      body: mlxAudioFormData,
      cache: "no-store",
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
    });
    const payload = await backendResponse.json().catch(() => ({
      detail: "The local ASR backend returned an invalid response.",
    }));

    if (!backendResponse.ok) {
      return NextResponse.json(payload, { status: backendResponse.status });
    }
    if (typeof payload.text !== "string") {
      return NextResponse.json(
        { detail: "The local MLX Audio server returned no transcript text." },
        { status: 502 },
      );
    }

    return NextResponse.json({
      transcript: payload.text,
      model_id: process.env.ASR_MODEL_ID ?? DEFAULT_MODEL_ID,
      language: typeof language === "string" ? language : "",
      filename: audio.name,
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown connection error.";
    return NextResponse.json(
      {
        detail: `Cannot reach the local MLX Audio server at ${backendUrl()}: ${detail}`,
      },
      { status: 503 },
    );
  }
}
