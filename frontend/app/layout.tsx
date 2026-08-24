import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KelanaAI | AI Travel Planner",
  description:
    "Plan a thoughtful day-by-day itinerary with FastAPI and Amazon Bedrock.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
