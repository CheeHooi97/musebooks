import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MuseBooks — Photobook discovery",
  description: "Find the next book worth keeping.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
