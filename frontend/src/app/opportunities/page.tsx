"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import JobsTab from "../components/JobsTab";
import ErrorBoundary from "../components/ErrorBoundary";
import Toast from "../components/Toast";
import { Job, Application } from "../types";
import { ALL_WORLD_COUNTRIES } from "../constants";
import EmailReviewModal from "../components/EmailReviewModal";
import AutoApplyModal from "../components/AutoApplyModal";
import AutoApplyProgress from "../components/AutoApplyProgress";
import JobDetailsModal from "../components/JobDetailsModal";

// Map country names (with emoji flags) to standardized names without emoji for matching
const COUNTRY_NAME_MAP: Record<string, string> = {
  "United States": "us",
  "Canada": "ca",
  "United Kingdom": "gb",
  "Germany": "de",
  "Netherlands": "nl",
  "Switzerland": "ch",
  "Sweden": "se",
  "Australia": "au",
  "Singapore": "sg",
  "United Arab Emirates": "ae",
  "Saudi Arabia": "sa",
  "Japan": "jp",
  "Ireland": "ie",
  "France": "fr",
  "New Zealand": "nz",
  "Denmark": "dk",
  "Norway": "no",
  "Finland": "fi",
  "Austria": "at",
  "Belgium": "be",
  "Spain": "es",
  "Italy": "it",
  "Portugal": "pt",
  "Poland": "pl",
  "Estonia": "ee",
  "Qatar": "qa",
  "Kuwait": "kw",
  "Oman": "om",
  "Bahrain": "bh",
  "Turkey": "tr",
  "South Korea": "kr",
  "Malaysia": "my",
  "China": "cn",
  "India": "in",
  "Pakistan": "pk",
  "Brazil": "br",
  "Mexico": "mx",
  "Argentina": "ar",
  "Chile": "cl",
  "South Africa": "za"
};

function normalizeCountryName(country: string): string {
  // Strip emoji flags and trim
  return country.replace(/[\u{1F1E6}-\u{1F1FF}]/gu, "").trim();
}

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

  // Email Review Modal State
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [emailPreview, setEmailPreview] = useState<any>(null);
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [pendingJob, setPendingJob] = useState<Job | null>(null);

  // Job Details Modal State
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isJobDetailsOpen, setIsJobDetailsOpen] = useState(false);
  const [isApplyingFromDetails, setIsApplyingFromDetails] = useState(false);

  // Auto-Apply Batch State
  const [isAutoApplyModalOpen, setIsAutoApplyModalOpen] = useState(false);
  const [isStartingAutoApply, setIsStartingAutoApply] = useState(false);
  const [autoApplyStatus, setAutoApplyStatus] = useState<any>(null);
  const [isStoppingAutoApply, setIsStoppingAutoApply] = useState(false);

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

  // Step 1: Generate preview and show review modal
  const handleAutoApply = async (job: Job) => {
    setIsApplyingId(job.id);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auto-apply/preview`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ job_id: job.id })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.success && data.preview) {
          setPendingJob(job);
          setEmailPreview(data.preview);
          setIsReviewModalOpen(true);
          // Close job details modal if open
          setIsJobDetailsOpen(false);
        } else {
          showToast(data.message || "Failed to generate email preview.", "error");
        }
      } else {
        const errData = await res.json().catch(() => ({}));
        showToast(errData.detail || `Failed to generate email preview (status ${res.status}).`, "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to connect to backend application router.", "error");
    } finally {
      setIsApplyingId(null);
      setIsApplyingFromDetails(false);
    }
  };

  // Handle apply from job details modal
  const handleApplyFromDetails = async (job: Job) => {
    setIsApplyingFromDetails(true);
    await handleAutoApply(job);
  };

  // Open job details modal
  const handleViewJobDetails = (job: Job) => {
    setSelectedJob(job);
    setIsJobDetailsOpen(true);
  };

  // Step 2: User confirmed - send the email
  const handleConfirmSendEmail = async () => {
    if (!pendingJob) return;
    setIsSendingEmail(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auto-apply/send-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ job_id: pendingJob.id })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          showToast(`⚡ Application successfully emailed to ${pendingJob.company} via Gmail! Sent to ${data.recipient_email || 'HR'}`);
        } else {
          showToast(data.message || data.error || `Failed to send email application.`, "error");
        }
      } else {
        const errData = await res.json().catch(() => ({}));
        showToast(errData.detail || `Failed to send email application (status ${res.status}).`, "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to connect to backend application router.", "error");
    } finally {
      setIsSendingEmail(false);
      setIsReviewModalOpen(false);
      setPendingJob(null);
      setEmailPreview(null);
    }
  };

  // Auto-Apply Batch Handlers
  const fetchAutoApplyStatus = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/auto-apply/status`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAutoApplyStatus(data);
      }
    } catch (err) {
      console.error("Failed to fetch auto-apply status:", err);
    }
  }, [token]);

  const handleStartAutoApply = async (jobCount: number, internshipCount: number) => {
    setIsStartingAutoApply(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auto-apply/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ job_count: jobCount, internship_count: internshipCount })
      });

      if (res.ok) {
        const data = await res.json();
        showToast(data.message || "Auto-apply started successfully!");
        setIsAutoApplyModalOpen(false);
        fetchAutoApplyStatus();
      } else {
        const errData = await res.json().catch(() => ({}));
        showToast(errData.detail || `Failed to start auto-apply (status ${res.status}).`, "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to connect to backend auto-apply router.", "error");
    } finally {
      setIsStartingAutoApply(false);
    }
  };

  const openAutoApplyModal = () => {
    setIsAutoApplyModalOpen(true);
  };

  const handleStopAutoApply = async () => {
    setIsStoppingAutoApply(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auto-apply/stop`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        showToast(data.message || "Auto-apply stopped.");
        fetchAutoApplyStatus();
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to stop auto-apply.", "error");
    } finally {
      setIsStoppingAutoApply(false);
    }
  };

  // Poll auto-apply status every 3 seconds while running
  useEffect(() => {
    if (!isAuthenticated || !token) return;
    fetchAutoApplyStatus();
    const interval = setInterval(() => {
      fetchAutoApplyStatus();
    }, 3000);
    return () => clearInterval(interval);
  }, [isAuthenticated, token, fetchAutoApplyStatus]);

  // Filter jobs by selected target countries
  // Convert selected country names (e.g. "United States 🇺🇸") to country codes ("us")
  // to match against job.country which stores codes like "us", "gb", "de"
  const selectedCountryCodes = selectedCountries.map(c => {
    const name = normalizeCountryName(c).toLowerCase();
    // Reverse lookup from name map
    for (const [countryName, code] of Object.entries(COUNTRY_NAME_MAP)) {
      if (countryName.toLowerCase() === name) return code;
    }
    // Try direct match (e.g. user typed "US" or "us")
    return name === "usa" ? "us" : name;
  });

  const filteredDailyJobs = dailyJobs.filter(
    (job) => {
      if (!job.country) return true;
      return selectedCountryCodes.includes(job.country.toLowerCase());
    }
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
            handleAutoApplyBatch={openAutoApplyModal}
            isAutoApplyRunning={autoApplyStatus?.status === "running"}
            onStopAutoApply={handleStopAutoApply}
            isAutoApplyStopping={isStoppingAutoApply}
            onViewJobDetails={handleViewJobDetails}
            isLoading={isJobsLoading}
            error={jobsError}
            onRetry={fetchOpportunities}
          />
        </ErrorBoundary>
      </main>

      {/* Email Review Modal - shows before sending */}
      <EmailReviewModal
        isOpen={isReviewModalOpen}
        onClose={() => {
          setIsReviewModalOpen(false);
          setPendingJob(null);
          setEmailPreview(null);
        }}
        onConfirm={handleConfirmSendEmail}
        preview={emailPreview}
        isSending={isSendingEmail}
      />

      {/* Auto-Apply Modal - configure counts */}
      <AutoApplyModal
        isOpen={isAutoApplyModalOpen}
        onClose={() => setIsAutoApplyModalOpen(false)}
        onStart={handleStartAutoApply}
        isStarting={isStartingAutoApply}
      />

      {/* Auto-Apply Progress Tracker - floating status panel */}
      <AutoApplyProgress
        status={autoApplyStatus}
        onStop={handleStopAutoApply}
        isStopping={isStoppingAutoApply}
      />

      {/* Job Details Modal - shows full description with apply button */}
      <JobDetailsModal
        job={selectedJob}
        isOpen={isJobDetailsOpen}
        onClose={() => {
          setIsJobDetailsOpen(false);
          setSelectedJob(null);
        }}
        onApply={handleApplyFromDetails}
        isApplying={isApplyingFromDetails}
      />
    </div>
  );
}
