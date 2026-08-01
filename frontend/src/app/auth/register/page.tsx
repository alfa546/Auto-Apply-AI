'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/context/AuthContext';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const data = await response.json();
      login(data.access_token, data.user);
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090a0f] bg-grid-omni bg-coral-glow text-slate-100 font-sans flex items-center justify-center p-4 selection:bg-rose-500 selection:text-white">
      <div className="glass-panel p-8 sm:p-10 rounded-2xl max-w-md w-full text-center space-y-6 border border-white/10 shadow-2xl relative overflow-hidden bg-slate-900/40 backdrop-blur-2xl">
        <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-rose-600/15 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10">
          <img src="/logo.png" alt="Auto-Apply AI Logo" className="w-16 h-16 mx-auto mb-4 object-contain rounded-xl shadow-[0_0_20px_rgba(244,63,94,0.4)]" />
          <h2 className="text-2xl font-extrabold text-white tracking-tight mb-1">Create Your Workspace</h2>
          <p className="text-slate-400 text-xs mb-6">Set up your account to start automating job searches, matching, and Gmail dispatching.</p>

          <form onSubmit={handleSubmit} className="space-y-4 text-left">
            {error && (
              <div className="bg-rose-950/80 border border-rose-500/50 text-rose-200 px-4 py-3 rounded-xl text-xs flex items-center gap-2">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                placeholder="you@domain.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-700/50 focus:border-rose-500/80 focus:ring-1 focus:ring-rose-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-all placeholder:text-slate-600"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-700/50 focus:border-rose-500/80 focus:ring-1 focus:ring-rose-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-all placeholder:text-slate-600"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-700/50 focus:border-rose-500/80 focus:ring-1 focus:ring-rose-500/50 outline-none text-white rounded-xl px-4 py-3 text-sm transition-all placeholder:text-slate-600"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-red-glow text-white font-bold py-3 px-4 rounded-xl shadow-lg transition-all mt-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading && <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>}
              <span>{isLoading ? 'Creating Workspace...' : 'Create Account & Start'}</span>
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-white/10 text-xs text-slate-400">
            Already have a workspace?{' '}
            <button
              onClick={() => router.push('/auth/login')}
              className="font-bold text-rose-400 hover:text-rose-300 transition-colors"
            >
              Sign In Here
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
