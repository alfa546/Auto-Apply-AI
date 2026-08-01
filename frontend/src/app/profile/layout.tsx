import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "User Profile & CV Management | AutoApply AI",
  description: "Configure target international markets, career goals, and upload resumes for real-time AI parsing and ATS scoring.",
};

export default function ProfileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
