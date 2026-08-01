"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import HistoryTab from "../components/HistoryTab";
import ErrorBoundary from "../components/ErrorBoundary";
import Toast from "../components/Toast";
import { Application } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function HistoryPage() {
  const { token, isAuthenticated } = useAuth();

  const [applications, setApplications] = useState<Application[]>([]);
  const [historyFilter, setHistoryFilter] = useState<"today" | "monthly" | "yearly" | "all">("today");
  const [isAppsLoading, setIsAppsLoading] = useState(true);
  const [appsError, setAppsError] = useState<string | null>(null);

  // Toast Notification State
  const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification((prev) => (prev?.message === message ? null : prev));
    }, 4000);
  };

  const fetchApplications = useCallback(async () => {
    if (!token) return;
    setIsAppsLoading(true);
    setAppsError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/applications`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) {
        if (res.status === 404) {
          setApplications([]);
          return;
        }
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server responded with status ${res.status}`);
      }
      const data = await res.json();
      setApplications(Array.isArray(data) ? data : []);
    } catch (err: any) {
      const msg = err instanceof Error ? err.message : "Failed to load application history";
      setAppsError(msg);
      showToast(`Applications fetch failed: ${msg}`, "error");
    } finally {
      setIsAppsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated || !token) return;
    fetchApplications();
  }, [isAuthenticated, token, fetchApplications]);

  // Compute time-filtered subsets
  const now = new Date();
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const startOfYear = new Date(now.getFullYear(), 0, 1);

  const todayApps = useMemo(() => 
    applications.filter(app => new Date(app.applied_at) >= startOfDay),
    [applications, startOfDay]
  );

  const monthlyApps = useMemo(() =>
    applications.filter(app => new Date(app.applied_at) >= startOfMonth),
    [applications, startOfMonth]
  );

  const yearlyApps = useMemo(() =>
    applications.filter(app => new Date(app.applied_at) >= startOfYear),
    [applications, startOfYear]
  );

  const todayJobsCount = useMemo(() =>
    todayApps.filter(app => app.opportunity_type !== "internship").length,
    [todayApps]
  );

  const todayInternshipsCount = useMemo(() =>
    todayApps.filter(app => app.opportunity_type === "internship").length,
    [todayApps]
  );

  const filteredApplications = useMemo(() => {
    if (historyFilter === "today") return todayApps;
    if (historyFilter === "monthly") return monthlyApps;
    if (historyFilter === "yearly") return yearlyApps;
    return applications;
  }, [historyFilter, todayApps, monthlyApps, yearlyApps, applications]);

  return (
    <div className="min-h-screen bg-[#090a0f] bg-grid-omni text-slate-100 selection:bg-rose-500 selection:text-white">
      <Toast notification={notification} />
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <HistoryTab
            isLoading={isAppsLoading}
            error={appsError}
            onRetry={fetchApplications}
            historyFilter={historyFilter}
            setHistoryFilter={setHistoryFilter}
            todayApps={todayApps}
            todayJobsCount={todayJobsCount}
            todayInternshipsCount={todayInternshipsCount}
            monthlyApps={monthlyApps}
            yearlyApps={yearlyApps}
            applications={applications}
            filteredApplications={filteredApplications}
          />
        </ErrorBoundary>
      </main>
    </div>
  );
}
