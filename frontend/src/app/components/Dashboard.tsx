"use client";
import JobsTab from "./JobsTab";
import HistoryTab from "./HistoryTab";
import ProfileTab from "./ProfileTab";
import SettingsTab from "./SettingsTab";
import GmailModal from "./GmailModal";
import Toast from "./Toast";
import { DashboardIcon, GmailIcon, UserIcon, CheckCircleIcon, KeyIcon } from "./Icons";
import { Job, Application, ProfileData, AtsMetrics } from "../types";
import { ALL_WORLD_COUNTRIES } from "../constants";


import React, { useState, useEffect } from "react";

// Standard SVG Icons


const SparklesIcon = ({ className = "w-5 h-5 object-contain rounded-md" }: { className?: string }) => (
  <img src="/logo.png" alt="Auto-Apply AI Logo" className={className} />
);





const GithubIcon = () => (
  <svg className="w-4 h-4 text-slate-300" fill="currentColor" viewBox="0 0 24 24">
    <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
  </svg>
);

const LinkedinIcon = () => (
  <svg className="w-4 h-4 text-rose-400" fill="currentColor" viewBox="0 0 24 24">
    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.25V10.9H6.46M7.86 6.74a1.65 1.65 0 1 0 0 3.3 1.65 1.65 0 0 0 0-3.3z"/>
  </svg>
);

const BriefcaseIcon = () => (
  <svg className="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  </svg>
);

const AcademicIcon = () => (
  <svg className="w-5 h-5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l9-5-9-5-9 5 9 5z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0112 20.055a11.952 11.952 0 01-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
  </svg>
);





const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";







export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("jobs");
  const [dailyJobs, setDailyJobs] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [isTriggeringSearch, setIsTriggeringSearch] = useState(false);

  // Mock Login State
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [mockLoginInput, setMockLoginInput] = useState("");

  // Time-based History Filter State ("today" | "monthly" | "yearly" | "all")
  const [historyFilter, setHistoryFilter] = useState<"today" | "monthly" | "yearly" | "all">("today");

  // Gmail Connection State
  const [isGmailConnected, setIsGmailConnected] = useState(false);
  const [gmailEmail, setGmailEmail] = useState("");
  const [showGmailModal, setShowGmailModal] = useState(false);
  const [smtpPassword, setSmtpPassword] = useState("");

  // API Keys & AI Provider Settings State
  const [llmProvider, setLlmProvider] = useState("openai");
  const [llmModel, setLlmModel] = useState("gpt-4o");
  const [customApiBase, setCustomApiBase] = useState("");
  const [openaiApiKey, setOpenaiApiKey] = useState("");
  const [googleClientId, setGoogleClientId] = useState("");
  const [googleClientSecret, setGoogleClientSecret] = useState("");
  const [adzunaAppId, setAdzunaAppId] = useState("");
  const [adzunaAppKey, setAdzunaAppKey] = useState("");
  const [joobleApiKey, setJoobleApiKey] = useState("");
  const [isSavingApiSettings, setIsSavingApiSettings] = useState(false);
  const [showApiKeys, setShowApiKeys] = useState(false);

  // User Personal Details & Social Links State
  const [userEmail, setUserEmail] = useState("");
  const [portfolioUrl, setPortfolioUrl] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [otherUrl, setOtherUrl] = useState("");
  const [targetRoles, setTargetRoles] = useState<string[]>([]);

  // Country Search Box & Selected Target Countries State
  const [countryQuery, setCountryQuery] = useState("");
  const [isCountryDropdownOpen, setIsCountryDropdownOpen] = useState(false);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);

  // International Career Preferences State
  const [workModePref, setWorkModePref] = useState<string>("Fully Remote (Worldwide)");
  const [selectedEmpTypes, setSelectedEmpTypes] = useState<string[]>(["Full-Time Jobs", "Internships & Traineeships"]);
  const [salaryPref, setSalaryPref] = useState<string>("$90,000 - $130,000 / year");
  const [experiencePref, setExperiencePref] = useState<string>("Mid-Level (2 - 5 Yrs)");
  const [visaSponsorshipPref, setVisaSponsorshipPref] = useState<string>("Visa Sponsorship Required");

  // Daily Application Goal Settings State
  const [dailyJobGoal, setDailyJobGoal] = useState<number>(5);
  const [dailyInternshipGoal, setDailyInternshipGoal] = useState<number>(3);
  const [autoFulfillEnabled, setAutoFulfillEnabled] = useState<boolean>(true);

  // AI Resume Extraction & ATS Metrics State
  const [uploadedResume, setUploadedResume] = useState<string | null>(null);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isAnalyzingATS, setIsAnalyzingATS] = useState(false);

  const [atsMetrics, setAtsMetrics] = useState({
    overall_score: 0,
    formatting_score: 0,
    keyword_density_score: 0,
    action_verbs_score: 0,
    section_completeness_score: 0,
    summary: "No resume PDF uploaded yet. Upload your CV to calculate real-time ATS compatibility scores.",
    strengths: [] as string[],
    missing_skills: [] as string[],
    formatting_suggestions: [] as string[],
    experience_improvements: [] as string[]
  });

  const [extractedProfile, setExtractedProfile] = useState({
    summary: "Upload a PDF resume to view AI-extracted summary, skills, experience, and project breakdown.",
    skills: [] as string[],
    experience: [] as any[],
    education: [] as any[],
    projects: [] as any[]
  });

  // Toast Notification State
  const [isUploading, setIsUploading] = useState(false);
  const [isApplyingId, setIsApplyingId] = useState<number | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);
  
  // RAG Agent Thinking UI State
  const [agentPhase, setAgentPhase] = useState<string | null>(null);
  const [agentLogs, setAgentLogs] = useState<string[]>([]);

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleSelectCountryFromDropdown = (countryName: string) => {
    if (selectedCountries.includes(countryName)) {
      showToast("Country already added to your target list.", "error");
    } else if (selectedCountries.length >= 10) {
      showToast("Maximum limit of 10 target countries reached!", "error");
    } else {
      setSelectedCountries(prev => [...prev, countryName]);
      showToast(`Added ${countryName} to target countries!`);
    }
    setCountryQuery("");
    setIsCountryDropdownOpen(false);
  };

  const handleRemoveCountry = (countryName: string) => {
    if (selectedCountries.length === 1) {
      showToast("Please keep at least 1 target country.", "error");
      return;
    }
    setSelectedCountries(prev => prev.filter(c => c !== countryName));
  };

  const toggleEmpType = (empType: string) => {
    setSelectedEmpTypes(prev => 
      prev.includes(empType) ? prev.filter(e => e !== empType) : [...prev, empType]
    );
  };

  useEffect(() => {
    const storedUsername = localStorage.getItem("mock_username");
    if (storedUsername) {
      setUsername(storedUsername);
      setIsLoggedIn(true);
    }
  }, []);

  // Fetch status & live data from backend APIs on mount or when logged in
  useEffect(() => {
    if (!isLoggedIn || !username) return;

    async function checkGmailStatus() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/gmail/status`, {
          headers: { "Authorization": `Bearer dev-mock-${username}` }
        });
        if (res.ok) {
          const data = await res.json();
          setIsGmailConnected(data.is_connected);
          if (data.connected_email) setGmailEmail(data.connected_email);
        }
      } catch (err) {
        console.log("Backend offline or local dev.");
      }
    }

    async function fetchUserSettings() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/users/settings`, {
          headers: { "Authorization": `Bearer dev-mock-${username}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (data.openai_api_key) setOpenaiApiKey(data.openai_api_key);
          if (data.google_client_id) setGoogleClientId(data.google_client_id);
          if (data.google_client_secret) setGoogleClientSecret(data.google_client_secret);
          if (data.adzuna_app_id) setAdzunaAppId(data.adzuna_app_id);
          if (data.adzuna_app_key) setAdzunaAppKey(data.adzuna_app_key);
          if (data.jooble_api_key) setJoobleApiKey(data.jooble_api_key);
          if (data.target_roles?.length) setTargetRoles(data.target_roles);
          if (data.target_countries?.length) setSelectedCountries(data.target_countries);
          if (data.work_mode_preference) setWorkModePref(data.work_mode_preference);
          if (data.employment_types?.length) setSelectedEmpTypes(data.employment_types);
          if (data.salary_preference) setSalaryPref(data.salary_preference);
          if (data.experience_level) setExperiencePref(data.experience_level);
          if (data.visa_sponsorship !== undefined) setVisaSponsorshipPref(data.visa_sponsorship ? "Visa Sponsorship Required" : "No Visa Needed (Authorized Work Permit)");
          if (data.daily_job_goal) setDailyJobGoal(data.daily_job_goal);
          if (data.daily_internship_goal) setDailyInternshipGoal(data.daily_internship_goal);
          if (data.auto_fulfill_enabled !== undefined) setAutoFulfillEnabled(data.auto_fulfill_enabled);
          if (data.email) setUserEmail(data.email);
          if (data.portfolio_url) setPortfolioUrl(data.portfolio_url);
          if (data.github_url) setGithubUrl(data.github_url);
          if (data.other_url) setOtherUrl(data.other_url);
        }
      } catch (err) {
        console.log("Local API settings initialized.");
      }
    }

    async function fetchOpportunities() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/search/opportunities?limit=50`, {
          headers: { "Authorization": `Bearer dev-mock-${username}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (data.items) setDailyJobs(data.items);
        }
      } catch (err) {
        console.log("No backend opportunities fetched.");
      }
    }

    async function fetchApplications() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/applications`, {
          headers: { "Authorization": `Bearer dev-mock-${username}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data)) setApplications(data);
        }
      } catch (err) {
        console.log("No backend applications fetched.");
      }
    }

    async function fetchResumeProfile() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/resumes/profile`, {
          headers: { "Authorization": `Bearer dev-mock-${username}` }
        });
        if (res.ok) {
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
        }
      } catch (err) {
        console.log("No stored resume profile fetched.");
      }
    }

    checkGmailStatus();
    fetchUserSettings();
    fetchOpportunities();
    fetchApplications();
    fetchResumeProfile();
  }, [isLoggedIn, username]);

  // Trigger Smart Job Search Agent
  const handleTriggerSearchAgent = async () => {
    setIsTriggeringSearch(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/search/trigger`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer dev-mock-${username}`
        },
        body: JSON.stringify({})
      });
      if (res.ok) {
        const data = await res.json();
        showToast(data.message || "Smart Job Search Agent completed multi-country scan!");
        const oppRes = await fetch(`${API_BASE}/api/v1/search/opportunities?limit=50`, {
          headers: { "Authorization": `Bearer dev-mock-${username}` }
        });
        if (oppRes.ok) {
          const oppData = await oppRes.json();
          if (oppData.items) setDailyJobs(oppData.items);
        }
      } else {
        if (res.status === 429) {
          showToast("Your API key limit has been reached! Please enter a new API key in Settings.", "error");
        } else {
          showToast("Failed to trigger Smart Search Agent.", "error");
        }
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to trigger Smart Search Agent.", "error");
    } finally {
      setIsTriggeringSearch(false);
    }
  };

  // Save API Settings Handler
  const handleSaveApiSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingApiSettings(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/users/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer dev-mock-${username}`
        },
        body: JSON.stringify({
          llm_provider: llmProvider,
          llm_model: llmModel,
          custom_api_base: customApiBase,
          openai_api_key: openaiApiKey,
          google_client_id: googleClientId,
          google_client_secret: googleClientSecret,
          adzuna_app_id: adzunaAppId,
          adzuna_app_key: adzunaAppKey,
          jooble_api_key: joobleApiKey,
          target_countries: selectedCountries
        })
      });
      if (res.ok) {
        showToast("Successfully saved API keys & integration credentials!");
      } else {
        showToast("Failed to save API settings.", "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to save API settings.", "error");
    } finally {
      setIsSavingApiSettings(false);
    }
  };

  // Handle Save Profile Details & Preferences
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingProfile(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/users/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer dev-mock-${username}`
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
          visa_sponsorship: visaSponsorshipPref,
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

  // Handle PDF Resume Upload & AI Analysis Trigger
    const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

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
        headers: {
          "Authorization": `Bearer ${token}`
        },
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
      }, 2000); // leave the complete log visible for 2s
    }
  };

  // Re-run ATS Audit
  const handleRunAtsCheck = async () => {
    setIsAnalyzingATS(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/resumes/ats-check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer dev-mock-${username}`
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

  // Handle Auto-Apply via Email
  const handleAutoApply = async (job: any) => {
    setIsApplyingId(job.id);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auto-apply/send-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer dev-mock-${username}`
        },
        body: JSON.stringify({ job_id: job.id })
      });

      const newApp = {
        id: Date.now(),
        title: job.title,
        company: job.company,
        company_email: job.company_email,
        opportunity_type: job.opportunity_type || "job",
        status: "Sent via Gmail",
        gmail_message_id: `msg_${Date.now().toString(16)}`,
        applied_at: new Date().toISOString(),
        notes: `Sent via connected Gmail to ${job.company_email}`
      };

      if (res.ok) {
        const data = await res.json();
        if (data.gmail_message_id) newApp.gmail_message_id = data.gmail_message_id;
        showToast(data.message || `Applied to ${job.company}! Check your Gmail Sent folder.`);
        setApplications(prev => [newApp, ...prev]);
      } else {
        showToast(`Failed to send application email to ${job.company_email}.`, "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : `Failed to send application email to ${job.company_email}.`, "error");
    } finally {
      setIsApplyingId(null);
    }
  };

  const todayStr = new Date().toISOString().split("T")[0];
  const monthStr = todayStr.substring(0, 7);
  const yearStr = todayStr.substring(0, 4);

  const todayApps = applications.filter(app => (app.applied_at || "").startsWith(todayStr));
  const todayJobsCount = todayApps.filter(app => app.opportunity_type === "job").length;
  const todayInternshipsCount = todayApps.filter(app => app.opportunity_type === "internship").length;
  const totalTodayApplied = todayApps.length;
  const totalDailyTarget = dailyJobGoal + dailyInternshipGoal;
  const overallGoalProgress = Math.min(100, Math.round((totalTodayApplied / (totalDailyTarget || 1)) * 100));

  const monthlyApps = applications.filter(app => (app.applied_at || "").startsWith(monthStr));
  const yearlyApps = applications.filter(app => (app.applied_at || "").startsWith(yearStr));

  const filteredApplications = applications.filter(app => {
    const appliedStr = app.applied_at || "";
    if (historyFilter === "today") return appliedStr.startsWith(todayStr);
    if (historyFilter === "monthly") return appliedStr.startsWith(monthStr);
    if (historyFilter === "yearly") return appliedStr.startsWith(yearStr);
    return true;
  });

  const filteredDailyJobs = dailyJobs.filter(job => {
    const matchesEmpType = selectedEmpTypes.length === 0 || 
      (job.opportunity_type === "job" && selectedEmpTypes.includes("Full-Time Jobs")) ||
      (job.opportunity_type === "internship" && selectedEmpTypes.includes("Internships & Traineeships"));
    return matchesEmpType;
  });

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-[#090a0f] bg-grid-omni bg-coral-glow text-slate-100 font-sans flex items-center justify-center p-4">
        <div className="glass-panel p-8 rounded-2xl max-w-md w-full text-center space-y-6 border border-white/10 shadow-2xl relative overflow-hidden">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-rose-600/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="relative z-10">
            <SparklesIcon className="w-16 h-16 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Login to AutoApply AI</h2>
            <p className="text-slate-400 text-sm mb-6">Enter a unique username to access your isolated workspace. This keeps your API keys and data private.</p>
            <input
              type="text"
              value={mockLoginInput}
              onChange={(e) => setMockLoginInput(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-700/50 focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50 outline-none text-white rounded-xl px-4 py-3 mb-4 transition-all placeholder:text-slate-500"
              placeholder="Username (e.g. ali123)"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && mockLoginInput.trim()) {
                  localStorage.setItem("mock_username", mockLoginInput.trim());
                  setUsername(mockLoginInput.trim());
                  setIsLoggedIn(true);
                }
              }}
            />
            <button
              onClick={() => {
                if (mockLoginInput.trim()) {
                  localStorage.setItem("mock_username", mockLoginInput.trim());
                  setUsername(mockLoginInput.trim());
                  setIsLoggedIn(true);
                }
              }}
              className="w-full btn-red-glow text-white font-bold py-3 px-4 rounded-xl shadow-lg transition-all"
            >
              Enter Workspace
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090a0f] bg-grid-omni bg-coral-glow text-slate-100 font-sans selection:bg-rose-500 selection:text-white">
      {notification && (
        <Toast notification={notification} />
      )}

      <header className="border-b border-white/10 bg-[#090a0f]/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 bg-rose-500 transform rotate-45 rounded-sm shadow-[0_0_12px_rgba(244,63,94,0.8)]"></div>
            <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
              AutoApply<span className="text-rose-500 font-normal">AI</span>
            </h1>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <button onClick={() => setActiveTab("jobs")} className={`hover:text-white transition-colors ${activeTab === "jobs" ? "text-rose-400 font-semibold" : ""}`}>
              Opportunities
            </button>
            <button onClick={() => setActiveTab("history")} className={`hover:text-white transition-colors ${activeTab === "history" ? "text-rose-400 font-semibold" : ""}`}>
              Gmail Proofs
            </button>
            <button onClick={() => setActiveTab("profile")} className={`hover:text-white transition-colors ${activeTab === "profile" ? "text-rose-400 font-semibold" : ""}`}>
              CV & Profile
            </button>
            <button onClick={() => setActiveTab("settings")} className={`hover:text-white transition-colors ${activeTab === "settings" ? "text-rose-400 font-semibold" : ""}`}>
              API Vault
            </button>
          </nav>

          <div className="flex items-center gap-3">
            {isGmailConnected && (
              <div className="hidden sm:flex items-center gap-2 bg-rose-950/40 border border-rose-500/30 px-3.5 py-1.5 rounded-full text-xs text-rose-300">
                <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping"></span>
                <span>Gmail: <strong className="text-rose-200">{gmailEmail}</strong></span>
              </div>
            )}
            <button onClick={() => setActiveTab("settings")} className="btn-red-glow text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center gap-2">
              <KeyIcon />
              <span>API Vault</span>
              <span>→</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex border-b border-white/10 mb-8 overflow-x-auto gap-2">
          <button onClick={() => setActiveTab("jobs")} className={`pb-3.5 px-6 font-semibold text-sm border-b-2 whitespace-nowrap transition-all flex items-center gap-2.5 rounded-t-xl ${activeTab === "jobs" ? "border-rose-400 text-rose-300 bg-rose-950/20 shadow-[0_4px_20px_-4px_rgba(244,63,94,0.3)]" : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"}`}>
            <DashboardIcon />
            <span>Daily Opportunities</span>
            <span className="ml-1 bg-rose-950/80 text-rose-300 text-xs px-2.5 py-0.5 rounded-full border border-rose-500/30 font-mono">
              {filteredDailyJobs.length}
            </span>
          </button>
          <button onClick={() => setActiveTab("history")} className={`pb-3.5 px-6 font-semibold text-sm border-b-2 whitespace-nowrap transition-all flex items-center gap-2.5 rounded-t-xl ${activeTab === "history" ? "border-rose-400 text-rose-300 bg-rose-950/20 shadow-[0_4px_20px_-4px_rgba(244,63,94,0.3)]" : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"}`}>
            <GmailIcon />
            <span>Applications & Gmail Proofs</span>
            <span className="ml-1 bg-rose-950/80 text-rose-300 border border-rose-500/30 text-xs px-2.5 py-0.5 rounded-full font-mono">
              {applications.length}
            </span>
          </button>
          <button onClick={() => setActiveTab("profile")} className={`pb-3.5 px-6 font-semibold text-sm border-b-2 whitespace-nowrap transition-all flex items-center gap-2.5 rounded-t-xl ${activeTab === "profile" ? "border-rose-400 text-rose-300 bg-rose-950/20 shadow-[0_4px_20px_-4px_rgba(244,63,94,0.3)]" : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"}`}>
            <UserIcon />
            <span>User Profile & CV Management</span>
          </button>
        </div>

        {activeTab === "jobs" && (
          <JobsTab
            filteredDailyJobs={filteredDailyJobs}
            selectedCountries={selectedCountries}
            isTriggeringSearch={isTriggeringSearch}
            handleTriggerSearchAgent={handleTriggerSearchAgent}
            isApplyingId={isApplyingId}
            handleAutoApply={handleAutoApply}
          />
        )}
        {activeTab === "profile" && (
          <ProfileTab
            userEmail={userEmail}
            setUserEmail={setUserEmail}
            portfolioUrl={portfolioUrl}
            setPortfolioUrl={setPortfolioUrl}
            githubUrl={githubUrl}
            setGithubUrl={setGithubUrl}
            otherUrl={otherUrl}
            setOtherUrl={setOtherUrl}
            targetRoles={targetRoles}
            setTargetRoles={setTargetRoles}
            countryQuery={countryQuery}
            setCountryQuery={setCountryQuery}
            isCountryDropdownOpen={isCountryDropdownOpen}
            setIsCountryDropdownOpen={setIsCountryDropdownOpen}
            selectedCountries={selectedCountries}
            handleSelectCountryFromDropdown={handleSelectCountryFromDropdown}
            handleRemoveCountry={handleRemoveCountry}
            workModePref={workModePref}
            setWorkModePref={setWorkModePref}
            salaryPref={salaryPref}
            setSalaryPref={setSalaryPref}
            experiencePref={experiencePref}
            setExperiencePref={setExperiencePref}
            visaSponsorshipPref={visaSponsorshipPref}
            setVisaSponsorshipPref={setVisaSponsorshipPref}
            selectedEmpTypes={selectedEmpTypes}
            toggleEmpType={toggleEmpType}
            dailyJobGoal={dailyJobGoal}
            setDailyJobGoal={setDailyJobGoal}
            dailyInternshipGoal={dailyInternshipGoal}
            setDailyInternshipGoal={setDailyInternshipGoal}
            totalTodayApplied={totalTodayApplied}
            totalDailyTarget={totalDailyTarget}
            overallGoalProgress={overallGoalProgress}
            todayJobsCount={todayJobsCount}
            todayInternshipsCount={todayInternshipsCount}
            isSavingProfile={isSavingProfile}
            handleSaveProfile={handleSaveProfile}
            isUploading={isUploading}
            agentPhase={agentPhase}
            agentLogs={agentLogs}
            uploadedResume={uploadedResume}
            handleResumeUpload={handleResumeUpload}
            extractedProfile={extractedProfile}
            atsMetrics={atsMetrics}
            handleRunAtsCheck={handleRunAtsCheck}
            isAnalyzingATS={isAnalyzingATS}
          />
        )}
        {activeTab === "history" && (
          <HistoryTab
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
        )}
        {activeTab === "settings" && (
          <SettingsTab
            showApiKeys={showApiKeys}
            setShowApiKeys={setShowApiKeys}
            llmProvider={llmProvider}
            setLlmProvider={setLlmProvider}
            llmModel={llmModel}
            setLlmModel={setLlmModel}
            customApiBase={customApiBase}
            setCustomApiBase={setCustomApiBase}
            openaiApiKey={openaiApiKey}
            setOpenaiApiKey={setOpenaiApiKey}
            googleClientId={googleClientId}
            setGoogleClientId={setGoogleClientId}
            googleClientSecret={googleClientSecret}
            setGoogleClientSecret={setGoogleClientSecret}
            isGmailConnected={isGmailConnected}
            gmailEmail={gmailEmail}
            setShowGmailModal={setShowGmailModal}
            adzunaAppId={adzunaAppId}
            setAdzunaAppId={setAdzunaAppId}
            adzunaAppKey={adzunaAppKey}
            setAdzunaAppKey={setAdzunaAppKey}
            joobleApiKey={joobleApiKey}
            setJoobleApiKey={setJoobleApiKey}
            isSavingApiSettings={isSavingApiSettings}
            handleSaveApiSettings={handleSaveApiSettings}
          />
        )}
      </main>

      {showGmailModal && (
        <GmailModal
          API_BASE={API_BASE}
          showGmailModal={showGmailModal}
          gmailEmail={gmailEmail}
          setGmailEmail={setGmailEmail}
          smtpPassword={smtpPassword}
          setSmtpPassword={setSmtpPassword}
          setShowGmailModal={setShowGmailModal}
          setIsGmailConnected={setIsGmailConnected}
          showToast={showToast}
          username={username}
        />
      )}
    </div>
  );
}
