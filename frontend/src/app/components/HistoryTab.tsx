import React from "react";
import { Application } from "../types";
import { CalendarIcon, GmailIcon } from "./Icons";

interface HistoryTabProps {
  historyFilter: "today" | "monthly" | "yearly" | "all";
  setHistoryFilter: (filter: "today" | "monthly" | "yearly" | "all") => void;
  todayApps: Application[];
  todayJobsCount: number;
  todayInternshipsCount: number;
  monthlyApps: Application[];
  yearlyApps: Application[];
  applications: Application[];
  filteredApplications: Application[];
}

export default function HistoryTab({
  historyFilter,
  setHistoryFilter,
  todayApps,
  todayJobsCount,
  todayInternshipsCount,
  monthlyApps,
  yearlyApps,
  applications,
  filteredApplications
}: HistoryTabProps) {
  return (
    <div className="space-y-6">
      {/* Top Metric Cards for Today, Monthly, Yearly */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Card 1: Today */}
        <div 
          onClick={() => setHistoryFilter("today")}
          className={`p-5 rounded-2xl border cursor-pointer transition-all shadow-lg ${
            historyFilter === "today"
              ? "bg-rose-950/40 border-rose-500/80 ring-2 ring-rose-500/30"
              : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-rose-300 uppercase tracking-wider flex items-center gap-1.5">
              <CalendarIcon />
              <span>Today's Submissions</span>
            </span>
            <span className="bg-rose-950 text-rose-300 border border-rose-500/30 text-[10px] px-2 py-0.5 rounded font-mono">
              24 Hours
            </span>
          </div>
          <div className="text-2xl font-extrabold text-rose-400 font-mono">{todayApps.length} Applications</div>
          <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
            <span>Jobs: <strong className="text-slate-200 font-mono">{todayJobsCount}</strong></span>
            <span>Internships: <strong className="text-amber-300 font-mono">{todayInternshipsCount}</strong></span>
          </div>
        </div>

        {/* Card 2: Monthly */}
        <div 
          onClick={() => setHistoryFilter("monthly")}
          className={`p-5 rounded-2xl border cursor-pointer transition-all shadow-lg ${
            historyFilter === "monthly"
              ? "bg-rose-950/40 border-rose-500/80 ring-2 ring-rose-500/30"
              : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-rose-300 uppercase tracking-wider flex items-center gap-1.5">
              <CalendarIcon />
              <span>Monthly</span>
            </span>
            <span className="bg-rose-950 text-rose-300 border border-rose-500/30 text-[10px] px-2 py-0.5 rounded font-mono">
              This Month
            </span>
          </div>
          <div className="text-2xl font-extrabold text-rose-400 font-mono">{monthlyApps.length} Applications</div>
          <p className="text-[11px] text-slate-400 mt-1">Total applications submitted during current billing period.</p>
        </div>

        {/* Card 3: Yearly */}
        <div 
          onClick={() => setHistoryFilter("yearly")}
          className={`p-5 rounded-2xl border cursor-pointer transition-all shadow-lg ${
            historyFilter === "yearly"
              ? "bg-rose-950/40 border-rose-500/80 ring-2 ring-rose-500/30"
              : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
          }`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-rose-300 uppercase tracking-wider flex items-center gap-1.5">
              <CalendarIcon />
              <span>Yearly</span>
            </span>
            <span className="bg-rose-950 text-rose-300 border border-rose-500/30 text-[10px] px-2 py-0.5 rounded font-mono">
              Year to Date
            </span>
          </div>
          <div className="text-2xl font-extrabold text-rose-400 font-mono">{yearlyApps.length} Applications</div>
          <p className="text-[11px] text-slate-400 mt-1">Lifetime total application deliveries in current year.</p>
        </div>
      </div>

      {/* Main Application Table Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <GmailIcon />
              <span>Applications Sent via Connected Gmail</span>
            </h3>
            <p className="text-xs text-slate-400">Direct proof of emails delivered from your Gmail account to company hiring managers.</p>
          </div>

          {/* Period Filter Buttons */}
          <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setHistoryFilter("today")}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                historyFilter === "today"
                  ? "bg-rose-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              ⚡ Today ({todayApps.length})
            </button>
            <button
              onClick={() => setHistoryFilter("monthly")}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                historyFilter === "monthly"
                  ? "bg-rose-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              📅 Monthly ({monthlyApps.length})
            </button>
            <button
              onClick={() => setHistoryFilter("yearly")}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                historyFilter === "yearly"
                  ? "bg-rose-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              🗓️ Yearly ({yearlyApps.length})
            </button>
            <button
              onClick={() => setHistoryFilter("all")}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                historyFilter === "all"
                  ? "bg-slate-800 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              🌐 All ({applications.length})
            </button>
          </div>
        </div>

        <div className="divide-y divide-slate-800">
          {filteredApplications.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs space-y-2">
              <p className="text-sm font-semibold text-slate-300">No Applications Submitted Yet</p>
              <p>Trigger Auto-Apply on recommended opportunities to see real-time Gmail delivery proofs here.</p>
            </div>
          ) : (
            filteredApplications.map((app) => (
              <div key={app.id} className="p-6 hover:bg-slate-900/40 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-3">
                    <h4 className="text-sm font-bold text-slate-100">{app.title}</h4>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                      app.opportunity_type === "internship"
                        ? "bg-amber-950/80 text-amber-300 border border-amber-500/30"
                        : "bg-rose-950/80 text-rose-300 border border-rose-500/30"
                    }`}>
                      {(app.opportunity_type || "job").toUpperCase()}
                    </span>
                    <span className="bg-rose-950/80 text-rose-300 border border-rose-500/30 text-[10px] px-2 py-0.5 rounded-full font-semibold">
                      {app.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    Company: <strong className="text-slate-200">{app.company}</strong> ({app.company_email || "HR Email"})
                  </p>
                  {app.gmail_message_id && (
                    <p className="text-[11px] text-slate-500 font-mono">
                      Gmail Message ID: {app.gmail_message_id} • Sent At: {new Date(app.applied_at).toLocaleString()}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-rose-400 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 font-mono">
                    ✓ Appears in Gmail "Sent" folder
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
