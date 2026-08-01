'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function validateToken() {
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('auth_user');

      if (!storedToken) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/api/v1/users/me`, {
          headers: {
            'Authorization': `Bearer ${storedToken}`
          }
        });

        if (response.ok) {
          const userData = await response.json();
          setToken(storedToken);
          setUser({
            id: userData.id,
            email: userData.email
          });
        } else {
          // Token expired or invalid
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
          setToken(null);
          setUser(null);
        }
      } catch (err) {
        // If backend is down or unreachable during local offline dev, fallback to stored user session if present
        console.warn('Backend unreachable during token verification. Falling back to stored session.', err);
        if (storedUser) {
          try {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
          } catch (e) {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('auth_user');
          }
        }
      } finally {
        setIsLoading(false);
      }
    }

    validateToken();
  }, []);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem('auth_token', newToken);
    localStorage.setItem('auth_user', JSON.stringify(newUser));
    router.push('/');
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    router.push('/auth/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const isAuthRoute = pathname === '/auth/login' || pathname === '/auth/register';

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated && !isAuthRoute) {
        router.push('/auth/login');
      } else if (isAuthenticated && isAuthRoute) {
        router.push('/');
      }
    }
  }, [isLoading, isAuthenticated, isAuthRoute, router]);

  if (isLoading || (!isAuthenticated && !isAuthRoute) || (isAuthenticated && isAuthRoute)) {
    return (
      <div className="min-h-screen bg-[#090a0f] bg-grid-omni bg-coral-glow flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-rose-500/20 border-t-rose-500 rounded-full animate-spin shadow-[0_0_15px_rgba(244,63,94,0.5)]"></div>
          <span className="text-sm font-semibold text-slate-400 tracking-wider uppercase">Authenticating Workspace...</span>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
