'use client';

import React from 'react';

export function JobsSkeleton() {
  return (
    <div className="space-y-4 w-full animate-pulse">
      {[...Array(4)].map((_, idx) => (
        <div 
          key={idx} 
          className="bg-slate-900/60 border border-slate-800/80 p-6 rounded-xl shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-6 overflow-hidden relative"
        >
          <div className="space-y-3 flex-1">
            <div className="flex items-center gap-3">
              <div className="h-6 w-48 bg-slate-800/80 rounded-lg"></div>
              <div className="h-5 w-16 bg-rose-950/40 border border-rose-900/30 rounded-full"></div>
            </div>
            <div className="flex flex-wrap items-center gap-4 pt-1">
              <div className="h-4 w-32 bg-slate-800/60 rounded-md"></div>
              <div className="h-4 w-24 bg-slate-800/60 rounded-md"></div>
              <div className="h-4 w-28 bg-slate-800/60 rounded-md"></div>
            </div>
            <div className="space-y-1.5 pt-2">
              <div className="h-3 w-full bg-slate-800/50 rounded"></div>
              <div className="h-3 w-4/5 bg-slate-800/50 rounded"></div>
            </div>
          </div>
          <div className="flex md:flex-col items-end justify-between gap-4 min-w-[200px]">
            <div className="space-y-1 text-right w-full flex flex-col items-end">
              <div className="h-3 w-20 bg-slate-800/60 rounded"></div>
              <div className="h-6 w-24 bg-rose-900/30 rounded-md"></div>
            </div>
            <div className="h-10 w-full bg-slate-800/80 rounded-lg"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function HistorySkeleton() {
  return (
    <div className="divide-y divide-slate-800/80 animate-pulse bg-slate-900/40 rounded-2xl border border-slate-800/80 overflow-hidden">
      {[...Array(5)].map((_, idx) => (
        <div key={idx} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2.5 flex-1">
            <div className="flex items-center gap-3">
              <div className="h-5 w-40 bg-slate-800/80 rounded-md"></div>
              <div className="h-5 w-16 bg-rose-950/40 rounded-full"></div>
              <div className="h-5 w-24 bg-slate-800/60 rounded-full"></div>
            </div>
            <div className="h-4 w-64 bg-slate-800/60 rounded-md"></div>
            <div className="h-3 w-80 bg-slate-800/40 rounded-md"></div>
          </div>
          <div className="h-8 w-44 bg-slate-800/60 rounded-lg"></div>
        </div>
      ))}
    </div>
  );
}

export function ProfileSkeleton() {
  return (
    <div className="grid lg:grid-cols-3 gap-8 animate-pulse">
      <div className="lg:col-span-1 space-y-6">
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-6">
          <div className="h-5 w-48 bg-slate-800/80 rounded-lg mb-4"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="space-y-1.5">
                <div className="h-3 w-24 bg-slate-800/60 rounded"></div>
                <div className="h-10 w-full bg-slate-800/40 rounded-xl"></div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="lg:col-span-2 space-y-8">
        <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl space-y-6">
          <div className="flex justify-between items-center pb-4 border-b border-slate-800">
            <div className="h-6 w-56 bg-slate-800/80 rounded-lg"></div>
            <div className="h-9 w-36 bg-slate-800/80 rounded-xl"></div>
          </div>
          <div className="space-y-3">
            <div className="h-4 w-32 bg-slate-800/80 rounded"></div>
            <div className="h-16 w-full bg-slate-950/60 rounded-xl p-3 space-y-2">
              <div className="h-3 w-full bg-slate-800/50 rounded"></div>
              <div className="h-3 w-3/4 bg-slate-800/50 rounded"></div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="h-4 w-28 bg-slate-800/80 rounded"></div>
            <div className="flex flex-wrap gap-2">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-7 w-20 bg-slate-800/60 rounded-full"></div>
              ))}
            </div>
          </div>
          <div className="space-y-3 pt-4 border-t border-slate-800/80">
            <div className="h-4 w-36 bg-slate-800/80 rounded"></div>
            <div className="space-y-3">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-20 w-full bg-slate-950/60 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ErrorCard({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="glass-panel p-8 rounded-2xl border border-rose-500/30 text-center space-y-4 bg-rose-950/20 max-w-lg mx-auto shadow-2xl">
      <div className="w-12 h-12 bg-rose-500/20 border border-rose-500/40 rounded-xl flex items-center justify-center mx-auto text-rose-300 text-2xl shadow-[0_0_15px_rgba(244,63,94,0.3)]">
        ⚠️
      </div>
      <div className="space-y-1">
        <h4 className="text-base font-bold text-slate-100">Failed to Load Data</h4>
        <p className="text-xs text-slate-300 font-mono bg-slate-950/60 p-3 rounded-xl border border-white/5">
          {message}
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-red-glow text-white text-xs font-bold py-2.5 px-6 rounded-xl inline-flex items-center gap-2 transition-all shadow-lg hover:scale-105"
        >
          <span>🔄 Retry Request</span>
        </button>
      )}
    </div>
  );
}
