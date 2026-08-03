"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import ProfileTab from "../components/ProfileTab";
import ErrorBoundary from "../components/ErrorBoundary";
import Toast from "../components/Toast";
import { ProfileData, AtsMetrics, Application } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function ProfilePage() {
  const { user, token, isAuthenticated } = useAuth();

  // User details & links
  const [userEmail, setUserEmail] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("https://your-portfolio.dev");
  const [githubUrl, setGithubUrl] = useState("https://github.com/your-username");
  const [otherUrl, setOtherUrl] = useState("https://linkedin.com/in/your-username");

  // Career Preferences
  const [targetRoles, setTargetRoles] = useState<string[]>(["Frontend Engineer", "Full Stack Developer", "AI Specialist"]);
  const [countryQuery, setCountryQuery] = useState("");
  const [isCountryDropdownOpen, setIsCountryDropdownOpen] = useState(false);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([
    "United States", "United Kingdom", "Canada", "Australia",
    "Germany", "France", "Singapore", "Netherlands",
    "Sweden", "Switzerland", "United Arab Emirates"
  ]);
  const [workModePref, setWorkModePref] = useState("Remote & Hybrid Permitted");
  const [salaryPref, setSalaryPref] = useState("$100,000+");
  const [experiencePref, setExperiencePref] = useState("Mid-to-Senior (3-7 yrs)");
  const [visaSponsorshipPref, setVisaSponsorshipPref] = useState("No visa sponsorship required");
  const [selectedEmpTypes, setSelectedEmpTypes] = useState<string[]>(["Full-time", "Contract"]);
  const [dailyJobGoal, setDailyJobGoal] = useState(15);
  const [dailyInternshipGoal, setDailyInternshipGoal] = useState(5);
  const [autoFulfillEnabled, setAutoFulfillEnabled] = useState(true);

  // Resume Upload & Agent Logs State
  const [isUploading, setIsUploading] = useState(false);
  const [agentPhase, setAgentPhase] = useState<string | null>(null);
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const [uploadedResume, setUploadedResume] = useState<string | null>(null);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isAnalyzingATS, setIsAnalyzingATS] = useState(false);

  // Loading & Error states
  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [todayJobsCount, setTodayJobsCount] = useState(0);
  const [todayInternshipsCount, setTodayInternshipsCount] = useState(0);

  // Extracted Profile
  const [extractedProfile, setExtractedProfile] = useState<ProfileData>({
    summary: "",
    skills: [],
    experience: [],
    education: [],
    projects: []
  });

  // ATS Metrics
  const [atsMetrics, setAtsMetrics] = useState<AtsMetrics>({
    overall_score: 0,
    formatting_score: 0,
    keyword_density_score: 0,
    action_verbs_score: 0,
    section_completeness_score: 0,
    summary: "No resume analyzed yet. Upload a PDF resume above to run real-time ATS grading.",
    strengths: [],
    missing_skills: [],
    formatting_suggestions: [],
    experience_improvements: []
  });

  // Toast Notification State
  const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification((prev) => (prev?.message === message ? null : prev));
    }, 4000);
  };

  useEffect(() => {
    if (user?.email) {
      setUserEmail(user.email);
    }
  }, [user]);

  const fetchResumeProfile = useCallback(async () => {
    if (!token) return;
    setIsProfileLoading(true);
    setProfileError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/resumes/profile`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) {
        if (res.status === 404) {
          setIsProfileLoading(false);
          return;
        }
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server responded with status ${res.status}`);
      }
      const data = await res.json();
      if (data.resume_url) setUploadedResume("Active Resume (Saved)");
      setExtractedProfile(prev => ({
        ...prev,
        summary: data.summary || prev.summary,
        skills: data.skills || prev.skills,
        experience: data.experience || prev.experience,
        education: data.education || prev.education,
        projects: data.projects || prev.projects
      }));
      if (data.ats_score) {
        setAtsMetrics(prev => ({
          ...prev,
          overall_score: data.ats_score
        }));
      }
    } catch (err: any) {
      const msg = err instanceof Error ? err.message : "Failed to load resume profile";
      setProfileError(msg);
      showToast(`Profile fetch failed: ${msg}`, "error");
    } finally {
      setIsProfileLoading(false);
    }
  }, [token]);

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
      console.error("Failed to load user settings in profile:", err);
    }
  }, [token]);

  const fetchTodayApplicationCounts = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/applications`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          const now = new Date();
          const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
          const todayApps = data.filter((app: Application) => new Date(app.applied_at) >= startOfDay);
          setTodayJobsCount(todayApps.filter(app => app.opportunity_type !== "internship").length);
          setTodayInternshipsCount(todayApps.filter(app => app.opportunity_type === "internship").length);
        }
      }
    } catch (err) {
      console.error("Failed to calculate goal progress:", err);
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated || !token) return;
    fetchResumeProfile();
    fetchUserSettings();
    fetchTodayApplicationCounts();
  }, [isAuthenticated, token, fetchResumeProfile, fetchUserSettings, fetchTodayApplicationCounts]);

  const toggleEmpType = (type: string) => {
    setSelectedEmpTypes(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const handleSelectCountryFromDropdown = (country: string) => {
    if (!selectedCountries.includes(country)) {
      setSelectedCountries([...selectedCountries, country]);
    }
    setCountryQuery("");
    setIsCountryDropdownOpen(false);
  };

  const handleRemoveCountry = (country: string) => {
    setSelectedCountries(selectedCountries.filter(c => c !== country));
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingProfile(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/users/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          email: userEmail,
          portfolio_url: portfolioUrl,
          github_url: githubUrl,
          other_url: otherUrl,
          target_roles: targetRoles,
          target_countries: selectedCountries,
          work_mode_preference: workModePref,
          employment_types: selectedEmpTypes,
          salary_preference: salaryPref,
          experience_level: experiencePref,
          visa_sponsorship: (() => {
            const visaStr = visaSponsorshipPref.toLowerCase();
            return (visaStr.includes("required") || visaStr.includes("needed")) && !visaStr.includes("no visa") && !visaStr.includes("not required");
          })(),
          visa_sponsorship_str: visaSponsorshipPref,
          daily_job_goal: dailyJobGoal,
          daily_internship_goal: dailyInternshipGoal,
          auto_fulfill_enabled: autoFulfillEnabled
        })
      });
      if (res.ok) {
        showToast(`Saved ${selectedCountries.length} target countries & international preferences!`);
      } else {
        showToast("Failed to save profile.", "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to save profile.", "error");
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !token) return;

    setIsUploading(true);
    setAgentPhase("reading");
    setAgentLogs(["[Agent] Initializing local environment...", "[Agent] Reading PDF binary..."]);

    const formData = new FormData();
    formData.append("file", file);

    const fakeLogs = [
      "[Agent] Initializing AI analysis engine...",
      "[Agent] Chunking resume text...",
      "[Agent] Extracting skills and core competencies...",
      "[Agent] Analyzing work experience achievements...",
      "[Agent] Formatting structured JSON profile...",
      "[Agent] Calculating real-time ATS match score..."
    ];
    let logIndex = 0;

    const logInterval = setInterval(() => {
      if (logIndex < fakeLogs.length) {
        setAgentLogs(prev => [...prev, fakeLogs[logIndex]]);
        if (logIndex === 1) setAgentPhase("planning");
        else if (logIndex === 3) setAgentPhase("extracting");
        else if (logIndex === 5) setAgentPhase("scoring");
        logIndex++;
      }
    }, 1200);

    try {
      const res = await fetch(`${API_BASE}/api/v1/resumes/upload`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData
      });

      clearInterval(logInterval);
      setAgentPhase("complete");
      setAgentLogs(prev => [...prev, "[Agent] Process finished successfully!"]);

      if (res.ok) {
        const data = await res.json();
        setUploadedResume(file.name);
        setExtractedProfile(prev => ({
          ...prev,
          summary: data.summary || prev.summary,
          skills: data.skills || prev.skills,
          experience: data.experience || prev.experience,
          education: data.education || prev.education,
          projects: data.projects || prev.projects
        }));
        if (data.ats_score) {
          setAtsMetrics(prev => ({
            ...prev,
            overall_score: data.ats_score
          }));
        }
        showToast("Resume uploaded and parsed successfully by AI Engine!");
      } else {
        if (res.status === 429) {
          showToast("Your API key limit has been reached! Please enter a new API key in Settings.", "error");
        } else {
          showToast("Failed to upload and analyze resume.", "error");
        }
      }
    } catch (err) {
      clearInterval(logInterval);
      showToast(err instanceof Error ? err.message : "Failed to upload and analyze resume.", "error");
    } finally {
      setTimeout(() => {
        setIsUploading(false);
        setAgentPhase(null);
      }, 2000);
    }
  };

  const handleRunAtsCheck = async () => {
    if (!token) return;
    setIsAnalyzingATS(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/resumes/ats-check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ target_role: targetRoles[0] || "Full Stack Developer" })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.ats_score) {
          setAtsMetrics(prev => ({
            ...prev,
            overall_score: data.ats_score,
            missing_skills: data.ats_suggestions?.missing_skills || prev.missing_skills,
            formatting_suggestions: data.ats_suggestions?.formatting_suggestions || prev.formatting_suggestions,
            experience_improvements: data.ats_suggestions?.experience_improvements || prev.experience_improvements
          }));
        }
        showToast("AI Agent completed real-time ATS Audit!");
      } else {
        if (res.status === 429) {
          showToast("Your API key limit has been reached! Please enter a new API key in Settings.", "error");
        } else {
          showToast("Failed to run ATS Audit check.", "error");
        }
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to run ATS Audit check.", "error");
    } finally {
      setIsAnalyzingATS(false);
    }
  };

  const totalTodayApplied = todayJobsCount + todayInternshipsCount;
  const totalDailyTarget = dailyJobGoal + dailyInternshipGoal;
  const overallGoalProgress = totalDailyTarget > 0 ? Math.min(100, Math.round((totalTodayApplied / totalDailyTarget) * 100)) : 0;

  return (
    <div className="min-h-screen bg-[#090a0f] bg-grid-omni text-slate-100 selection:bg-rose-500 selection:text-white">
      <Toast notification={notification} />
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <ProfileTab
            userEmail={userEmail} setUserEmail={setUserEmail}
            portfolioUrl={portfolioUrl} setPortfolioUrl={setPortfolioUrl}
            githubUrl={githubUrl} setGithubUrl={setGithubUrl}
            otherUrl={otherUrl} setOtherUrl={setOtherUrl}
            targetRoles={targetRoles} setTargetRoles={setTargetRoles}
            countryQuery={countryQuery} setCountryQuery={setCountryQuery}
            isCountryDropdownOpen={isCountryDropdownOpen} setIsCountryDropdownOpen={setIsCountryDropdownOpen}
            selectedCountries={selectedCountries} handleSelectCountryFromDropdown={handleSelectCountryFromDropdown} handleRemoveCountry={handleRemoveCountry}
            workModePref={workModePref} setWorkModePref={setWorkModePref}
            salaryPref={salaryPref} setSalaryPref={setSalaryPref}
            experiencePref={experiencePref} setExperiencePref={setExperiencePref}
            visaSponsorshipPref={visaSponsorshipPref} setVisaSponsorshipPref={setVisaSponsorshipPref}
            selectedEmpTypes={selectedEmpTypes} toggleEmpType={toggleEmpType}
            dailyJobGoal={dailyJobGoal} setDailyJobGoal={setDailyJobGoal}
            dailyInternshipGoal={dailyInternshipGoal} setDailyInternshipGoal={setDailyInternshipGoal}
            totalTodayApplied={totalTodayApplied} totalDailyTarget={totalDailyTarget} overallGoalProgress={overallGoalProgress}
            todayJobsCount={todayJobsCount} todayInternshipsCount={todayInternshipsCount}
            isSavingProfile={isSavingProfile} handleSaveProfile={handleSaveProfile}
            isUploading={isUploading} agentPhase={agentPhase} agentLogs={agentLogs}
            uploadedResume={uploadedResume} handleResumeUpload={handleResumeUpload}
            extractedProfile={extractedProfile} atsMetrics={atsMetrics}
            handleRunAtsCheck={handleRunAtsCheck} isAnalyzingATS={isAnalyzingATS}
            isLoading={isProfileLoading} error={profileError} onRetry={fetchResumeProfile}
          />
        </ErrorBoundary>
      </main>
    </div>
  );
}
