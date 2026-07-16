"use client";

import React, { useState, useEffect } from "react";

// Standard SVG Icons (inline to prevent dependency install lags)
const DashboardIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" />
  </svg>
);

const AppListIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const InboxIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 01-2 2H6a2 2 0 01-2-2m16 0l-3.586 3.586a2 2 0 01-2.828 0L4 13m16 0h-3m-9 0H3" />
  </svg>
);

const SearchIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const UploadIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
  </svg>
);

const SparklesIcon = () => (
  <svg className="w-5 h-5 text-purple-600 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
  </svg>
);

// Fallback Mock Data
const MOCK_APPLICATIONS = [
  { id: 1, title: "Senior React Developer", company: "Stripe", opportunity_type: "job", status: "Matched", url: "https://stripe.com/jobs", applied_at: null, cover_letter: "", notes: "Match score: 92%" },
  { id: 2, title: "Backend FastAPI Engineer", company: "Vercel", opportunity_type: "job", status: "Applied", url: "https://vercel.com/jobs", applied_at: "2026-07-15T18:22:16Z", cover_letter: "Dear Hiring Team, I am writing to express interest...", notes: "Successfully applied via browser automation." },
  { id: 3, title: "Full-Stack Software Developer", company: "OpenAI", opportunity_type: "job", status: "Failed", url: "https://openai.com/jobs", applied_at: "2026-07-14T10:05:00Z", cover_letter: "", notes: "Form load timeout during Playwright fill." },
  { id: 4, title: "Developer Advocate", company: "Cloudflare", opportunity_type: "job", status: "Matched", url: "https://cloudflare.com/jobs", applied_at: null, cover_letter: "", notes: "Match score: 86%" }
];

const MOCK_DRAFTS = [
  { id: 1, sender: "hr-team@google.com", subject: "Google Developer Role Follow-up", body: "Hi Alex, We reviewed your application and would like to invite you for a 30-minute introductory phone screen next week. Let us know your availability.", classification: "Interview Invite", response_draft: "Hi Google Team,\n\nThank you so much for the invitation! I am very excited to speak with you. I am available next Monday morning between 9:00 AM and 11:30 AM EST, or Tuesday afternoon between 1:00 PM and 4:00 PM EST. Please let me know if any of these slots suit your schedule.\n\nBest regards,\nAlex", status: "Pending Review", received_at: "2026-07-15T19:00:00Z" },
  { id: 2, sender: "recruiting@stripe.com", subject: "Stripe Systems Engineer Update", body: "Hello, Thank you for your time. Unfortunately, we have decided not to move forward with your candidacy at this time.", classification: "Rejection", response_draft: "Dear Stripe Team,\n\nThank you for keeping me updated. While disappointed, I appreciate your consideration and hope to remain in contact for future opportunities.\n\nBest regards,\nAlex", status: "Pending Review", received_at: "2026-07-14T15:20:00Z" }
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://autoapplyai-00e737b6d760.herokuapp.com";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [applications, setApplications] = useState(MOCK_APPLICATIONS);
  const [drafts, setDrafts] = useState(MOCK_DRAFTS);
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [isCrawlRunning, setIsCrawlRunning] = useState(false);
  const [isMatchingRunning, setIsMatchingRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([
    "System startup: All agents initialized.",
    "Search Agent: Crawled Greenhouse and Jooble. Found 4 matching job prospects.",
    "Matching Agent: Analyzed resumes vector index. 2 jobs exceeded threshold."
  ]);
  const [applyingId, setApplyingId] = useState<number | null>(null);

  // Resume Upload Fields State
  const [uploadedResume, setUploadedResume] = useState<string | null>("resume_alex_final.pdf");
  const [profileSkills, setProfileSkills] = useState(["React", "TypeScript", "FastAPI", "Python", "SQL"]);
  const [profileExperience, setProfileExperience] = useState([
    { title: "Software Engineer", company: "TechCorp", duration: "2 years" },
    { title: "Frontend Intern", company: "WebStudio", duration: "6 months" }
  ]);

  // Attempt to fetch live data from FastAPI Backend
  useEffect(() => {
    async function fetchBackendData() {
      try {
        const appsRes = await fetch(`${API_BASE}/api/v1/applications`, {
          headers: { "Authorization": "Bearer dev-mock-matcher_test_uid" }
        });
        if (appsRes.ok) {
          const appsData = await appsRes.json();
          if (appsData.length > 0) {
            setApplications(appsData);
            setIsDemoMode(false);
          }
        }
        
        const draftsRes = await fetch(`${API_BASE}/api/v1/emails/drafts`, {
          headers: { "Authorization": "Bearer dev-mock-matcher_test_uid" }
        });
        if (draftsRes.ok) {
          const draftsData = await draftsRes.json();
          if (draftsData.length > 0) {
            setDrafts(draftsData);
          }
        }

        const profileRes = await fetch(`${API_BASE}/api/v1/resumes/profile`, {
          headers: { "Authorization": "Bearer dev-mock-matcher_test_uid" }
        });
        if (profileRes.ok) {
          const profileData = await profileRes.json();
          setUploadedResume(profileData.resume_url ? profileData.resume_url.split("/").pop() : null);
          setProfileSkills(profileData.skills || []);
          setProfileExperience(profileData.experience || []);
        }
      } catch (err) {
        console.log("FastAPI backend offline. Defaulting to mock demo mode.");
      }
    }
    fetchBackendData();
  }, []);

  // Trigger search background crawl
  const handleTriggerSearch = async () => {
    setIsCrawlRunning(true);
    setLogs(prev => [...prev, "Search Agent: Triggering manual crawl on backend..."]);
    try {
      const res = await fetch(`${API_BASE}/api/v1/search/trigger`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer dev-mock-matcher_test_uid"
        },
        body: JSON.stringify({ query: "Python Developer", country: "us" })
      });
      if (res.ok) {
        const data = await res.json();
        setLogs(prev => [...prev, `Search Agent: Crawl finished. ${data.message}`]);
      } else {
        const errData = await res.json();
        setLogs(prev => [...prev, `Search Agent: Crawl failed. ${errData.detail || "Server error"}`]);
      }
    } catch (err) {
      setLogs(prev => [...prev, `Search Agent: Network error during crawl.`]);
    } finally {
      setIsCrawlRunning(false);
    }
  };

  // Trigger matching algorithm run
  const handleTriggerMatching = async () => {
    setIsMatchingRunning(true);
    setLogs(prev => [...prev, "Matching Agent: Running constraint check & semantic analysis..."]);
    try {
      const res = await fetch(`${API_BASE}/api/v1/matching/run`, {
        method: "POST",
        headers: {
          "Authorization": "Bearer dev-mock-matcher_test_uid"
        }
      });
      if (res.ok) {
        const data = await res.json();
        setLogs(prev => [...prev, `Matching Agent: Finished. ${data.message}`]);
        // Refresh application matches
        const appsRes = await fetch(`${API_BASE}/api/v1/applications`, {
          headers: { "Authorization": "Bearer dev-mock-matcher_test_uid" }
        });
        if (appsRes.ok) {
          const appsData = await appsRes.json();
          setApplications(appsData);
          setIsDemoMode(false);
        }
      } else {
        const errData = await res.json();
        setLogs(prev => [...prev, `Matching Agent: Pipeline failed. ${errData.detail || "Server error"}`]);
      }
    } catch (err) {
      setLogs(prev => [...prev, `Matching Agent: Network error during evaluation.`]);
    } finally {
      setIsMatchingRunning(false);
    }
  };

  // Submit dynamic application with Playwright backend trigger
  const handleApply = async (appId: number) => {
    setApplyingId(appId);
    setLogs(prev => [...prev, `Application Agent: Initiating Playwright form-filler for App ID ${appId}...`]);
    
    // Update state to Applying
    setApplications(prev => 
      prev.map(app => app.id === appId ? { ...app, status: "Applying" } : app)
    );

    try {
      const res = await fetch(`${API_BASE}/api/v1/applications/${appId}/apply`, {
        method: "POST",
        headers: {
          "Authorization": "Bearer dev-mock-matcher_test_uid"
        }
      });
      if (res.ok) {
        setLogs(prev => [...prev, `Application Agent: Successfully queued form-filler for App ID ${appId}.`]);
        // Set up polling for status update
        let attempts = 0;
        const interval = setInterval(async () => {
          attempts += 1;
          const checkRes = await fetch(`${API_BASE}/api/v1/applications/${appId}`, {
            headers: { "Authorization": "Bearer dev-mock-matcher_test_uid" }
          });
          if (checkRes.ok) {
            const appData = await checkRes.json();
            if (appData.status !== "Applying" || attempts > 10) {
              clearInterval(interval);
              setApplyingId(null);
              setApplications(prev => 
                prev.map(app => app.id === appId ? { 
                  ...app, 
                  status: appData.status,
                  applied_at: appData.applied_at,
                  notes: appData.notes
                } : app)
              );
              setLogs(prev => [...prev, `Application Agent: Application status resolved to '${appData.status}' for App ID ${appId}.`]);
            }
          } else {
            clearInterval(interval);
            setApplyingId(null);
          }
        }, 3000);
      } else {
        const errData = await res.json();
        setLogs(prev => [...prev, `Application Agent: Failed to queue application. ${errData.detail || "Server error"}`]);
        setApplyingId(null);
        // Revert status
        setApplications(prev => 
          prev.map(app => app.id === appId ? { ...app, status: "Matched" } : app)
        );
      }
    } catch (err) {
      setLogs(prev => [...prev, `Application Agent: Network error during apply.`]);
      setApplyingId(null);
      setApplications(prev => 
        prev.map(app => app.id === appId ? { ...app, status: "Matched" } : app)
      );
    }
  };

  // Approve Email Draft
  const handleApproveDraft = (draftId: number) => {
    setDrafts(prev =>
      prev.map(d => d.id === draftId ? { ...d, status: "Approved" } : d)
    );
    setLogs(prev => [...prev, `Email Agent: Draft ID ${draftId} approved and scheduled to send.`]);
  };

  // Discard Email Draft
  const handleDiscardDraft = (draftId: number) => {
    setDrafts(prev =>
      prev.map(d => d.id === draftId ? { ...d, status: "Dismissed" } : d)
    );
    setLogs(prev => [...prev, `Email Agent: Draft ID ${draftId} dismissed.`]);
  };

  // Resume Upload Handler
  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const filename = file.name;
      setUploadedResume(filename);
      setLogs(prev => [...prev, `Resume Agent: Uploaded PDF file '${filename}'. Starting parsing & ChromaDB embedding generation...`]);
      
      const formData = new FormData();
      formData.append("file", file);
      
      try {
        const res = await fetch(`${API_BASE}/api/v1/users/resume`, {
          method: "POST",
          headers: {
            "Authorization": "Bearer dev-mock-matcher_test_uid"
          },
          body: formData
        });
        
        if (res.ok) {
          setLogs(prev => [...prev, "Resume Agent: Resume parsing completed successfully. Index updated in local vector store."]);
          // Fetch updated profile
          const profileRes = await fetch(`${API_BASE}/api/v1/resumes/profile`, {
            headers: { "Authorization": "Bearer dev-mock-matcher_test_uid" }
          });
          if (profileRes.ok) {
            const profileData = await profileRes.json();
            setProfileSkills(profileData.skills || []);
            setProfileExperience(profileData.experience || []);
            setLogs(prev => [...prev, `Resume Agent: Extracted ${profileData.skills.length} skills and ${profileData.experience.length} experiences.`]);
          }
        } else {
          const errData = await res.json();
          setLogs(prev => [...prev, `Resume Agent: Parse failed. ${errData.detail || "Server error"}`]);
        }
      } catch (err) {
        setLogs(prev => [...prev, `Resume Agent: Network error during upload.`]);
      }
    }
  };

  // Stats Computations
  const totalApplied = applications.filter(a => a.status === "Applied").length;
  const totalMatched = applications.filter(a => a.status === "Matched").length;
  const pendingInboxCount = drafts.filter(d => d.status === "Pending Review").length;

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 flex flex-col">
      {/* Top Banner Header */}
      <header className="bg-white border-b border-slate-100 sticky top-0 z-10 shadow-sm shadow-purple-50/50">
        <div className="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-purple-200">
              A
            </div>
            <div>
              <h1 className="font-bold text-xl tracking-tight text-slate-900 flex items-center gap-2">
                AutoApplyAI <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">Agentic Suite</span>
              </h1>
              <p className="text-xs text-slate-400">Automate your career applications lifecycle</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {isDemoMode && (
              <span className="text-xs px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-700 font-medium animate-pulse flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Mock Demo Mode (Backend Offline)
              </span>
            )}
            <div className="flex items-center gap-2 bg-slate-100 rounded-lg p-1">
              <span className="text-xs text-slate-500 font-medium px-3">Alex Rivera</span>
              <div className="w-8 h-8 rounded-full bg-purple-200 text-purple-800 font-semibold text-xs flex items-center justify-center">
                AR
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid Content */}
      <div className="max-w-7xl w-full mx-auto px-6 py-8 flex flex-col md:flex-row gap-8 flex-1">
        {/* Navigation Sidebar */}
        <aside className="w-full md:w-64 shrink-0 flex flex-col gap-2">
          <button
            onClick={() => setActiveTab("overview")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === "overview"
                ? "bg-purple-600 text-white shadow-md shadow-purple-200"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
            }`}
          >
            <DashboardIcon /> Overview Dashboard
          </button>
          <button
            onClick={() => setActiveTab("applications")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === "applications"
                ? "bg-purple-600 text-white shadow-md shadow-purple-200"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
            }`}
          >
            <AppListIcon /> Matches & Applies
            <span className="ml-auto bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full font-bold">
              {totalMatched}
            </span>
          </button>
          <button
            onClick={() => setActiveTab("inbox")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === "inbox"
                ? "bg-purple-600 text-white shadow-md shadow-purple-200"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
            }`}
          >
            <InboxIcon /> Recruiter Inbox
            {pendingInboxCount > 0 && (
              <span className="ml-auto bg-rose-100 text-rose-700 text-xs px-2 py-0.5 rounded-full font-bold">
                {pendingInboxCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab("crawlers")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === "crawlers"
                ? "bg-purple-600 text-white shadow-md shadow-purple-200"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
            }`}
          >
            <SearchIcon /> Agent Actions
          </button>
          <button
            onClick={() => setActiveTab("resume")}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
              activeTab === "resume"
                ? "bg-purple-600 text-white shadow-md shadow-purple-200"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
            }`}
          >
            <UploadIcon /> Resume & Profile
          </button>

          <hr className="my-4 border-slate-200" />

          {/* Quick Logs Container */}
          <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-sm shadow-purple-50/50 flex flex-col gap-3">
            <h3 className="font-bold text-xs text-slate-400 uppercase tracking-wider">Live Agent Log</h3>
            <div className="flex flex-col gap-2 max-h-48 overflow-y-auto">
              {logs.map((log, index) => (
                <div key={index} className="text-xxs leading-relaxed font-mono text-slate-500 bg-slate-50 p-2 rounded-lg border border-slate-100">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Tab content panels */}
        <main className="flex-1 flex flex-col gap-8">
          {activeTab === "overview" && (
            <div className="flex flex-col gap-8">
              {/* Target Banner Progress Bar */}
              <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 relative overflow-hidden">
                <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 w-32 h-32 rounded-full bg-purple-50 animate-pulse"></div>
                <div className="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <SparklesIcon />
                      <h2 className="text-lg font-bold text-slate-900">Weekly Target Progress</h2>
                    </div>
                    <p className="text-sm text-slate-500">Auto-Apply agent automatically manages your daily targets.</p>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-extrabold text-purple-600">{totalApplied}</span>
                    <span className="text-slate-400 font-medium"> / 20 applied</span>
                  </div>
                </div>
                {/* Progress bar */}
                <div className="w-full bg-slate-100 h-3 rounded-full mt-6 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-indigo-600 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((totalApplied / 20) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Stats Counters Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 hover:shadow-md hover:shadow-purple-100/50 hover:-translate-y-0.5 duration-300 flex flex-col gap-2">
                  <span className="text-sm font-semibold text-slate-400">Total Matches Found</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-extrabold text-slate-900">{applications.length}</span>
                    <span className="text-xs text-purple-600 font-bold bg-purple-50 px-2 py-0.5 rounded-full">+4 today</span>
                  </div>
                </div>
                <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 hover:shadow-md hover:shadow-purple-100/50 hover:-translate-y-0.5 duration-300 flex flex-col gap-2">
                  <span className="text-sm font-semibold text-slate-400">Total Applications Submitted</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-extrabold text-slate-900">{totalApplied}</span>
                    <span className="text-xs text-indigo-600 font-bold bg-indigo-50 px-2 py-0.5 rounded-full">60% success</span>
                  </div>
                </div>
                <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 hover:shadow-md hover:shadow-purple-100/50 hover:-translate-y-0.5 duration-300 flex flex-col gap-2">
                  <span className="text-sm font-semibold text-slate-400">Pending Recruiter Invites</span>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-extrabold text-rose-600">{pendingInboxCount}</span>
                    <span className="text-xs text-rose-600 font-bold bg-rose-50 px-2 py-0.5 rounded-full">requires reply</span>
                  </div>
                </div>
              </div>

              {/* Action Board Split Section */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Matched opportunities */}
                <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 lg:col-span-2 flex flex-col gap-4">
                  <h3 className="font-bold text-slate-900 text-base">Recommended Matches</h3>
                  <div className="flex flex-col gap-4">
                    {applications.filter(a => a.status === "Matched").map(app => (
                      <div key={app.id} className="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:bg-slate-50 duration-200">
                        <div className="flex flex-col gap-1">
                          <span className="font-semibold text-sm text-slate-900">{app.title}</span>
                          <div className="flex items-center gap-2 text-xs text-slate-400 font-medium">
                            <span>{app.company}</span>
                            <span>•</span>
                            <span className="text-purple-600 font-semibold">{app.notes}</span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleApply(app.id)}
                          className="bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs px-4 py-2 rounded-lg transition shadow-md shadow-purple-100 flex items-center gap-1.5"
                        >
                          Auto-Apply
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Email Tasks Overview */}
                <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 flex flex-col gap-4">
                  <h3 className="font-bold text-slate-900 text-base">Inbox Alerts</h3>
                  <div className="flex flex-col gap-4">
                    {drafts.filter(d => d.status === "Pending Review").slice(0, 2).map(draft => (
                      <div key={draft.id} className="flex flex-col gap-2 p-4 rounded-xl border border-slate-100 bg-rose-50/30">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded-full">{draft.classification}</span>
                          <span className="text-xxs text-slate-400 font-medium">10m ago</span>
                        </div>
                        <span className="text-xs font-semibold text-slate-900">{draft.sender}</span>
                        <p className="text-xxs text-slate-500 line-clamp-2">{draft.body}</p>
                        <button
                          onClick={() => setActiveTab("inbox")}
                          className="text-purple-600 hover:text-purple-800 text-xs font-bold mt-2 text-left"
                        >
                          Review draft response →
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "applications" && (
            <div className="bg-white border border-slate-100 rounded-2xl shadow-sm shadow-purple-50/50 overflow-hidden flex flex-col">
              <div className="p-6 border-b border-slate-100 flex justify-between items-center flex-wrap gap-4">
                <div>
                  <h2 className="font-bold text-lg text-slate-900">Application Submissions Logs</h2>
                  <p className="text-xs text-slate-400">Review status and audit history of auto-generated applies.</p>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-400 text-xs font-semibold border-b border-slate-100">
                      <th className="px-6 py-4">Job Title</th>
                      <th className="px-6 py-4">Company</th>
                      <th className="px-6 py-4">Type</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4">Verification Logs</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    {applications.map(app => (
                      <tr key={app.id} className="hover:bg-slate-50/50 duration-150">
                        <td className="px-6 py-4 font-semibold text-slate-900">{app.title}</td>
                        <td className="px-6 py-4 font-medium text-slate-600">{app.company}</td>
                        <td className="px-6 py-4">
                          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600">
                            {app.opportunity_type}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                            app.status === "Applied" ? "bg-emerald-100 text-emerald-700" :
                            app.status === "Applying" ? "bg-amber-100 text-amber-700 animate-pulse" :
                            app.status === "Failed" ? "bg-rose-100 text-rose-700" :
                            "bg-purple-100 text-purple-700"
                          }`}>
                            {app.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-xs text-slate-500 max-w-xs truncate">{app.notes}</td>
                        <td className="px-6 py-4 text-right">
                          {app.status === "Matched" ? (
                            <button
                              disabled={applyingId !== null}
                              onClick={() => handleApply(app.id)}
                              className="bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs px-3.5 py-1.5 rounded-lg transition duration-200 shadow-md shadow-purple-50 disabled:bg-purple-300"
                            >
                              Apply Now
                            </button>
                          ) : (
                            <span className="text-xs text-slate-400 font-medium">Synced</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === "inbox" && (
            <div className="flex flex-col gap-6">
              <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 flex flex-col gap-2">
                <h2 className="font-bold text-lg text-slate-900">Interviews & Recruiter Drafts</h2>
                <p className="text-xs text-slate-400">Recruiter replies are monitored, classified, and response drafts are held for approval before sending.</p>
              </div>

              {drafts.map(draft => (
                <div key={draft.id} className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 flex flex-col gap-6">
                  {/* Draft Header */}
                  <div className="flex justify-between items-start flex-wrap gap-4 border-b border-slate-100 pb-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-3">
                        <span className="font-bold text-slate-900 text-sm">{draft.sender}</span>
                        <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                          draft.classification === "Interview Invite" ? "bg-emerald-100 text-emerald-700" :
                          "bg-rose-100 text-rose-700"
                        }`}>
                          {draft.classification}
                        </span>
                      </div>
                      <span className="text-xs font-semibold text-slate-400">Subject: {draft.subject}</span>
                    </div>
                    <span className="text-xs text-slate-400 font-medium">Received at: {draft.received_at.substring(0, 10)}</span>
                  </div>

                  {/* Body Split */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Received email */}
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                      <h4 className="font-bold text-xs text-slate-400 uppercase tracking-wider mb-2">Received Email Body</h4>
                      <p className="text-xs text-slate-600 whitespace-pre-line leading-relaxed">{draft.body}</p>
                    </div>

                    {/* Response Draft */}
                    <div className="flex flex-col gap-4">
                      <h4 className="font-bold text-xs text-purple-500 uppercase tracking-wider">Suggested Reply Draft</h4>
                      <textarea
                        disabled={draft.status !== "Pending Review"}
                        className="w-full h-40 bg-white border border-slate-200 rounded-xl p-4 text-xs font-medium focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none leading-relaxed text-slate-700"
                        value={draft.response_draft}
                        onChange={(e) => {
                          const val = e.target.value;
                          setDrafts(prev => prev.map(d => d.id === draft.id ? { ...d, response_draft: val } : d));
                        }}
                      />
                      {draft.status === "Pending Review" ? (
                        <div className="flex gap-3 justify-end">
                          <button
                            onClick={() => handleDiscardDraft(draft.id)}
                            className="border border-slate-200 hover:bg-slate-50 text-slate-600 font-semibold text-xs px-4 py-2 rounded-lg transition"
                          >
                            Dismiss Reply
                          </button>
                          <button
                            onClick={() => handleApproveDraft(draft.id)}
                            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs px-4 py-2 rounded-lg transition shadow-md shadow-purple-100"
                          >
                            Approve & Send
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-end gap-2 text-xs font-bold text-purple-700">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                          </svg>
                          Status: {draft.status}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "crawlers" && (
            <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 flex flex-col gap-6">
              <div className="border-b border-slate-100 pb-4">
                <h2 className="font-bold text-lg text-slate-900">Background Tasks & Crawlers</h2>
                <p className="text-xs text-slate-400">Trigger search crawlers to scan job listings, or evaluate matches against your resume profile.</p>
              </div>

              {/* Grid actions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="p-6 rounded-xl border border-slate-100 flex flex-col gap-4">
                  <h3 className="font-bold text-sm text-slate-900">Search Agent Crawler</h3>
                  <p className="text-xs text-slate-400">Triggers parallel crawlers across Adzuna, Jooble, Greenhouse boards, and Lever public boards.</p>
                  <button
                    disabled={isCrawlRunning}
                    onClick={handleTriggerSearch}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs px-4 py-2.5 rounded-lg transition disabled:bg-purple-300"
                  >
                    {isCrawlRunning ? "Crawling Board APIs..." : "Trigger Manual Search Crawl"}
                  </button>
                </div>

                <div className="p-6 rounded-xl border border-slate-100 flex flex-col gap-4">
                  <h3 className="font-bold text-sm text-slate-900">Matching Agent Engine</h3>
                  <p className="text-xs text-slate-400">Runs location constraints, remote filters, offered salary matching, and semantic vector indexing checks.</p>
                  <button
                    disabled={isMatchingRunning}
                    onClick={handleTriggerMatching}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs px-4 py-2.5 rounded-lg transition disabled:bg-purple-300"
                  >
                    {isMatchingRunning ? "Analyzing listings..." : "Trigger Matching Engine Pipeline"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "resume" && (
            <div className="flex flex-col gap-6">
              {/* Drag and Drop Zone */}
              <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 flex flex-col gap-4">
                <h2 className="font-bold text-lg text-slate-900">Resume & Vector Indexing</h2>
                <p className="text-xs text-slate-400">Upload your PDF resume. The Resume Agent will extract structural sections, calculate ATS scores, and update vector embeddings in ChromaDB.</p>
                
                <div className="border-2 border-dashed border-purple-200 rounded-xl p-8 flex flex-col items-center justify-center gap-3 bg-purple-50/20 hover:bg-purple-50/40 duration-200 cursor-pointer relative">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleResumeUpload}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                  <div className="w-12 h-12 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center">
                    <UploadIcon />
                  </div>
                  <div className="text-center">
                    <span className="text-xs font-bold text-purple-700 block">Click or Drag PDF to upload</span>
                    <span className="text-xxs text-slate-400 mt-1 block">PDFPlumber parsing + PyPDF2 fallback support</span>
                  </div>
                </div>

                {uploadedResume && (
                  <div className="flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-slate-50">
                    <span className="text-xs font-semibold text-slate-700 font-mono">{uploadedResume}</span>
                    <span className="text-xxs font-bold text-emerald-700 bg-emerald-100 px-2.5 py-0.5 rounded-full">ChromaDB Indexed</span>
                  </div>
                )}
              </div>

              {/* Extracted Profile details */}
              <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm shadow-purple-50/50 flex flex-col gap-6">
                <h3 className="font-bold text-slate-900 text-base">Extracted Candidate Details</h3>
                
                <div className="flex flex-col gap-4">
                  <div className="flex flex-col gap-2">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Indexed Skills</span>
                    <div className="flex flex-wrap gap-2">
                      {profileSkills.map((skill, index) => (
                        <span key={index} className="text-xs font-semibold px-3 py-1 rounded-lg bg-purple-50 text-purple-700 border border-purple-100">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Experience Summary</span>
                    <div className="flex flex-col gap-3">
                      {profileExperience.map((exp, index) => (
                        <div key={index} className="p-3 rounded-lg border border-slate-100 hover:bg-slate-50 duration-150">
                          <div className="flex justify-between items-center">
                            <span className="text-xs font-bold text-slate-900">{exp.title}</span>
                            <span className="text-xxs text-slate-400 font-semibold">{exp.duration}</span>
                          </div>
                          <span className="text-xxs text-slate-400">{exp.company}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-100 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center text-xs text-slate-400">
          <span>AutoApplyAI v0.1.0</span>
          <span>Designed with Purple & White themes</span>
        </div>
      </footer>
    </div>
  );
}
