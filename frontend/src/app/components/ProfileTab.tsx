import React from "react";
import { ProfileData, AtsMetrics, Experience, Education } from "../types";
import { UserIcon, SparklesIcon, UploadIcon, TargetIcon } from "./Icons";
import { ProfileSkeleton, ErrorCard } from "./Skeletons";
import {
  WORK_MODE_OPTIONS,
  ALL_WORLD_COUNTRIES,
  EMPLOYMENT_TYPE_OPTIONS,
  SALARY_RANGE_OPTIONS,
  EXPERIENCE_LEVEL_OPTIONS,
  VISA_SPONSORSHIP_OPTIONS
} from "../constants";

interface ProfileTabProps {
  userEmail: string;
  setUserEmail: (v: string) => void;
  portfolioUrl: string;
  setPortfolioUrl: (v: string) => void;
  githubUrl: string;
  setGithubUrl: (v: string) => void;
  otherUrl: string;
  setOtherUrl: (v: string) => void;
  targetRoles: string[];
  setTargetRoles: (v: string[]) => void;
  countryQuery: string;
  setCountryQuery: (v: string) => void;
  isCountryDropdownOpen: boolean;
  setIsCountryDropdownOpen: (v: boolean) => void;
  selectedCountries: string[];
  handleSelectCountryFromDropdown: (c: string) => void;
  handleRemoveCountry: (c: string) => void;
  workModePref: string;
  setWorkModePref: (v: string) => void;
  salaryPref: string;
  setSalaryPref: (v: string) => void;
  experiencePref: string;
  setExperiencePref: (v: string) => void;
  visaSponsorshipPref: string;
  setVisaSponsorshipPref: (v: string) => void;
  selectedEmpTypes: string[];
  toggleEmpType: (type: string) => void;
  dailyJobGoal: number;
  setDailyJobGoal: (v: number) => void;
  dailyInternshipGoal: number;
  setDailyInternshipGoal: (v: number) => void;
  totalTodayApplied: number;
  totalDailyTarget: number;
  overallGoalProgress: number;
  todayJobsCount: number;
  todayInternshipsCount: number;
  isSavingProfile: boolean;
  handleSaveProfile: (e: React.FormEvent) => void;
  isUploading: boolean;
  agentPhase: string | null;
  agentLogs: string[];
  uploadedResume: string | null;
  handleResumeUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  extractedProfile: ProfileData;
  atsMetrics: AtsMetrics;
  handleRunAtsCheck: () => void;
  isAnalyzingATS: boolean;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export default function ProfileTab({
  userEmail, setUserEmail,
  portfolioUrl, setPortfolioUrl,
  githubUrl, setGithubUrl,
  otherUrl, setOtherUrl,
  targetRoles, setTargetRoles,
  countryQuery, setCountryQuery,
  isCountryDropdownOpen, setIsCountryDropdownOpen,
  selectedCountries, handleSelectCountryFromDropdown, handleRemoveCountry,
  workModePref, setWorkModePref,
  salaryPref, setSalaryPref,
  experiencePref, setExperiencePref,
  visaSponsorshipPref, setVisaSponsorshipPref,
  selectedEmpTypes, toggleEmpType,
  dailyJobGoal, setDailyJobGoal,
  dailyInternshipGoal, setDailyInternshipGoal,
  totalTodayApplied, totalDailyTarget, overallGoalProgress,
  todayJobsCount, todayInternshipsCount,
  isSavingProfile, handleSaveProfile,
  isUploading, agentPhase, agentLogs,
  uploadedResume, handleResumeUpload,
  extractedProfile, atsMetrics,
  handleRunAtsCheck, isAnalyzingATS,
  isLoading, error, onRetry
}: ProfileTabProps) {
  if (isLoading) {
    return <ProfileSkeleton />;
  }

  if (error) {
    return <ErrorCard message={error} onRetry={onRetry} />;
  }

  return (
    <div className="space-y-8">
      {/* Top Grid: User Info Form + Resume Upload Card & AI Profile Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Col 1 & 2: User Personal Details & Portfolio Links Form */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <UserIcon />
                <span>User Information & Portfolio Links</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Manage your contact details, portfolio websites, GitHub, and job preferences.</p>
            </div>
            <span className="bg-rose-950/80 text-rose-300 border border-rose-500/30 text-xs px-3 py-1 rounded-full font-mono">
              Profile Configured
            </span>
          </div>

          <form onSubmit={handleSaveProfile} className="space-y-6 text-xs">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Email Address</label>
                <input
                  type="email"
                  value={userEmail}
                  onChange={e => setUserEmail(e.target.value)}
                  placeholder="you@domain.com"
                  className="w-full omni-input rounded-xl px-3 py-2.5"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Portfolio / Personal Website</label>
                <input
                  type="url"
                  value={portfolioUrl}
                  onChange={e => setPortfolioUrl(e.target.value)}
                  placeholder="https://yourportfolio.com"
                  className="w-full omni-input rounded-xl px-3 py-2.5"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">GitHub / GitLab Profile</label>
                <input
                  type="url"
                  value={githubUrl}
                  onChange={e => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/username"
                  className="w-full omni-input rounded-xl px-3 py-2.5"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Other Link (LinkedIn, Twitter)</label>
                <input
                  type="url"
                  value={otherUrl}
                  onChange={e => setOtherUrl(e.target.value)}
                  placeholder="https://linkedin.com/in/username"
                  className="w-full omni-input rounded-xl px-3 py-2.5"
                />
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-white/10">
              <h4 className="text-sm font-bold text-slate-200">International Job Search Preferences</h4>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Target Roles (Comma separated)</label>
                <input
                  type="text"
                  value={targetRoles.join(", ")}
                  onChange={e => setTargetRoles(e.target.value.split(",").map(r => r.trim()))}
                  placeholder="e.g. Software Engineer, Frontend Developer"
                  className="w-full omni-input rounded-xl px-3 py-2.5"
                />
              </div>

              {/* Target Countries Search Component */}
              <div className="relative z-20">
                <label className="block text-slate-300 font-semibold mb-1 flex items-center justify-between">
                  <span>Target Countries (Multi-Select)</span>
                  <span className="text-[10px] text-rose-400 font-mono">{selectedCountries.length}/10 Max</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={countryQuery}
                    onChange={e => {
                      setCountryQuery(e.target.value);
                      setIsCountryDropdownOpen(true);
                    }}
                    onFocus={() => setIsCountryDropdownOpen(true)}
                    placeholder="Search and add countries (e.g. United States, Germany...)"
                    className="w-full omni-input rounded-xl px-3 py-2.5"
                  />
                  {isCountryDropdownOpen && (
                    <div className="absolute top-full left-0 w-full mt-2 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl max-h-60 overflow-y-auto custom-scrollbar z-50">
                      {ALL_WORLD_COUNTRIES
                        .filter(c => c.toLowerCase().includes(countryQuery.toLowerCase()))
                        .map((country, idx) => {
                          const isAlreadySelected = selectedCountries.includes(country);
                          return (
                            <div
                              key={idx}
                              onClick={() => handleSelectCountryFromDropdown(country)}
                              className={`px-4 py-2.5 text-xs font-semibold cursor-pointer flex items-center justify-between transition-colors ${isAlreadySelected
                                  ? "bg-slate-950 text-slate-500 cursor-not-allowed"
                                  : "hover:bg-rose-950/40 text-slate-200 hover:text-rose-300"
                                }`}
                            >
                              <span>{country}</span>
                              {isAlreadySelected ? (
                                <span className="text-[10px] text-rose-400 font-mono">Already Selected</span>
                              ) : (
                                <span className="text-[10px] text-rose-400 font-mono">+ Click to Add</span>
                              )}
                            </div>
                          );
                        })}
                      {ALL_WORLD_COUNTRIES.filter(c => c.toLowerCase().includes(countryQuery.toLowerCase())).length === 0 && (
                        <div className="p-4 text-xs text-slate-400 text-center">No matching countries found</div>
                      )}
                    </div>
                  )}
                </div>

                {/* Selected Target Countries Tags / Badges Displayed Below */}
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 block mb-2 mt-2">Active Target Countries List (CV will be sent to these countries):</span>
                  <div className="flex flex-wrap gap-2">
                    {selectedCountries.map((country, idx) => (
                      <span
                        key={idx}
                        className="bg-rose-950/90 border border-rose-500/50 text-rose-200 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-2 shadow-sm"
                      >
                        <span>{country}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveCountry(country)}
                          className="hover:text-red-400 text-slate-400 font-bold ml-1"
                          title="Remove country"
                        >
                          ✕
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-white/10 pt-4">
                {/* Work Mode */}
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Preferred Work Mode / Remote Policy</label>
                  <select
                    value={workModePref}
                    onChange={e => setWorkModePref(e.target.value)}
                    className="w-full omni-input rounded-xl px-3 py-2 text-xs"
                  >
                    {WORK_MODE_OPTIONS.map((opt, idx) => (
                      <option key={idx} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>

                {/* Salary Range */}
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Minimum Compensation Range (USD)</label>
                  <select
                    value={salaryPref}
                    onChange={e => setSalaryPref(e.target.value)}
                    className="w-full omni-input rounded-xl px-3 py-2 text-xs"
                  >
                    {SALARY_RANGE_OPTIONS.map((opt, idx) => (
                      <option key={idx} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>

                {/* Experience Level */}
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Target Experience Level</label>
                  <select
                    value={experiencePref}
                    onChange={e => setExperiencePref(e.target.value)}
                    className="w-full omni-input rounded-xl px-3 py-2 text-xs"
                  >
                    {EXPERIENCE_LEVEL_OPTIONS.map((opt, idx) => (
                      <option key={idx} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>

                {/* Visa Sponsorship */}
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Visa Sponsorship & Relocation Requirement</label>
                  <select
                    value={visaSponsorshipPref}
                    onChange={e => setVisaSponsorshipPref(e.target.value)}
                    className="w-full omni-input rounded-xl px-3 py-2 text-xs"
                  >
                    {VISA_SPONSORSHIP_OPTIONS.map((opt, idx) => (
                      <option key={idx} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Employment Type Pills */}
              <div>
                <label className="block text-slate-300 font-semibold mb-2">Target Opportunity Types</label>
                <div className="flex flex-wrap gap-2">
                  {EMPLOYMENT_TYPE_OPTIONS.map((type, idx) => {
                    const isSelected = selectedEmpTypes.includes(type);
                    return (
                      <button
                        type="button"
                        key={idx}
                        onClick={() => toggleEmpType(type)}
                        className={`text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all ${isSelected
                            ? "bg-rose-950/80 border-rose-500 text-rose-200 shadow"
                            : "bg-[#12141d] border-white/10 text-slate-400 hover:text-slate-200"
                          }`}
                      >
                        {isSelected ? "✓ " : "+ "}{type}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* 🎯 Daily Application Goal & Auto-Fulfill Settings Card */}
            <div className="bg-[#12141d] border border-white/10 p-5 rounded-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center gap-2">
                  <TargetIcon />
                  <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider">
                    Daily Application Goals & Automation Targets
                  </h4>
                </div>
                <span className="text-[10px] bg-rose-950/80 text-rose-300 border border-rose-500/30 px-2.5 py-0.5 rounded font-mono">
                  Auto-Fulfill Active
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">
                    💼 Daily Jobs Goal (Applications / Day)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={dailyJobGoal}
                    onChange={e => setDailyJobGoal(parseInt(e.target.value) || 1)}
                    className="w-full omni-input rounded-xl px-3 py-2 font-mono text-xs"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">Set how many job applications the agent should apply for daily.</p>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">
                    🎓 Daily Internships Goal (Applications / Day)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={dailyInternshipGoal}
                    onChange={e => setDailyInternshipGoal(parseInt(e.target.value) || 1)}
                    className="w-full omni-input rounded-xl px-3 py-2 font-mono text-xs"
                  />
                  <p className="text-[10px] text-slate-400 mt-1">Set how many internship applications the agent should apply for daily.</p>
                </div>
              </div>

              {/* Goal Progress Tracker Bar */}
              <div className="bg-[#090a0f] p-4 rounded-xl border border-white/10 space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-200 font-semibold flex items-center gap-1.5">
                    <span>⚡ Today's Goal Progress:</span>
                    <strong className="text-rose-400 font-mono">{totalTodayApplied} / {totalDailyTarget} Applications</strong>
                  </span>
                  <span className="text-rose-400 font-mono font-bold">{overallGoalProgress}% Completed</span>
                </div>

                <div className="w-full bg-[#12141d] h-2.5 rounded-full overflow-hidden border border-white/10">
                  <div
                    className="bg-gradient-to-r from-rose-600 via-rose-500 to-rose-400 h-full rounded-full transition-all duration-500"
                    style={{ width: `${overallGoalProgress}%` }}
                  ></div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 pt-1">
                  <div>• Jobs Applied Today: <strong className="text-rose-300 font-mono">{todayJobsCount} / {dailyJobGoal}</strong></div>
                  <div>• Internships Applied Today: <strong className="text-rose-300 font-mono">{todayInternshipsCount} / {dailyInternshipGoal}</strong></div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end pt-2">
              <button
                type="submit"
                disabled={isSavingProfile}
                className="btn-red-glow text-white font-semibold px-5 py-2.5 rounded-lg shadow-lg flex items-center gap-2 transition-all text-xs"
              >
                {isSavingProfile ? "Saving Settings..." : `Save ${selectedCountries.length} Target Countries & Profile Preferences`}
              </button>
            </div>
          </form>
        </div>

        {/* Col 3: PDF Resume Upload & Extracted Candidate Profile Breakdown Card */}
        <div className="lg:col-span-1 space-y-6">

          {/* Upload Card or Agent Thinking UI */}
          {isUploading ? (
            <div className="bg-slate-900/90 border-2 border-rose-500/50 p-6 rounded-2xl shadow-[0_0_30px_rgba(244,63,94,0.15)] space-y-4 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-slate-800">
                <div className="h-full bg-rose-500 rounded-r-full animate-pulse" style={{ width: agentPhase === 'reading' ? '25%' : agentPhase === 'planning' ? '50%' : agentPhase === 'extracting' ? '75%' : agentPhase === 'scoring' ? '90%' : '100%' }}></div>
              </div>

              <div className="flex items-center justify-between border-b border-rose-500/30 pb-3">
                <h3 className="text-sm font-bold text-rose-300 flex items-center gap-2">
                  <SparklesIcon />
                  <span>RAG Agent Active...</span>
                </h3>
                <div className="flex gap-1">
                  <span className="w-2 h-2 rounded-full bg-rose-400 animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 rounded-full bg-rose-400 animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 rounded-full bg-rose-400 animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>

              <div className="bg-slate-950 rounded-xl p-4 font-mono text-[11px] text-slate-300 space-y-2 h-40 overflow-y-auto border border-rose-500/20 shadow-inner">
                {agentLogs.map((log, idx) => (
                  <div key={idx} className="flex items-start gap-2 animate-fade-in">
                    <span className="text-rose-500 mt-0.5">❯</span>
                    <span className={idx === agentLogs.length - 1 && agentPhase !== 'complete' ? 'text-white font-bold animate-pulse' : 'text-slate-400'}>
                      {log}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
                  <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                    <UploadIcon />
                    <span>PDF Resume Upload</span>
                  </h3>
                  <span className="text-[10px] bg-rose-950 text-rose-400 border border-rose-500/30 px-2.5 py-0.5 rounded font-mono">
                    AI Parsing Engine
                  </span>
                </div>

                <div className="border-2 border-dashed border-slate-700 hover:border-rose-500 p-6 rounded-xl text-center bg-slate-950/60 cursor-pointer relative transition-all group">
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleResumeUpload}
                    className="absolute inset-0 opacity-0 cursor-pointer z-10"
                  />
                  <div className="w-12 h-12 bg-rose-950/60 border border-rose-500/30 rounded-xl flex items-center justify-center mx-auto text-rose-400 group-hover:scale-110 transition-transform">
                    <UploadIcon />
                  </div>
                  <p className="text-xs font-semibold text-slate-200 mt-3">
                    Click or Drag PDF Resume File
                  </p>
                  <p className="text-[10px] text-slate-400 mt-1">Agent will plan, extract skills & score against jobs</p>
                </div>
              </div>

              {uploadedResume ? (
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-200 font-semibold truncate">📄 {uploadedResume}</span>
                    <span className="bg-rose-950 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded text-[10px] font-mono">
                      Active PDF
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
                    <span>AI Processed Status:</span>
                    <strong className="text-rose-300 font-mono">Profile Ready</strong>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center text-xs space-y-1">
                  <p className="text-slate-300 font-semibold">No Active Resume</p>
                  <p className="text-[10px] text-slate-400">Upload your PDF resume above to let the RAG Agent analyze it.</p>
                </div>
              )}
            </div>
          )}

          {/* Candidate AI Profile Breakdown Card */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-5 h-[500px] overflow-y-auto custom-scrollbar">
            <div className="border-b border-slate-800 pb-3 flex items-center justify-between sticky top-0 bg-slate-900/80 backdrop-blur z-10">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <SparklesIcon />
                <span>Extracted Candidate Profile Breakdown</span>
              </h3>
              <span className="text-[10px] bg-rose-950 text-rose-300 border border-rose-500/30 px-2 py-0.5 rounded font-mono">
                AI Live Summary
              </span>
            </div>

            {/* Candidate Executive Summary */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
              <h4 className="text-[11px] font-bold text-rose-400 uppercase tracking-wider">Executive Summary</h4>
              <p className="text-xs text-slate-300 leading-relaxed">{extractedProfile.summary || "No executive summary extracted yet. Upload a PDF resume above to run real-time AI parsing."}</p>
            </div>

            {/* Extracted Skills Badges */}
            <div>
              <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2">Extracted Skills & Tech Stack</h4>
              {extractedProfile.skills.length === 0 ? (
                <p className="text-xs text-slate-500">No skills extracted yet. Upload a PDF resume above.</p>
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {extractedProfile.skills.map((skill, idx) => (
                    <span key={idx} className="bg-rose-950/60 border border-rose-500/40 text-rose-200 text-xs font-semibold px-2.5 py-1 rounded-lg shadow-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Experience */}
            {extractedProfile.experience && extractedProfile.experience.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2 border-t border-slate-800 pt-4">Work Experience</h4>
                {extractedProfile.experience.map((exp: Experience, idx: number) => (
                  <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800/60 flex flex-col gap-1">
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-bold text-slate-200">{exp.title}</span>
                      <span className="text-[10px] text-rose-400 font-mono bg-rose-950/30 px-1.5 py-0.5 rounded">{exp.company}</span>
                    </div>
                    {exp.date && <span className="text-[10px] text-slate-500">{exp.date}</span>}
                    <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{exp.description}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Education */}
            {extractedProfile.education && extractedProfile.education.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2 border-t border-slate-800 pt-4">Education</h4>
                {extractedProfile.education.map((edu: Education, idx: number) => (
                  <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800/60 flex flex-col gap-1">
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-bold text-slate-200">{edu.degree}</span>
                      <span className="text-[10px] text-indigo-400 font-mono bg-indigo-950/30 px-1.5 py-0.5 rounded">{edu.institution}</span>
                    </div>
                    {edu.date && <span className="text-[10px] text-slate-500">{edu.date}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Middle Section: Authentic ATS Scoring Dashboard */}
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <SparklesIcon />
              <span>Original ATS Resume Score & Portfolio Health</span>
            </h3>
            <p className="text-xs text-slate-400">Authentic grading based on ATS section completeness, skill density, formatting, and impact verbs.</p>
          </div>

          <button
            onClick={handleRunAtsCheck}
            disabled={isAnalyzingATS}
            className="bg-rose-950/80 hover:bg-rose-900 border border-rose-500/40 text-rose-200 text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-2 transition-all self-start sm:self-auto"
          >
            {isAnalyzingATS ? "Running ATS Audit..." : "⚡ Re-Run Real-Time ATS Check"}
          </button>
        </div>

        {/* Score Gauge Card */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">

          {/* Score Gauge Card */}
          <div className="md:col-span-1 bg-slate-950 border border-slate-800 p-6 rounded-xl text-center flex flex-col justify-center items-center space-y-2">
            <div className="relative w-28 h-28 flex items-center justify-center rounded-full bg-gradient-to-tr from-rose-500/20 via-red-500/20 to-orange-500/20 border-4 border-rose-500/50 shadow-lg shadow-rose-500/10">
              <div className="text-center">
                <span className="text-3xl font-extrabold text-rose-400">{atsMetrics.overall_score || 0}</span>
                <span className="text-xs text-slate-400 block font-semibold">/ 100</span>
              </div>
            </div>
            <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider pt-2">
              {atsMetrics.overall_score > 0 ? "ATS Score Ready" : "Awaiting Resume Upload"}
            </h4>
            <p className="text-[11px] text-slate-400">{atsMetrics.summary}</p>
          </div>

          {/* Detailed Meters */}
          <div className="md:col-span-3 grid grid-cols-1 sm:grid-cols-2 gap-4">

            {/* Meter 1: Formatting & Structure */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-semibold">🎨 Formatting & Structure</span>
                <span className="text-rose-400 font-mono font-bold">{atsMetrics.formatting_score}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-rose-400 h-full rounded-full" style={{ width: `${atsMetrics.formatting_score}%` }}></div>
              </div>
              <p className="text-[10px] text-slate-400">Clean font sizing, standard section headings & standard PDF encoding.</p>
            </div>

            {/* Meter 2: Skill Density */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-semibold">🔑 Technical Skill Density</span>
                <span className="text-rose-400 font-mono font-bold">{atsMetrics.keyword_density_score}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-rose-400 h-full rounded-full" style={{ width: `${atsMetrics.keyword_density_score}%` }}></div>
              </div>
              <p className="text-[10px] text-slate-400">High frequency of core technical & job keywords.</p>
            </div>

            {/* Meter 3: Action Verbs */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-semibold">⚡ Impact & Action Verbs</span>
                <span className="text-rose-400 font-mono font-bold">{atsMetrics.action_verbs_score}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-rose-400 h-full rounded-full" style={{ width: `${atsMetrics.action_verbs_score}%` }}></div>
              </div>
              <p className="text-[10px] text-slate-400">Includes strong verbs: 'Architected', 'Engineered', 'Optimized'.</p>
            </div>

            {/* Meter 4: Section Completeness */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-semibold">📋 Section Completeness</span>
                <span className="text-rose-400 font-mono font-bold">{atsMetrics.section_completeness_score}%</span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                <div className="bg-rose-400 h-full rounded-full" style={{ width: `${atsMetrics.section_completeness_score}%` }}></div>
              </div>
              <p className="text-[10px] text-slate-400">Education, experience, skills & contact links present.</p>
            </div>
          </div>
        </div>

        {/* ATS Optimization Roadmap Section */}
        {(atsMetrics.missing_skills?.length > 0 || atsMetrics.formatting_suggestions?.length > 0 || atsMetrics.experience_improvements?.length > 0) && (
          <div className="border-t border-slate-800/80 pt-6 mt-2 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <SparklesIcon />
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-400 via-pink-400 to-indigo-400 font-extrabold text-base">
                    AI-Powered ATS Optimization Roadmap
                  </span>
                </h4>
                <p className="text-xs text-slate-400 mt-1">
                  Actionable insights generated from real-time resume parsing to elevate keyword density and interview callback ranking.
                </p>
              </div>
              <span className="text-[11px] bg-slate-950 text-slate-300 border border-slate-800 px-3 py-1 rounded-full font-mono self-start sm:self-auto shadow-sm">
                ✨ Personalized Insights
              </span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Missing Skills Card */}
              {atsMetrics.missing_skills?.length > 0 && (
                <div className="bg-gradient-to-b from-slate-950 to-[#12141e] p-5 rounded-2xl border border-amber-500/25 shadow-lg hover:border-amber-500/50 transition-all duration-300 flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex items-center justify-between border-b border-amber-500/15 pb-3 mb-3">
                      <div className="flex items-center gap-2.5">
                        <span className="w-8 h-8 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 font-bold text-sm shadow-inner">🔑</span>
                        <h5 className="text-xs font-extrabold text-amber-400 uppercase tracking-wider">Missing Keywords</h5>
                      </div>
                      <span className="text-[10px] bg-amber-500/15 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-md font-mono">
                        {atsMetrics.missing_skills.length} detected
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
                      Adding these high-frequency keywords from target job descriptions will significantly boost your technical match score:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {atsMetrics.missing_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="bg-amber-950/50 hover:bg-amber-900/60 border border-amber-500/40 text-amber-200 text-xs font-semibold px-2.5 py-1.5 rounded-lg transition-colors shadow-sm flex items-center gap-1.5"
                        >
                          <span className="text-amber-400 font-bold">+</span>
                          <span>{skill}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Formatting Suggestions Card */}
              {atsMetrics.formatting_suggestions?.length > 0 && (
                <div className="bg-gradient-to-b from-slate-950 to-[#12141e] p-5 rounded-2xl border border-indigo-500/25 shadow-lg hover:border-indigo-500/50 transition-all duration-300 flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex items-center justify-between border-b border-indigo-500/15 pb-3 mb-3">
                      <div className="flex items-center gap-2.5">
                        <span className="w-8 h-8 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-sm shadow-inner">🎨</span>
                        <h5 className="text-xs font-extrabold text-indigo-400 uppercase tracking-wider">Formatting Tips</h5>
                      </div>
                      <span className="text-[10px] bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-md font-mono">
                        Layout & ATS
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
                      Optimize structural presentation to ensure accurate automated parsing and human readability:
                    </p>
                    <ul className="space-y-2.5">
                      {atsMetrics.formatting_suggestions.map((suggestion, idx) => (
                        <li key={idx} className="bg-indigo-950/25 border border-indigo-500/20 rounded-xl p-3 text-xs text-slate-200 flex items-start gap-3 shadow-sm hover:bg-indigo-950/40 transition-colors">
                          <span className="text-indigo-400 text-sm font-bold shrink-0 mt-0.5">❯</span>
                          <span className="leading-relaxed">{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Experience Improvements Card */}
              {atsMetrics.experience_improvements?.length > 0 && (
                <div className="bg-gradient-to-b from-slate-950 to-[#12141e] p-5 rounded-2xl border border-emerald-500/25 shadow-lg hover:border-emerald-500/50 transition-all duration-300 flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex items-center justify-between border-b border-emerald-500/15 pb-3 mb-3">
                      <div className="flex items-center gap-2.5">
                        <span className="w-8 h-8 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-bold text-sm shadow-inner">⚡</span>
                        <h5 className="text-xs font-extrabold text-emerald-400 uppercase tracking-wider">Experience Enhancements</h5>
                      </div>
                      <span className="text-[10px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-md font-mono">
                        Action & Impact
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
                      Strengthen achievement descriptions and demonstrate measurable business impact:
                    </p>
                    <ul className="space-y-2.5">
                      {atsMetrics.experience_improvements.map((improvement, idx) => (
                        <li key={idx} className="bg-emerald-950/25 border border-emerald-500/20 rounded-xl p-3 text-xs text-slate-200 flex items-start gap-3 shadow-sm hover:bg-emerald-950/40 transition-colors">
                          <span className="text-emerald-400 text-sm font-bold shrink-0 mt-0.5">✓</span>
                          <span className="leading-relaxed">{improvement}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
