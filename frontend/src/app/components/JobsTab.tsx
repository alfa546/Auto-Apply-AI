import React from "react";
import { Job } from "../types";
import { SparklesIcon, GlobeIcon, GmailIcon } from "./Icons";
import { JobsSkeleton, ErrorCard } from "./Skeletons";

interface JobsTabProps {
  filteredDailyJobs: Job[];
  selectedCountries: string[];
  isTriggeringSearch: boolean;
  handleTriggerSearchAgent: () => void;
  isApplyingId: number | null;
  handleAutoApply: (job: Job) => void;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

export default function JobsTab({
  filteredDailyJobs,
  selectedCountries,
  isTriggeringSearch,
  handleTriggerSearchAgent,
  isApplyingId,
  handleAutoApply,
  isLoading,
  error,
  onRetry
}: JobsTabProps) {
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="glass-panel p-5 rounded-2xl border border-white/10 h-20 animate-pulse bg-slate-900/40"></div>
        <JobsSkeleton />
      </div>
    );
  }

  if (error) {
    return <ErrorCard message={error} onRetry={onRetry} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-white/10">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <span>Recommended Opportunities</span>
            <span className="bg-rose-950/80 text-rose-300 border border-rose-500/30 text-[10px] uppercase font-bold px-2 py-0.5 rounded">Live Scan</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Extracted HR emails matched against your candidate skills & selected target countries.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleTriggerSearchAgent}
            disabled={isTriggeringSearch}
            className="btn-red-glow text-white font-bold text-xs py-2.5 px-4 rounded-xl shadow-lg flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {isTriggeringSearch ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Scanning Target Countries...</span>
              </>
            ) : (
              <>
                <SparklesIcon />
                <span>⚡ Run Search Agent</span>
              </>
            )}
          </button>

          <div className="bg-slate-950/80 border border-rose-500/40 px-3.5 py-1.5 rounded-xl text-xs text-rose-300 flex items-center gap-2 shadow-inner">
            <GlobeIcon />
            <span>Target Countries: <strong className="text-rose-200 font-mono">{selectedCountries.length} Active</strong></span>
          </div>
        </div>
      </div>

      <div className="grid gap-4">
        {filteredDailyJobs.length === 0 ? (
          <div className="glass-panel p-12 rounded-3xl text-center space-y-5 shadow-2xl border border-white/10 relative overflow-hidden">
            <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-rose-600/10 rounded-full blur-3xl pointer-events-none"></div>
            <div className="w-16 h-16 bg-gradient-to-br from-rose-500/20 to-red-500/20 border border-rose-500/40 rounded-2xl flex items-center justify-center mx-auto text-rose-300 shadow-lg shadow-rose-500/10">
              <SparklesIcon />
            </div>
            <div className="space-y-1.5 max-w-md mx-auto relative z-10">
              <h3 className="text-lg font-bold text-slate-100">No Opportunities Fetched Yet</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Click <strong>"Run Search Agent"</strong> or upload your PDF resume to start scanning target countries for matching roles in real time!
              </p>
            </div>
            <button
              onClick={handleTriggerSearchAgent}
              disabled={isTriggeringSearch}
              className="btn-red-glow text-white font-bold px-6 py-3 rounded-2xl text-xs inline-flex items-center gap-2 transition-all relative z-10"
            >
              <SparklesIcon />
              <span>⚡ Run Smart Search Agent Now</span>
            </button>
          </div>
        ) : (
          filteredDailyJobs.map((job) => (
            <div 
              key={job.id} 
              className="bg-slate-900/80 border border-slate-800 hover:border-rose-500/50 p-6 rounded-xl transition-all shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="text-lg font-bold text-slate-100">{job.title}</h3>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                    job.opportunity_type === "internship"
                      ? "bg-amber-950/80 text-amber-300 border border-amber-500/30"
                      : "bg-rose-950/80 text-rose-300 border border-rose-500/30"
                  }`}>
                    {(job.opportunity_type || "job").toUpperCase()}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-slate-400">
                  <span className="font-semibold text-slate-200">🏢 {job.company}</span>
                  {job.location && <span>📍 {job.location}</span>}
                  {job.salary && <span className="text-amber-300 font-mono">💰 {job.salary}</span>}
                  {job.company_email && <span className="text-rose-400 font-mono">✉️ HR Email: {job.company_email}</span>}
                </div>

                {job.description && <p className="text-xs text-slate-300 line-clamp-2 pt-1">{job.description.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim()}</p>}
              </div>

              <div className="flex md:flex-col items-end justify-between gap-4 min-w-[200px]">
                <div className="text-right">
                  <div className="text-xs text-slate-400">AI Match Score</div>
                  <div className="text-lg font-extrabold text-rose-400">{job.match_score || 92}% Match</div>
                </div>

                <button
                  onClick={() => handleAutoApply(job)}
                  disabled={isApplyingId === job.id}
                  className="w-full btn-red-glow text-white font-semibold text-xs py-2.5 px-4 rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50"
                >
                  {isApplyingId === job.id ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Sending via Gmail...</span>
                    </>
                  ) : (
                    <>
                      <GmailIcon />
                      <span>Apply via Gmail (CV Attached)</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
