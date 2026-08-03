"use client";

import React from "react";

interface AutoApplyProgressProps {
    status: {
        status: string;
        job_target: number;
        job_applied: number;
        internship_target: number;
        internship_applied: number;
        total_applied: number;
        total_failed: number;
        current_job_title?: string | null;
        current_job_company?: string | null;
        last_error?: string | null;
    } | null;
    onStop: () => void;
    isStopping: boolean;
}

export default function AutoApplyProgress({
    status,
    onStop,
    isStopping
}: AutoApplyProgressProps) {
    if (!status || status.status === "idle") return null;

    const isRunning = status.status === "running";
    const totalTarget = status.job_target + status.internship_target;
    const totalApplied = status.job_applied + status.internship_applied;
    const progress = totalTarget > 0 ? Math.min(100, Math.round((totalApplied / totalTarget) * 100)) : 0;

    const statusLabel = {
        running: "🔄 Auto-Apply in Progress...",
        completed: "✅ Auto-Apply Completed!",
        stopped: "⏹️ Auto-Apply Stopped",
        error: "❌ Auto-Apply Error"
    }[status.status] || status.status;

    const statusColor = {
        running: "text-rose-300",
        completed: "text-emerald-400",
        stopped: "text-amber-400",
        error: "text-red-400"
    }[status.status] || "text-slate-300";

    return (
        <div className={`fixed bottom-6 right-6 z-50 w-[380px] shadow-2xl border rounded-2xl backdrop-blur-xl ${isRunning ? "border-rose-500/40 bg-[#12141d]/95" : "border-white/10 bg-[#12141d]/95"
            }`}>
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                    {isRunning && (
                        <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                    )}
                    <h4 className={`text-xs font-bold ${statusColor}`}>{statusLabel}</h4>
                </div>
                {isRunning && (
                    <button
                        onClick={onStop}
                        disabled={isStopping}
                        className="text-[10px] font-semibold text-amber-300 border border-amber-500/30 hover:bg-amber-950/30 px-2 py-0.5 rounded"
                    >
                        {isStopping ? "Stopping..." : "⏹ Stop"}
                    </button>
                )}
            </div>

            <div className="p-4 space-y-3">
                {/* Progress bar */}
                <div>
                    <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                        <span>Progress</span>
                        <span className="font-mono text-rose-300">{progress}%</span>
                    </div>
                    <div className="w-full bg-[#090a0f] h-2 rounded-full overflow-hidden border border-white/10">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${status.status === "completed"
                                    ? "bg-emerald-500"
                                    : status.status === "error"
                                        ? "bg-red-500"
                                        : "bg-gradient-to-r from-rose-600 via-rose-500 to-rose-400"
                                }`}
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>

                {/* Current job being applied */}
                {isRunning && status.current_job_title && (
                    <div className="bg-[#090a0f] border border-white/10 rounded-lg px-3 py-2">
                        <p className="text-[10px] text-slate-400">Currently applying to:</p>
                        <p className="text-xs font-semibold text-slate-200 truncate">{status.current_job_title}</p>
                        <p className="text-[10px] text-rose-300 truncate">{status.current_job_company}</p>
                    </div>
                )}

                {/* Stats grid */}
                <div className="grid grid-cols-2 gap-2">
                    <div className="bg-[#090a0f] border border-white/10 rounded-lg p-2 text-center">
                        <div className="text-lg font-extrabold text-rose-400 font-mono">{status.job_applied}/{status.job_target}</div>
                        <div className="text-[10px] text-slate-400">💼 Jobs</div>
                    </div>
                    <div className="bg-[#090a0f] border border-white/10 rounded-lg p-2 text-center">
                        <div className="text-lg font-extrabold text-amber-400 font-mono">{status.internship_applied}/{status.internship_target}</div>
                        <div className="text-[10px] text-slate-400">🎓 Internships</div>
                    </div>
                    <div className="bg-[#090a0f] border border-white/10 rounded-lg p-2 text-center">
                        <div className="text-lg font-extrabold text-emerald-400 font-mono">{status.total_applied}</div>
                        <div className="text-[10px] text-slate-400">✅ Applied</div>
                    </div>
                    <div className="bg-[#090a0f] border border-white/10 rounded-lg p-2 text-center">
                        <div className="text-lg font-extrabold text-red-400 font-mono">{status.total_failed}</div>
                        <div className="text-[10px] text-slate-400">❌ Failed</div>
                    </div>
                </div>

                {status.last_error && (
                    <div className="bg-red-950/40 border border-red-500/30 rounded-lg px-3 py-2 text-[10px] text-red-300">
                        ⚠️ {status.last_error}
                    </div>
                )}
            </div>
        </div>
    );
}