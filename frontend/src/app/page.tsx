"use client";

import Dashboard from "./components/Dashboard";
import ErrorBoundary from "./components/ErrorBoundary";

export default function Home() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  );
}
