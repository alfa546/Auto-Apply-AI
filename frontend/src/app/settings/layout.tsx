import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "API Settings & Integrations | AutoApply AI",
  description: "Configure your LLM providers (OpenAI/Ollama), Google OAuth client secrets, and global job board API keys.",
};

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
