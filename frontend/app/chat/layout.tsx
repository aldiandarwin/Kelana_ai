import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Conversation Memory | KelanaAI",
  description: "Continue private travel-planning conversations with KelanaAI.",
};

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return children;
}
