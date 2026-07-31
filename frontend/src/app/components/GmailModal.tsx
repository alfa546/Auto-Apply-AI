import React from "react";
import { GmailIcon } from "./Icons";

interface GmailModalProps {
  API_BASE: string;
  username: string;
  gmailEmail: string;
  setGmailEmail: (email: string) => void;
  showGmailModal: boolean;
  setShowGmailModal: (show: boolean) => void;
  smtpPassword: string;
  setSmtpPassword: (password: string) => void;
  setIsGmailConnected: (connected: boolean) => void;
  showToast: (message: string, type?: "success" | "error") => void;
}

export default function GmailModal({
  API_BASE,
  username,
  gmailEmail,
  setGmailEmail,
  showGmailModal,
  setShowGmailModal,
  smtpPassword,
  setSmtpPassword,
  setIsGmailConnected,
  showToast
}: GmailModalProps) {
  if (!showGmailModal) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full space-y-5 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <GmailIcon />
            <span>Connect Gmail Account</span>
          </h3>
          <button onClick={() => setShowGmailModal(false)} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>

        <div className="space-y-4 text-xs">
          <p className="text-slate-300 leading-relaxed">
            Connecting your Gmail account allows the AI Agent to send job application emails directly from your personal Gmail address. Every sent application will appear directly in your Gmail <strong>"Sent"</strong> folder!
          </p>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Your Gmail Address</label>
            <input 
              type="email" 
              value={gmailEmail}
              onChange={e => setGmailEmail(e.target.value)}
              placeholder="name@gmail.com"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
            />
          </div>

          {/* Option 1: Fast Google OAuth */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-200">Option 1: Google OAuth 2.0 (Fast 1-Click)</span>
              <span className="bg-rose-950 text-rose-300 border border-rose-500/30 text-[10px] px-2 py-0.5 rounded font-semibold">Recommended</span>
            </div>
            <button
              onClick={async () => {
                try {
                  const res = await fetch(`${API_BASE}/api/v1/auth/gmail/url`, {
                    headers: { "Authorization": `Bearer dev-mock-${username}` }
                  });
                  if (res.ok) {
                    const data = await res.json();
                    if (data.auth_url) {
                      window.location.href = data.auth_url;
                      return;
                    }
                    setIsGmailConnected(true);
                    setShowGmailModal(false);
                    showToast(`Successfully connected Gmail via Google OAuth as ${gmailEmail || 'User'}!`);
                  } else {
                    showToast("Failed to connect via Google OAuth.", "error");
                  }
                } catch (err) {
                  showToast(err instanceof Error ? err.message : "Failed to connect via Google OAuth.", "error");
                }
              }}
              className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-semibold py-2.5 px-4 rounded-lg text-xs flex items-center justify-center gap-2 transition-all shadow-lg shadow-red-900/30"
            >
              <GmailIcon />
              <span>Connect with Google OAuth</span>
            </button>
          </div>

          {/* Option 2: Gmail App Password (SMTP) */}
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <span className="font-bold text-slate-200 block">Option 2: Gmail App Password (SMTP)</span>
            <div>
              <label className="block text-slate-400 mb-1">Google App Password (16 Characters)</label>
              <input 
                type="password"
                placeholder="xxxx xxxx xxxx xxxx"
                value={smtpPassword}
                onChange={e => setSmtpPassword(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
              />
              <p className="text-[10px] text-slate-400 mt-1">Generated via Google Account &gt; Security &gt; 2-Step Verification &gt; App Passwords.</p>
            </div>

            <button
              onClick={async () => {
                if (!smtpPassword) {
                  showToast("Please enter your 16-character App Password", "error");
                  return;
                }
                try {
                  const res = await fetch(`${API_BASE}/api/v1/auth/gmail/setup-smtp`, {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                      "Authorization": `Bearer dev-mock-${username}`
                    },
                    body: JSON.stringify({ email: gmailEmail, app_password: smtpPassword })
                  });
                  if (res.ok) {
                    setIsGmailConnected(true);
                    setShowGmailModal(false);
                    showToast(`Connected Gmail SMTP for ${gmailEmail}!`);
                  } else {
                    showToast(`Failed to connect Gmail SMTP for ${gmailEmail}.`, "error");
                  }
                } catch (err) {
                  showToast(err instanceof Error ? err.message : `Failed to connect Gmail SMTP for ${gmailEmail}.`, "error");
                }
              }}
              className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-2 px-4 rounded-lg text-xs transition-all border border-slate-700"
            >
              Connect via App Password
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
