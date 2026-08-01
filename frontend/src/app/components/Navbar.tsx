"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../context/AuthContext";
import GmailModal from "./GmailModal";
import Toast from "./Toast";
import { DashboardIcon, GmailIcon, UserIcon, KeyIcon } from "./Icons";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Navbar() {
  const { user, token, isAuthenticated, logout } = useAuth();
  const pathname = usePathname();

  // Toast Notification State
  const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const showToast = (message: string, type: "success" | "error" = "success") => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification((prev) => (prev?.message === message ? null : prev));
    }, 4000);
  };

  // Gmail Connection Status State
  const [isGmailConnected, setIsGmailConnected] = useState(false);
  const [gmailEmail, setGmailEmail] = useState("");
  const [showGmailModal, setShowGmailModal] = useState(false);
  const [smtpPassword, setSmtpPassword] = useState("");

  const checkGmailStatus = useCallback(async () => {
    if (!isAuthenticated || !token) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/gmail/status`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setIsGmailConnected(data.is_connected);
        if (data.connected_email) setGmailEmail(data.connected_email);
      }
    } catch (err) {
      console.error("Gmail connection check error:", err);
    }
  }, [isAuthenticated, token]);

  useEffect(() => {
    checkGmailStatus();
  }, [checkGmailStatus]);

  // Handle modal close or successful connection to re-check status
  useEffect(() => {
    if (!showGmailModal) {
      checkGmailStatus();
    }
  }, [showGmailModal, checkGmailStatus]);

  const navLinks = [
    { href: "/opportunities", label: "Recommended Opportunities", icon: <DashboardIcon /> },
    { href: "/history", label: "Applications History", icon: <GmailIcon /> },
    { href: "/profile", label: "User Profile & CV Management", icon: <UserIcon /> },
    { href: "/settings", label: "API Settings", icon: <KeyIcon /> }
  ];

  return (
    <>
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link href="/opportunities" className="flex items-center gap-3 group">
              <div className="w-10 h-10 bg-gradient-to-br from-rose-500 to-red-600 rounded-xl flex items-center justify-center font-black text-xl shadow-[0_0_20px_rgba(244,63,94,0.4)] text-white group-hover:scale-105 transition-all">
                AI
              </div>
              <div>
                <h1 className="text-lg font-extrabold tracking-tight text-white flex items-center gap-2">
                  <span>AutoApply</span>
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-red-500 font-black">AI</span>
                </h1>
                <p className="text-[10px] font-medium text-slate-400 uppercase tracking-widest">Autonomous Suite</p>
              </div>
            </Link>
          </div>

          <div className="flex items-center gap-4">
            {user && (
              <div className="hidden md:flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-xl text-xs text-slate-300">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>User: <strong className="text-slate-200">{user.email}</strong></span>
              </div>
            )}

            <button
              onClick={() => setShowGmailModal(true)}
              className={`text-xs px-3.5 py-2 rounded-xl font-semibold flex items-center gap-2 transition-all border ${
                isGmailConnected
                  ? "bg-rose-950/80 text-rose-300 border-rose-500/30 hover:border-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.15)]"
                  : "bg-slate-900 text-slate-300 border-slate-800 hover:border-slate-700"
              }`}
            >
              <GmailIcon />
              <span>{isGmailConnected ? `Gmail Connected (${gmailEmail})` : "Connect Gmail"}</span>
              <span className={`w-2 h-2 rounded-full ${isGmailConnected ? "bg-rose-400 animate-ping" : "bg-amber-400"}`}></span>
            </button>

            <button
              onClick={logout}
              className="text-xs bg-slate-900/80 hover:bg-rose-950/40 text-slate-400 hover:text-rose-300 border border-slate-800 hover:border-rose-500/40 px-3.5 py-2 rounded-xl font-semibold transition-all shadow-sm flex items-center gap-1.5"
            >
              <span>Logout</span>
            </button>
          </div>
        </div>

        {/* Navigation Link Bar */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center gap-2 overflow-x-auto no-scrollbar pt-2 border-t border-slate-800/40">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`pb-3.5 px-6 font-semibold text-sm border-b-2 whitespace-nowrap transition-all flex items-center gap-2.5 rounded-t-xl ${
                  isActive
                    ? "border-rose-400 text-rose-300 bg-rose-950/20 shadow-[0_4px_20px_-4px_rgba(244,63,94,0.3)]"
                    : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                }`}
              >
                {link.icon}
                <span>{link.label}</span>
              </Link>
            );
          })}
        </div>
      </header>

      <Toast notification={notification} />

      {showGmailModal && (
        <GmailModal
          API_BASE={API_BASE}
          token={token}
          gmailEmail={gmailEmail}
          setGmailEmail={setGmailEmail}
          showGmailModal={showGmailModal}
          setShowGmailModal={setShowGmailModal}
          smtpPassword={smtpPassword}
          setSmtpPassword={setSmtpPassword}
          setIsGmailConnected={setIsGmailConnected}
          showToast={showToast}
        />
      )}
    </>
  );
}
