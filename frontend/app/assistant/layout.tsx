import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Travel Assistant | KelanaAI",
  description:
    "Ask KelanaAI a travel question and get an answer grounded in trusted documents.",
};

export default function AssistantLayout({ children }: { children: React.ReactNode }) {
  return children;
}
