import React from "react";
import { KeyIcon, LockIcon, SparklesIcon, GmailIcon, GlobeIcon } from "./Icons";

interface SettingsTabProps {
  showApiKeys: boolean;
  setShowApiKeys: (v: boolean) => void;
  llmProvider: string;
  setLlmProvider: (v: string) => void;
  llmModel: string;
  setLlmModel: (v: string) => void;
  customApiBase: string;
  setCustomApiBase: (v: string) => void;
  openaiApiKey: string;
  setOpenaiApiKey: (v: string) => void;
  googleClientId: string;
  setGoogleClientId: (v: string) => void;
  googleClientSecret: string;
  setGoogleClientSecret: (v: string) => void;
  isGmailConnected: boolean;
  gmailEmail: string;
  setShowGmailModal: (v: boolean) => void;
  adzunaAppId: string;
  setAdzunaAppId: (v: string) => void;
  adzunaAppKey: string;
  setAdzunaAppKey: (v: string) => void;
  joobleApiKey: string;
  setJoobleApiKey: (v: string) => void;
  isSavingApiSettings: boolean;
  handleSaveApiSettings: (e: React.FormEvent) => void;
}

export default function SettingsTab({
  showApiKeys, setShowApiKeys,
  llmProvider, setLlmProvider,
  llmModel, setLlmModel,
  customApiBase, setCustomApiBase,
  openaiApiKey, setOpenaiApiKey,
  googleClientId, setGoogleClientId,
  googleClientSecret, setGoogleClientSecret,
  isGmailConnected, gmailEmail, setShowGmailModal,
  adzunaAppId, setAdzunaAppId,
  adzunaAppKey, setAdzunaAppKey,
  joobleApiKey, setJoobleApiKey,
  isSavingApiSettings, handleSaveApiSettings
}: SettingsTabProps) {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div className="omni-card p-8 rounded-3xl space-y-6 border border-white/10">
        <div className="flex items-center justify-between border-b border-white/10 pb-5">
          <div>
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2.5">
              <KeyIcon />
              <span>API Keys & Integration Settings Vault</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">Configure your AI model keys, Google OAuth, Gmail credentials, and search API keys for maximum performance.</p>
          </div>
          <button
            onClick={() => setShowApiKeys(!showApiKeys)}
            className="btn-dark-outline text-xs font-semibold px-3.5 py-1.5 rounded-xl text-slate-300 transition-all flex items-center gap-1.5"
          >
            <LockIcon />
            <span>{showApiKeys ? "Hide Keys" : "Show Keys"}</span>
          </button>
        </div>

        <form onSubmit={handleSaveApiSettings} className="space-y-6 text-xs">
          {/* Section 1: AI Model Provider & API Key Settings */}
          <div className="bg-[#12141d] border border-white/10 p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                <SparklesIcon />
                <span>🧠 AI Model Provider & Key Vault</span>
              </h4>
              <span className="text-[10px] bg-rose-950/80 text-rose-300 border border-rose-500/30 px-2.5 py-0.5 rounded font-mono">
                Includes 100% Free Open-Source Models
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Select AI Provider (Free & Paid)</label>
                <select
                  value={llmProvider}
                  onChange={e => setLlmProvider(e.target.value)}
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 text-xs font-medium"
                >
                  <option value="openai">OpenAI (GPT-4o, GPT-4o-mini)</option>
                  <option value="ollama">Ollama / LM Studio (100% Free Local Offline Models)</option>
                  <option value="groq">Groq Cloud (Free Open Source Models Tier)</option>
                  <option value="openrouter">OpenRouter (Free Open Source Models API)</option>
                  <option value="gemini">Google Gemini (Gemini 1.5 Pro, Flash)</option>
                  <option value="deepseek">DeepSeek (DeepSeek V3, DeepSeek R1)</option>
                  <option value="custom">Custom OpenAI-Compatible Endpoint</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">AI Model Name</label>
                <input 
                  type="text"
                  value={llmModel}
                  onChange={e => setLlmModel(e.target.value)}
                  placeholder="gpt-4o, llama3, llama-3.1-70b, deepseek-chat..."
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
                />
              </div>
            </div>

            {(llmProvider === "ollama" || llmProvider === "custom") && (
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Custom API Base URL (Ollama / Local LLM / LM Studio)</label>
                <input 
                  type="text"
                  value={customApiBase}
                  onChange={e => setCustomApiBase(e.target.value)}
                  placeholder="http://localhost:11434/v1 or http://localhost:1234/v1"
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
                />
                <p className="text-[10px] text-slate-400 mt-1">Default Ollama URL: http://localhost:11434/v1 (No paid API Key needed! Runs 100% offline & free).</p>
              </div>
            )}

            <div>
              <label className="block text-slate-300 font-semibold mb-1">AI Model API Key (Leave empty if using local Ollama/LM Studio)</label>
              <input 
                type={showApiKeys ? "text" : "password"}
                value={openaiApiKey}
                onChange={e => setOpenaiApiKey(e.target.value)}
                placeholder="sk-proj-..., gsk_..., sk-or-v1-..."
                className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
              />
              <p className="text-[10px] text-slate-400 mt-1">Supports free Groq keys (gsk_), free OpenRouter keys (sk-or-v1-), OpenAI keys, or free local Ollama endpoints!</p>
            </div>
          </div>

          {/* Section 2: Google OAuth 2.0 Credentials */}
          <div className="bg-[#12141d] border border-white/10 p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                <GmailIcon />
                <span>🌐 Google OAuth 2.0 Credentials</span>
              </h4>
              <span className="text-[10px] bg-rose-950/80 text-rose-300 border border-rose-500/30 px-2.5 py-0.5 rounded font-mono">
                Official Gmail API
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Google Client ID</label>
                <input 
                  type="text"
                  value={googleClientId}
                  onChange={e => setGoogleClientId(e.target.value)}
                  placeholder="123456789-xxx.apps.googleusercontent.com"
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Google Client Secret</label>
                <input 
                  type={showApiKeys ? "text" : "password"}
                  value={googleClientSecret}
                  onChange={e => setGoogleClientSecret(e.target.value)}
                  placeholder="GOCSPX-..."
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
                />
              </div>
            </div>
          </div>

          {/* Section 3: Gmail Connection Hub */}
          <div className="bg-[#12141d] border border-white/10 p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                <GmailIcon />
                <span>✉️ Connected Gmail Account</span>
              </h4>
              <span className={`text-[10px] px-2.5 py-0.5 rounded font-mono ${
                isGmailConnected 
                  ? "bg-rose-950/80 text-rose-300 border border-rose-500/30" 
                  : "bg-red-950/80 text-red-300 border border-red-500/30"
              }`}>
                {isGmailConnected ? "Connected" : "Disconnected"}
              </span>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <span className="text-xs text-slate-300">Active Gmail Address: <strong>{gmailEmail || "Not Connected"}</strong></span>
                <p className="text-[10px] text-slate-400 mt-0.5">The agent sends candidate CVs and cover letters directly from this Gmail account.</p>
              </div>

              <button
                type="button"
                onClick={() => setShowGmailModal(true)}
                className="btn-red-glow text-white font-bold px-4 py-2 rounded-xl text-xs whitespace-nowrap"
              >
                {isGmailConnected ? "Re-Configure Gmail" : "Connect Gmail Account"}
              </button>
            </div>
          </div>

          {/* Section 4: Multi-Country Job Search Provider API Keys */}
          <div className="bg-[#12141d] border border-white/10 p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                <GlobeIcon />
                <span>🔍 Job Search Provider API Keys</span>
              </h4>
              <span className="text-[10px] bg-rose-950/80 text-rose-300 border border-rose-500/30 px-2.5 py-0.5 rounded font-mono">
                Multi-Country Scrapers
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Adzuna App ID</label>
                <input 
                  type="text"
                  value={adzunaAppId}
                  onChange={e => setAdzunaAppId(e.target.value)}
                  placeholder="Adzuna App ID"
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Adzuna App Key</label>
                <input 
                  type={showApiKeys ? "text" : "password"}
                  value={adzunaAppKey}
                  onChange={e => setAdzunaAppKey(e.target.value)}
                  placeholder="Adzuna App Key"
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Jooble API Key</label>
                <input 
                  type={showApiKeys ? "text" : "password"}
                  value={joobleApiKey}
                  onChange={e => setJoobleApiKey(e.target.value)}
                  placeholder="Jooble API Key"
                  className="w-full omni-input rounded-xl px-3.5 py-2.5 font-mono text-xs"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end pt-2">
            <button
              type="submit"
              disabled={isSavingApiSettings}
              className="btn-red-glow text-white font-bold px-6 py-3 rounded-xl text-xs"
            >
              {isSavingApiSettings ? "Saving API Vault..." : "Save All API Keys & Integration Credentials"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
