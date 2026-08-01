"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import JobsTab from "../components/JobsTab";
import ErrorBoundary from "../components/ErrorBoundary";
import Toast from "../components/Toast";
import { Job, Application } from "../types";
import { ALL_WORLD_COUNTRIES } from "../constants";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function OpportunitiesPage() {
  const { token, isAuthenticated } = useAuth();

  // Data & UI State
  const [dailyJobs, setDailyJobs] = useState<Job[]>([]);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([
    "United States", "United Kingdom", "Canada", "Australia",
    "Germany", "France", "Singapore", "Netherlands",
    "Sweden", "Switzerland", "United Arab Emirates"
  ]);
  const [isJobsLoading, setIsJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);

  const [isTriggeringSearch, setIsTriggeringSearch] = useState(false);
  const [isApplyingId, setIsApplyingId] = useState<number | null>(null);

  // Toast Notification State
  const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification((prev) => (prev?.message === message ? null : prev));
    }, 4000);
  };

  const fetchUserSettings = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/users/settings`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.target_countries?.length) {
          setSelectedCountries(data.target_countries);
        }
      }
    } catch (err) {
      console.error("Failed to load target countries setting:", err);
    }
  }, [token]);

  const fetchOpportunities = useCallback(async () => {
    if (!token) return;
    setIsJobsLoading(true);
    setJobsError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/search/opportunities?limit=50`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) {
        if (res.status === 404) {
          setDailyJobs([]);
          return;
        }
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server responded with status ${res.status}`);
      }
      const data = await res.json();
      setDailyJobs(data.items || []);
    } catch (err: any) {
      const msg = err instanceof Error ? err.message : "Failed to load job opportunities";
      setJobsError(msg);
      showToast(`Opportunities fetch failed: ${msg}`, "error");
    } finally {
      setIsJobsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated || !token) return;
    fetchUserSettings();
    fetchOpportunities();
  }, [isAuthenticated, token, fetchUserSettings, fetchOpportunities]);

  const handleTriggerSearchAgent = async () => {
    setIsTriggeringSearch(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/search/trigger`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({})
      });
      if (res.ok) {
        const data = await res.json();
        showToast(data.message || "Smart Job Search Agent completed multi-country scan!");
        fetchOpportunities();
      } else {
        if (res.status === 429) {
          showToast("Your API key limit has been reached! Please enter a new API key in Settings.", "error");
        } else {
          const errData = await res.json().catch(() => ({}));
          showToast(errData.detail || `Failed to trigger Smart Search Agent (status ${res.status}).`, "error");
        }
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to trigger Smart Search Agent.", "error");
    } finally {
      setIsTriggeringSearch(false);
    }
  };

  const handleAutoApply = async (job: Job) => {
    setIsApplyingId(job.id);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auto-apply/send-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ job_id: job.id })
      });

      if (res.ok) {
        showToast(`⚡ Application successfully emailed to ${job.company} via Gmail!`);
      } else {
        const errData = await res.json().catch(() => ({}));
        showToast(errData.detail || `Failed to send email application (status ${res.status}).`, "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to connect to backend application router.", "error");
    } finally {
      setIsApplyingId(null);
    }
  };

  // Filter jobs by selected target countries
  const filteredDailyJobs = dailyJobs.filter(
    (job) => !job.country || selectedCountries.includes(job.country)
  );

  return (
    <div className="min-h-screen bg-[#090a0f] bg-grid-omni text-slate-100 selection:bg-rose-500 selection:text-white">
      <Toast notification={notification} />
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <JobsTab
            filteredDailyJobs={filteredDailyJobs}
            selectedCountries={selectedCountries}
            isTriggeringSearch={isTriggeringSearch}
            handleTriggerSearchAgent={handleTriggerSearchAgent}
            isApplyingId={isApplyingId}
            handleAutoApply={handleAutoApply}
            isLoading={isJobsLoading}
            error={jobsError}
            onRetry={fetchOpportunities}
          />
        </ErrorBoundary>
      </main>
    </div>
  );
}
