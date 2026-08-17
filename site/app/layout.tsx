import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LiteMind CLI — Terminal UI for AI Chat & RAG",
  description:
    "A terminal user interface for the LiteMindUI backend. Chat with local and cloud AI models, query your own documents with RAG — all from your terminal, no browser required.",
  keywords: ["tui", "cli", "ai", "rag", "llm", "terminal", "textual"],
  authors: [{ name: "Debabrata Mishra" }],
  openGraph: {
    title: "LiteMind CLI — Terminal UI for AI Chat & RAG",
    description:
      "A terminal user interface for the LiteMindUI backend. Chat with local and cloud AI models, query your own documents with RAG — all from your terminal, no browser required.",
    url: "https://debabratamishra.github.io/litemind-cli/",
    type: "website",
  },
  alternates: {
    types: {
      "application/rss+xml": "https://debabratamishra.github.io/litemind-cli/feed.xml",
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen bg-canvas font-sans text-ink antialiased">
        {children}
      </body>
    </html>
  );
}
