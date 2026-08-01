import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Application History | AutoApply AI",
  description: "Monitor real-time Gmail application submissions, email verification proofs, and career opportunity tracking.",
};

export default function HistoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
