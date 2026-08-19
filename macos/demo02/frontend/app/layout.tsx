import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Cohere Voice · Demo 02",
  description: "Local macOS recording and ASR transcription demo.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
