'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error in ErrorBoundary:", error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-[#090a0f] bg-grid-omni text-slate-100 flex items-center justify-center p-6 selection:bg-rose-500 selection:text-white">
          <div className="glass-panel max-w-md w-full p-8 rounded-3xl border border-white/10 shadow-2xl text-center space-y-6 relative overflow-hidden bg-slate-900/60 backdrop-blur-2xl">
            <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-80 h-80 bg-rose-600/15 rounded-full blur-3xl pointer-events-none"></div>
            
            <div className="w-16 h-16 bg-rose-500/10 border border-rose-500/30 rounded-2xl flex items-center justify-center mx-auto text-3xl shadow-[0_0_20px_rgba(244,63,94,0.3)]">
              ⚠️
            </div>

            <div className="space-y-2 relative z-10">
              <h2 className="text-xl font-extrabold text-white tracking-tight">Something went wrong</h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                An unexpected error occurred in this application module. We have logged the error details to the console.
              </p>
              {this.state.error && (
                <div className="mt-4 p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-[11px] text-rose-300 font-mono text-left max-h-32 overflow-y-auto">
                  {this.state.error.message || this.state.error.toString()}
                </div>
              )}
            </div>

            <button
              onClick={this.handleRetry}
              className="w-full btn-red-glow text-white text-xs font-bold py-3 px-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
            >
              <span>🔄 Retry & Recover</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
