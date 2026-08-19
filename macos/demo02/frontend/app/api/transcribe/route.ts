import { NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";
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

  try {
    const backendResponse = await fetch(`${backendUrl()}/transcribe`, {
      method: "POST",
      body: formData,
      cache: "no-store",
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
    });
    const payload = await backendResponse.json().catch(() => ({
      detail: "The local ASR backend returned an invalid response.",
    }));

    return NextResponse.json(payload, { status: backendResponse.status });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown connection error.";
    return NextResponse.json(
      {
        detail: `Cannot reach the local ASR backend at ${backendUrl()}: ${detail}`,
      },
      { status: 503 },
    );
  }
}
