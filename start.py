#!/usr/bin/env python3
"""
Auto-Apply AI - Single Command Full Stack Launcher
Run: python start.py
Starts: Backend (port 8000) + Frontend (port 3000) + Opens Browser
"""

import os
import sys
import time
import subprocess
import webbrowser
import shutil
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        🚀 Auto-Apply AI - Full Stack Launcher            ║
    ║        Backend: http://localhost:8000                    ║
    ║        Frontend: http://localhost:3000                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def check_backend_deps():
    """Check if backend dependencies are installed."""
    print("📦 Checking backend dependencies...")
    try:
        import fastapi, uvicorn, sqlalchemy  # noqa
        print("✅ Backend dependencies already installed.")
        return True
    except ImportError:
        print("⚠️ Backend dependencies missing. Installing...")
        subprocess.run(
            f'"{sys.executable}" -m pip install -r requirements.txt',
            cwd=BACKEND_DIR,
            shell=True,
            check=True
        )
        print("✅ Backend dependencies installed.")
        return True

def check_frontend_deps():
    """Check if frontend node_modules exists."""
    print("📦 Checking frontend dependencies...")
    node_modules = os.path.join(FRONTEND_DIR, "node_modules")
    if os.path.exists(node_modules):
        print("✅ Frontend dependencies already installed.")
        return True
    print("⚠️ Frontend dependencies missing. Installing...")
    subprocess.run("npm install", cwd=FRONTEND_DIR, shell=True, check=True)
    print("✅ Frontend dependencies installed.")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting backend server on http://localhost:8000 ...")
    return subprocess.Popen(
        f'"{sys.executable}" -m uvicorn src.app.main:app --reload --port 8000',
        cwd=BACKEND_DIR,
        shell=True
    )

def start_frontend():
    """Start the Next.js frontend server."""
    print("🚀 Starting frontend server on http://localhost:3000 ...")
    return subprocess.Popen(
        "npm run dev",
        cwd=FRONTEND_DIR,
        shell=True
    )

def main():
    print_banner()
    
    # 1. Check dependencies
    check_backend_deps()
    check_frontend_deps()
    
    # 2. Start servers
    backend_proc = start_backend()
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    frontend_proc = start_frontend()
    print("⏳ Waiting for frontend to start...")
    time.sleep(5)
    
    # 3. Open browser
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:3000")
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  ✅ Auto-Apply AI is running!                            ║
    ║  📱 Frontend: http://localhost:3000                      ║
    ║  🔧 Backend API: http://localhost:8000                   ║
    ║  📊 API Docs: http://localhost:8000/docs                 ║
    ║  Press Ctrl+C to stop all servers.                       ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Keep running until Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Auto-Apply AI...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("✅ All servers stopped. Goodbye!")

if __name__ == "__main__":
    main()
