"use client";

import React, { useState } from "react";

interface AutoApplyModalProps {
    isOpen: boolean;
    onClose: () => void;
    onStart: (jobCount: number, internshipCount: number) => void;
    isStarting: boolean;
}

export default function AutoApplyModal({
    isOpen,
    onClose,
    onStart,
    isStarting
}: AutoApplyModalProps) {
    const [jobCount, setJobCount] = useState(10);
    const [internshipCount, setInternshipCount] = useState(3);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="bg-[#12141d] border border-white/10 rounded-2xl shadow-2xl w-full max-w-md custom-scrollbar">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-white/10 p-5">
                    <div>
                        <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                            <span className="text-rose-400">⚡</span>
                            <span>Auto-Apply Settings</span>
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">
                            System will apply automatically. No review needed per application.
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-200 text-xl font-bold px-2"
                        aria-label="Close"
                    >
                        ✕
                    </button>
                </div>

                <div className="p-5 space-y-5">
                    {/* Info banner */}
                    <div className="bg-rose-950/40 border border-rose-500/30 rounded-xl p-3 text-xs text-rose-200 space-y-1">
                        <p className="font-semibold">🚀 Fully Automated Mode</p>
                        <p className="text-rose-300/80">
                            The agent will generate cover letters, attach your CV, and send emails to all selected opportunities. Runs in the background until targets are met.
                        </p>
                    </div>

                    {/* Job Count Input */}
                    <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-2">
                            💼 Number of Jobs to Apply
                        </label>
                        <div className="flex items-center gap-3">
                            <input
                                type="range"
                                min={0}
                                max={10}
                                value={jobCount}
                                onChange={(e) => setJobCount(parseInt(e.target.value))}
                                className="flex-1 accent-rose-500"
                            />
                            <span className="text-lg font-bold text-rose-400 font-mono min-w-[40px] text-center">
                                {jobCount}
                            </span>
                        </div>
                        <p className="text-[10px] text-slate-400 mt-1">
                            Maximum: 10 jobs per run
                        </p>
                    </div>

                    {/* Internship Count Input */}
                    <div>
                        <label className="block text-xs font-semibold text-slate-300 mb-2">
                            🎓 Number of Internships to Apply
                        </label>
                        <div className="flex items-center gap-3">
                            <input
                                type="range"
                                min={0}
                                max={3}
                                value={internshipCount}
                                onChange={(e) => setInternshipCount(parseInt(e.target.value))}
                                className="flex-1 accent-rose-500"
                            />
                            <span className="text-lg font-bold text-rose-400 font-mono min-w-[40px] text-center">
                                {internshipCount}
                            </span>
                        </div>
                        <p className="text-[10px] text-slate-400 mt-1">
                            Maximum: 3 internships per run
                        </p>
                    </div>

                    {/* Total summary */}
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl p-4 text-center">
                        <span className="text-xs text-slate-400">Total Applications: </span>
                        <span className="text-xl font-extrabold text-rose-400 font-mono">
                            {jobCount + internshipCount}
                        </span>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center justify-end gap-3 pt-2 border-t border-white/10">
                        <button
                            onClick={onClose}
                            disabled={isStarting}
                            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 border border-white/10 hover:bg-white/5 transition-all"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={() => onStart(jobCount, internshipCount)}
                            disabled={isStarting || (jobCount === 0 && internshipCount === 0)}
                            className="btn-red-glow text-white font-bold px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 disabled:opacity-50"
                        >
                            {isStarting ? (
                                <>
                                    <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    Starting...
                                </>
                            ) : (
                                <>⚡ Start Auto-Apply</>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}