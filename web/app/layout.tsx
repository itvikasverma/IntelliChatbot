import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Personal Data Tools Chat",
  description: "LangGraph chatbot UI with short-term memory and multi-tool calling",
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
