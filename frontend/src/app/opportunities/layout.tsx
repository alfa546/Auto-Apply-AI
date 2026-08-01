import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Opportunities | AutoApply AI",
  description: "Discover AI-matched job and internship opportunities scanned across your targeted international locations.",
};

export default function OpportunitiesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
