"use client";

import React, { useState } from "react";

interface EmailReviewModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    preview: {
        job_title: string;
        company: string;
        recipient_email: string;
        sender_email: string;
        subject: string;
        cover_letter: string;
        has_resume_attachment: boolean;
        resume_filename?: string | null;
    } | null;
    isSending: boolean;
}

export default function EmailReviewModal({
    isOpen,
    onClose,
    onConfirm,
    preview,
    isSending
}: EmailReviewModalProps) {
    const [showFullLetter, setShowFullLetter] = useState(false);

    if (!isOpen || !preview) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="bg-[#12141d] border border-white/10 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto custom-scrollbar">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-white/10 p-5 sticky top-0 bg-[#12141d] z-10">
                    <div>
                        <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                            <span className="text-rose-400">✉️</span>
                            <span>Review Email Application</span>
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">Review before sending to {preview.company}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-200 text-xl font-bold px-2"
                        aria-label="Close"
                    >
                        ✕
                    </button>
                </div>

                <div className="p-5 space-y-4">
                    {/* Job & Recipient Info */}
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl p-4 space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-300">Position:</span>
                            <span className="text-xs font-bold text-rose-300">{preview.job_title}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-300">Company:</span>
                            <span className="text-xs font-bold text-slate-200">{preview.company}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-300">To:</span>
                            <span className="text-xs font-mono text-slate-200">{preview.recipient_email}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-300">From:</span>
                            <span className="text-xs font-mono text-slate-200">{preview.sender_email}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-300">Subject:</span>
                            <span className="text-xs font-mono text-slate-200">{preview.subject}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-slate-300">Attachment:</span>
                            <span className="text-xs font-mono text-emerald-400">
                                {preview.has_resume_attachment ? `📄 ${preview.resume_filename || "Resume.pdf"}` : "⚠️ No resume attached"}
                            </span>
                        </div>
                    </div>

                    {/* Cover Letter Preview */}
                    <div className="bg-[#090a0f] border border-white/10 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-3">
                            <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider">Cover Letter</h4>
                            <button
                                onClick={() => setShowFullLetter(!showFullLetter)}
                                className="text-[10px] text-rose-300 hover:text-rose-200 font-semibold border border-rose-500/30 px-2 py-0.5 rounded"
                            >
                                {showFullLetter ? "Show Less" : "Show Full"}
                            </button>
                        </div>
                        <pre className="text-xs text-slate-300 whitespace-pre-wrap font-sans leading-relaxed max-h-64 overflow-y-auto custom-scrollbar">
                            {showFullLetter ? preview.cover_letter : preview.cover_letter.slice(0, 500) + (preview.cover_letter.length > 500 ? "..." : "")}
                        </pre>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center justify-end gap-3 pt-2 border-t border-white/10">
                        <button
                            onClick={onClose}
                            disabled={isSending}
                            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 border border-white/10 hover:bg-white/5 transition-all"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={onConfirm}
                            disabled={isSending}
                            className="btn-red-glow text-white font-bold px-6 py-2.5 rounded-xl text-xs flex items-center gap-2"
                        >
                            {isSending ? (
                                <>
                                    <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    Sending...
                                </>
                            ) : (
                                <>🚀 Confirm & Send Email</>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}