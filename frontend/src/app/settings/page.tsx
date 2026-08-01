"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import SettingsTab from "../components/SettingsTab";
import ErrorBoundary from "../components/ErrorBoundary";
import Toast from "../components/Toast";
import GmailModal from "../components/GmailModal";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function SettingsPage() {
  const { token, isAuthenticated } = useAuth();

  const [showApiKeys, setShowApiKeys] = useState(false);
  const [llmProvider, setLlmProvider] = useState("openai");
  const [llmModel, setLlmModel] = useState("gpt-4o");
  const [customApiBase, setCustomApiBase] = useState("");
  const [openaiApiKey, setOpenaiApiKey] = useState("");
  const [googleClientId, setGoogleClientId] = useState("");
  const [googleClientSecret, setGoogleClientSecret] = useState("");
  const [adzunaAppId, setAdzunaAppId] = useState("");
  const [adzunaAppKey, setAdzunaAppKey] = useState("");
  const [joobleApiKey, setJoobleApiKey] = useState("");
  const [isSavingApiSettings, setIsSavingApiSettings] = useState(false);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([
    "United States", "United Kingdom", "Canada", "Australia",
    "Germany", "France", "Singapore", "Netherlands",
    "Sweden", "Switzerland", "United Arab Emirates"
  ]);

  // Gmail modal & connection status in settings
  const [isGmailConnected, setIsGmailConnected] = useState(false);
  const [gmailEmail, setGmailEmail] = useState("");
  const [showGmailModal, setShowGmailModal] = useState(false);
  const [smtpPassword, setSmtpPassword] = useState("");

  // Toast Notification State
  const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification((prev) => (prev?.message === message ? null : prev));
    }, 4000);
  };

  const checkGmailStatus = useCallback(async () => {
    if (!token) return;
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
  }, [token]);

  const fetchUserSettings = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/users/settings`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.llm_provider) setLlmProvider(data.llm_provider);
        if (data.llm_model) setLlmModel(data.llm_model);
        if (data.custom_api_base !== undefined) setCustomApiBase(data.custom_api_base || "");
        if (data.openai_api_key) setOpenaiApiKey(data.openai_api_key);
        if (data.google_client_id) setGoogleClientId(data.google_client_id);
        if (data.google_client_secret) setGoogleClientSecret(data.google_client_secret);
        if (data.adzuna_app_id) setAdzunaAppId(data.adzuna_app_id);
        if (data.adzuna_app_key) setAdzunaAppKey(data.adzuna_app_key);
        if (data.jooble_api_key) setJoobleApiKey(data.jooble_api_key);
        if (data.target_countries?.length) {
          setSelectedCountries(data.target_countries);
        }
      }
    } catch (err) {
      console.error("Failed to fetch user API settings:", err);
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated || !token) return;
    fetchUserSettings();
    checkGmailStatus();
  }, [isAuthenticated, token, fetchUserSettings, checkGmailStatus]);

  const handleSaveApiSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingApiSettings(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/users/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          llm_provider: llmProvider,
          llm_model: llmModel,
          custom_api_base: customApiBase,
          openai_api_key: openaiApiKey,
          google_client_id: googleClientId,
          google_client_secret: googleClientSecret,
          adzuna_app_id: adzunaAppId,
          adzuna_app_key: adzunaAppKey,
          jooble_api_key: joobleApiKey,
          target_countries: selectedCountries
        })
      });
      if (res.ok) {
        showToast("Successfully saved API keys & integration credentials!");
      } else {
        showToast("Failed to save API settings.", "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Failed to save API settings.", "error");
    } finally {
      setIsSavingApiSettings(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090a0f] bg-grid-omni text-slate-100 selection:bg-rose-500 selection:text-white">
      <Toast notification={notification} />
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary>
          <SettingsTab
            showApiKeys={showApiKeys} setShowApiKeys={setShowApiKeys}
            llmProvider={llmProvider} setLlmProvider={setLlmProvider}
            llmModel={llmModel} setLlmModel={setLlmModel}
            customApiBase={customApiBase} setCustomApiBase={setCustomApiBase}
            openaiApiKey={openaiApiKey} setOpenaiApiKey={setOpenaiApiKey}
            googleClientId={googleClientId} setGoogleClientId={setGoogleClientId}
            googleClientSecret={googleClientSecret} setGoogleClientSecret={setGoogleClientSecret}
            isGmailConnected={isGmailConnected} gmailEmail={gmailEmail} setShowGmailModal={setShowGmailModal}
            adzunaAppId={adzunaAppId} setAdzunaAppId={setAdzunaAppId}
            adzunaAppKey={adzunaAppKey} setAdzunaAppKey={setAdzunaAppKey}
            joobleApiKey={joobleApiKey} setJoobleApiKey={setJoobleApiKey}
            isSavingApiSettings={isSavingApiSettings} handleSaveApiSettings={handleSaveApiSettings}
          />
        </ErrorBoundary>
      </main>

      {showGmailModal && (
        <GmailModal
          API_BASE={API_BASE}
          showGmailModal={showGmailModal}
          gmailEmail={gmailEmail}
          setGmailEmail={setGmailEmail}
          smtpPassword={smtpPassword}
          setSmtpPassword={setSmtpPassword}
          isGmailConnected={isGmailConnected}
          handleConnectGmail={async (e: React.FormEvent) => {
            e.preventDefault();
            try {
              const res = await fetch(`${API_BASE}/api/v1/auth/gmail/connect`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ email: gmailEmail, app_password: smtpPassword })
              });
              if (res.ok) {
                setIsGmailConnected(true);
                setShowGmailModal(false);
                checkGmailStatus();
              } else {
                const errData = await res.json().catch(() => ({}));
                alert(errData.detail || "Failed to connect Gmail credentials.");
              }
            } catch (err) {
              alert("Failed to reach server when connecting Gmail.");
            }
          }}
          handleDisconnectGmail={async () => {
            try {
              const res = await fetch(`${API_BASE}/api/v1/auth/gmail/disconnect`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` }
              });
              if (res.ok) {
                setIsGmailConnected(false);
                setGmailEmail("");
                setSmtpPassword("");
                setShowGmailModal(false);
                checkGmailStatus();
              }
            } catch (err) {
              alert("Failed to disconnect Gmail account.");
            }
          }}
          setShowGmailModal={setShowGmailModal}
        />
      )}
    </div>
  );
}
