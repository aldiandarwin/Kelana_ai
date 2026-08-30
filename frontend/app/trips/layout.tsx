import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My Trips | KelanaAI",
  description: "Browse your private KelanaAI itinerary history.",
};

export default function TripsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
