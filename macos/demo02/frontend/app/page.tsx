"use client";

import { useEffect, useRef, useState } from "react";

const MODEL_ID = "CohereLabs/cohere-transcribe-03-2026";
const LANGUAGES = [
  { code: "it", label: "Italiano" },
  { code: "en", label: "English" },
  { code: "fr", label: "Français" },
  { code: "ar", label: "العربية" },
  { code: "nl", label: "Nederlands" },
] as const;

type AppStatus = "idle" | "requesting-device" | "recording" | "transcribing" | "error";

type TranscriptionResponse = {
  transcript: string;
  model_id: string;
  language: string;
  filename: string;
};

function preferredMimeType(): string | undefined {
  const supportedTypes = ["audio/webm;codecs=opus", "audio/mp4", "audio/ogg;codecs=opus"];
  return supportedTypes.find((mimeType) => MediaRecorder.isTypeSupported(mimeType));
}

function extensionForMimeType(mimeType: string): string {
  if (mimeType.includes("mp4")) {
    return "m4a";
  }
  if (mimeType.includes("ogg")) {
    return "ogg";
  }
  return "webm";
}

export default function Home() {
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");
  const [language, setLanguage] = useState("it");
  const [status, setStatus] = useState<AppStatus>("idle");
  const [transcript, setTranscript] = useState("");
  const [message, setMessage] = useState("Enable microphone access to list available input devices.");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const isBusy = status === "requesting-device" || status === "transcribing";
  const isRecording = status === "recording";

  useEffect(() => {
    return () => {
      recorderRef.current?.stop();
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  async function refreshDevices(): Promise<void> {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus("error");
      setMessage("This browser does not support microphone recording.");
      return;
    }

    setStatus("requesting-device");
    setMessage("Requesting microphone access…");
    try {
      const permissionStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      permissionStream.getTracks().forEach((track) => track.stop());
      const availableDevices = (await navigator.mediaDevices.enumerateDevices()).filter(
        (device) => device.kind === "audioinput",
      );
      setDevices(availableDevices);
      setSelectedDeviceId((currentId) => currentId || availableDevices[0]?.deviceId || "");
      setStatus("idle");
      setMessage(
        availableDevices.length
          ? "Choose an input device, then start recording."
          : "No audio-input device is available to this browser.",
      );
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Microphone permission was not granted.");
    }
  }

  async function startRecording(): Promise<void> {
    if (!selectedDeviceId) {
      setStatus("error");
      setMessage("Enable microphone access and select an input device first.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { deviceId: { exact: selectedDeviceId } },
      });
      const mimeType = preferredMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      chunksRef.current = [];
      streamRef.current = stream;
      recorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        void submitRecording(recorder.mimeType || mimeType || "audio/webm");
      };
      recorder.start();
      setTranscript("");
      setStatus("recording");
      setMessage("Recording in progress. Press Stop recording when you are finished.");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Unable to start recording.");
    }
  }

  function stopRecording(): void {
    if (recorderRef.current?.state === "recording") {
      recorderRef.current.stop();
      setStatus("transcribing");
      setMessage("Recording complete. Sending audio to the local ASR service…");
    }
  }

  async function submitRecording(mimeType: string): Promise<void> {
    const blob = new Blob(chunksRef.current, { type: mimeType });
    if (blob.size === 0) {
      setStatus("error");
      setMessage("The recording is empty. Please try again.");
      return;
    }

    const formData = new FormData();
    formData.append("audio", blob, `recording.${extensionForMimeType(mimeType)}`);
    formData.append("language", language);

    try {
      const response = await fetch("/api/transcribe", { method: "POST", body: formData });
      const payload = (await response.json()) as TranscriptionResponse | { detail?: string };
      if (!response.ok || !("transcript" in payload)) {
        const detail = "detail" in payload ? payload.detail : undefined;
        throw new Error(detail || "The local ASR service rejected the recording.");
      }
      setTranscript(payload.transcript);
      setStatus("idle");
      setMessage(`Transcription completed with ${payload.model_id}.`);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Transcription failed.");
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">CV</span>
          <div>
            <p className="eyebrow">LOCAL ASR LAB</p>
            <h1>Cohere Voice</h1>
          </div>
        </div>

        <section className="sidebar-section" aria-labelledby="model-heading">
          <p className="eyebrow" id="model-heading">ACTIVE MODEL</p>
          <div className="model-card">
            <span className="status-dot" />
            <div>
              <strong>Cohere Transcribe</strong>
              <span>{MODEL_ID}</span>
              <small>Non-quantized BF16 · MLX Audio</small>
            </div>
          </div>
        </section>

        <section className="sidebar-section" aria-labelledby="device-heading">
          <div className="section-heading">
            <p className="eyebrow" id="device-heading">AUDIO INPUT</p>
            <button className="text-button" type="button" onClick={refreshDevices} disabled={isBusy || isRecording}>
              Refresh
            </button>
          </div>
          <label className="device-label" htmlFor="audio-device">Microphone</label>
          <select
            id="audio-device"
            value={selectedDeviceId}
            onChange={(event) => setSelectedDeviceId(event.target.value)}
            disabled={isBusy || isRecording || devices.length === 0}
          >
            {devices.length === 0 ? (
              <option value="">Enable microphone access first</option>
            ) : (
              devices.map((device, index) => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label || `Microphone ${index + 1}`}
                </option>
              ))
            )}
          </select>
          <p className="helper-text">Device labels become visible after browser permission is granted.</p>
        </section>

        <section className="sidebar-section" aria-labelledby="language-heading">
          <p className="eyebrow" id="language-heading">TRANSCRIPTION LANGUAGE</p>
          <label className="device-label" htmlFor="language">Language</label>
          <select
            id="language"
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            disabled={isBusy || isRecording}
          >
            {LANGUAGES.map(({ code, label }) => (
              <option key={code} value={code}>{label} ({code})</option>
            ))}
          </select>
        </section>

        <div className="sidebar-footer">Apple Silicon · local-only processing</div>
      </aside>

      <section className="workspace">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">DEMO 02</p>
            <h2>Record, then transcribe.</h2>
          </div>
          <span className={`state-pill state-${status}`}>{status.replace("-", " ")}</span>
        </header>

        <div className="recording-panel">
          <div className={`waveform ${isRecording ? "waveform-live" : ""}`} aria-hidden="true">
            {Array.from({ length: 18 }, (_, index) => <i key={index} />)}
          </div>
          <p className="status-message" role="status">{message}</p>
          <div className="controls">
            <button className="primary-button" type="button" onClick={startRecording} disabled={isBusy || isRecording}>
              <span className="record-icon" /> Start recording
            </button>
            <button className="secondary-button" type="button" onClick={stopRecording} disabled={!isRecording}>
              <span className="stop-icon" /> Stop recording
            </button>
          </div>
        </div>

        <section className="transcript-panel" aria-labelledby="transcript-heading">
          <div className="transcript-heading">
            <div>
              <p className="eyebrow">RESULT</p>
              <h3 id="transcript-heading">Transcript</h3>
            </div>
            <span>{language.toUpperCase()}</span>
          </div>
          <textarea
            aria-label="Transcript"
            value={transcript}
            onChange={(event) => setTranscript(event.target.value)}
            placeholder="Your transcript will appear here after recording. You can edit it once it is ready."
          />
        </section>
      </section>
    </main>
  );
}
