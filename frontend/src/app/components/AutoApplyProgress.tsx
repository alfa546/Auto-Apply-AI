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
    onDismiss?: () => void;
    isDismissing?: boolean;
}

export default function AutoApplyProgress({
    status,
    onStop,
    isStopping,
    onDismiss,
    isDismissing = false
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
        <div className={`fixed bottom-6 right-6 z-50 w-[380px] shadow-2xl border rounded-2xl backdrop-blur-xl ${isRunning ? "border-red-500/60 bg-[#12141d]/95 shadow-[0_10px_30px_rgba(239,68,68,0.25)]" : "border-white/10 bg-[#12141d]/95"
            }`}>
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                    {isRunning && (
                        <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>
                    )}
                    <h4 className={`text-xs font-bold ${statusColor}`}>{statusLabel}</h4>
                </div>
                <div className="flex items-center gap-2">
                    {isRunning && (
                        <button
                            onClick={onStop}
                            disabled={isStopping}
                            className="bg-red-600 hover:bg-red-700 text-white text-[11px] font-extrabold px-2.5 py-1 rounded-lg border border-red-400/80 shadow flex items-center gap-1 transition-all disabled:opacity-50"
                        >
                            <span>⏹️</span>
                            <span>{isStopping ? "Stopping..." : "Stop"}</span>
                        </button>
                    )}
                    {!isRunning && onDismiss && (
                        <button
                            onClick={onDismiss}
                            disabled={isDismissing}
                            className="text-slate-400 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 p-1 rounded-lg text-xs transition-all flex items-center justify-center w-7 h-7"
                            title="Close"
                        >
                            ✕
                        </button>
                    )}
                </div>
            </div>

            <div className="p-4 space-y-3.5">
                {/* Progress bar */}
                <div>
                    <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                        <span>Progress</span>
                        <span className="font-mono font-bold text-rose-300">{progress}%</span>
                    </div>
                    <div className="w-full bg-[#090a0f] h-2.5 rounded-full overflow-hidden border border-white/10">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${status.status === "completed"
                                    ? "bg-emerald-500"
                                    : status.status === "error"
                                        ? "bg-red-500"
                                        : "bg-gradient-to-r from-rose-600 via-red-500 to-red-400 animate-pulse"
                                }`}
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>

                {/* Current job being applied */}
                {isRunning && status.current_job_title && (
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl px-3.5 py-2.5">
                        <p className="text-[10px] text-slate-400 font-medium">Currently applying to:</p>
                        <p className="text-xs font-bold text-slate-200 truncate mt-0.5">{status.current_job_title}</p>
                        <p className="text-[11px] text-rose-400 font-semibold truncate">{status.current_job_company}</p>
                    </div>
                )}

                {/* Stats grid */}
                <div className="grid grid-cols-2 gap-2">
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl p-2.5 text-center">
                        <div className="text-lg font-extrabold text-rose-400 font-mono">{status.job_applied}/{status.job_target}</div>
                        <div className="text-[10px] text-slate-400 font-medium">💼 Jobs</div>
                    </div>
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl p-2.5 text-center">
                        <div className="text-lg font-extrabold text-amber-400 font-mono">{status.internship_applied}/{status.internship_target}</div>
                        <div className="text-[10px] text-slate-400 font-medium">🎓 Internships</div>
                    </div>
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl p-2.5 text-center">
                        <div className="text-lg font-extrabold text-emerald-400 font-mono">{status.total_applied}</div>
                        <div className="text-[10px] text-slate-400 font-medium">✅ Applied</div>
                    </div>
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl p-2.5 text-center">
                        <div className="text-lg font-extrabold text-red-400 font-mono">{status.total_failed}</div>
                        <div className="text-[10px] text-slate-400 font-medium">❌ Failed</div>
                    </div>
                </div>

                {status.last_error && (
                    <div className="bg-red-950/40 border border-red-500/30 rounded-xl px-3 py-2 text-[11px] text-red-300">
                        ⚠️ {status.last_error}
                    </div>
                )}

                {/* Prominent Red Stop Button when Running */}
                {isRunning && (
                    <div className="pt-2 border-t border-white/10">
                        <button
                            onClick={onStop}
                            disabled={isStopping}
                            className="w-full bg-red-600 hover:bg-red-700 text-white font-extrabold text-xs py-3 rounded-xl border-2 border-red-400/80 shadow-[0_0_15px_rgba(239,68,68,0.6)] flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50"
                        >
                            <span className="text-base">⏹️</span>
                            <span className="tracking-wide">{isStopping ? "STOPPING AUTO-APPLY..." : "STOP AUTO-APPLY NOW"}</span>
                        </button>
                    </div>
                )}

                {/* Close Button when Finished */}
                {!isRunning && onDismiss && (
                    <div className="pt-2 border-t border-white/10">
                        <button
                            onClick={onDismiss}
                            disabled={isDismissing}
                            className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs py-2.5 rounded-xl border border-white/10 shadow flex items-center justify-center gap-1.5 transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50"
                        >
                            <span className="text-sm">✖</span>
                            <span>{isDismissing ? "Closing..." : "Close"}</span>
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}