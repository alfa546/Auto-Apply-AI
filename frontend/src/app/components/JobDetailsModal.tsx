"use client";

import React from "react";
import { Job } from "../types";
import { GmailIcon } from "./Icons";

interface JobDetailsModalProps {
    job: Job | null;
    isOpen: boolean;
    onClose: () => void;
    onApply: (job: Job) => void;
    isApplying: boolean;
}

export default function JobDetailsModal({
    job,
    isOpen,
    onClose,
    onApply,
    isApplying
}: JobDetailsModalProps) {
    if (!isOpen || !job) return null;

    // Parse enhanced description with metadata and clean scraper snippet artifacts
    const parseDescription = (raw: string | undefined) => {
        if (!raw) return { metadata: [], description: "No description available for this position." };

        // Split by separator to get metadata and description
        const parts = raw.split('='.repeat(50));
        const metadataPart = parts[0] || "";
        let descriptionPart = parts.length > 1 ? parts[1] : raw;

        // Strip default header if included in text
        descriptionPart = descriptionPart.replace(/^\s*📋\s*Job\s*Description:\s*/i, "");

        // Extract metadata lines
        const metadataLines = metadataPart.split('\n').filter(line =>
            line.trim() && (line.includes('🏢') || line.includes('📍') || line.includes('🌍') || line.includes('💰'))
        );

        // Clean description part
        let cleanDesc = descriptionPart
            .replace(/<[^>]+>/g, "\n")
            .replace(/&nbsp;/g, " ")
            .replace(/&/g, "&")
            .replace(/</g, "<")
            .replace(/>/g, ">")
            .replace(/"/g, '"')
            .replace(/&#39;/g, "'")
            .replace(/\n{3,}/g, "\n\n")
            .trim();

        // Remove ugly leading/trailing ellipses from search engine snippet truncations
        cleanDesc = cleanDesc.replace(/^\.{2,}\s*/, "").replace(/,?\s*\.{2,}$/, "").trim();
        if (cleanDesc.length > 0) {
            cleanDesc = cleanDesc.charAt(0).toUpperCase() + cleanDesc.slice(1);
        }

        return { metadata: metadataLines, description: cleanDesc };
    };

    const { metadata, description } = parseDescription(job.description);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="bg-[#12141d] border border-white/10 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto custom-scrollbar">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-white/10 p-5 sticky top-0 bg-[#12141d] z-10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-rose-500/20 to-red-500/20 border border-rose-500/40 rounded-xl flex items-center justify-center text-rose-300">
                            💼
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-slate-100">{job.title}</h3>
                            <p className="text-xs text-slate-400">{job.company}</p>
                        </div>
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
                    {/* Job Meta Info */}
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        <div className="bg-[#090a0f] border border-white/10 rounded-xl p-3">
                            <div className="text-[10px] text-slate-400 uppercase tracking-wider">Country</div>
                            <div className="text-sm font-bold text-slate-200 mt-0.5">
                                {job.country ? job.country.toUpperCase() : "Not specified"}
                            </div>
                        </div>
                        <div className="bg-[#090a0f] border border-white/10 rounded-xl p-3">
                            <div className="text-[10px] text-slate-400 uppercase tracking-wider">Location</div>
                            <div className="text-sm font-bold text-slate-200 mt-0.5">{job.location || "Remote / Not specified"}</div>
                        </div>
                        <div className="bg-[#090a0f] border border-white/10 rounded-xl p-3">
                            <div className="text-[10px] text-slate-400 uppercase tracking-wider">Type</div>
                            <div className="text-sm font-bold text-slate-200 mt-0.5">
                                <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${job.opportunity_type === "internship"
                                    ? "bg-amber-950/80 text-amber-300 border border-amber-500/30"
                                    : "bg-rose-950/80 text-rose-300 border border-rose-500/30"
                                    }`}>
                                    {(job.opportunity_type || "job").toUpperCase()}
                                </span>
                            </div>
                        </div>
                        {job.salary && (
                            <div className="bg-[#090a0f] border border-white/10 rounded-xl p-3">
                                <div className="text-[10px] text-slate-400 uppercase tracking-wider">Salary</div>
                                <div className="text-sm font-bold text-amber-300 mt-0.5">{job.salary}</div>
                            </div>
                        )}
                        {job.company_email && (
                            <div className="bg-[#090a0f] border border-white/10 rounded-xl p-3 col-span-2">
                                <div className="text-[10px] text-slate-400 uppercase tracking-wider">HR Contact</div>
                                <div className="text-sm font-mono text-rose-300 mt-0.5">{job.company_email}</div>
                            </div>
                        )}
                        {job.match_score && (
                            <div className="bg-[#090a0f] border border-white/10 rounded-xl p-3">
                                <div className="text-[10px] text-slate-400 uppercase tracking-wider">AI Match</div>
                                <div className="text-sm font-extrabold text-rose-400 mt-0.5">{job.match_score}%</div>
                            </div>
                        )}
                    </div>

                    {/* Authentic Original Job Description */}
                    <div className="space-y-4 max-h-[52vh] overflow-y-auto custom-scrollbar pr-1">
                        {metadata.length > 0 && (
                            <div className="bg-[#090a0f] border border-white/10 rounded-xl p-3.5 flex flex-wrap gap-4">
                                {metadata.map((line, idx) => (
                                    <span key={idx} className="text-xs text-slate-300 font-semibold font-mono flex items-center">{line}</span>
                                ))}
                            </div>
                        )}

                        {/* Original Job Description (Purely from API/Source, No Generated Content) */}
                        <div className="bg-slate-950/90 border border-slate-800/80 rounded-xl p-5 space-y-3 shadow-md">
                            <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
                                <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                                    <span>📋</span>
                                    <span>Original Job Description & Requirements</span>
                                </h4>
                                <span className="text-[10px] bg-slate-900 text-slate-400 border border-slate-700/80 px-2.5 py-0.5 rounded-full font-mono">
                                    Original API Data
                                </span>
                            </div>
                            
                            <div className="text-xs text-slate-200 whitespace-pre-wrap font-sans leading-relaxed pt-1">
                                {description || "No detailed job description provided by the original job provider."}
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center justify-end gap-3 pt-2 border-t border-white/10">
                        <button
                            onClick={onClose}
                            disabled={isApplying}
                            className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-300 border border-white/10 hover:bg-white/5 transition-all"
                        >
                            Close
                        </button>
                        <button
                            onClick={() => onApply(job)}
                            disabled={isApplying}
                            className="btn-red-glow text-white font-bold px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 transition-all disabled:opacity-50"
                        >
                            {isApplying ? (
                                <>
                                    <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    Preparing Preview...
                                </>
                            ) : (
                                <>
                                    <GmailIcon />
                                    <span>Apply with Email</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}