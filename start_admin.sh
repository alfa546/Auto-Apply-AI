#!/bin/bash
# Start Admin Portal Backend (port 8001)

echo "🚀 Starting Admin Portal Backend..."
cd backend_admin

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/Scripts/activate  # On Windows

# Install dependencies if needed
pip install -r requirements.txt -q

# Run admin backend
echo "✅ Admin backend starting on http://localhost:8001"
uvicorn main:admin_app --host 0.0.0.0 --port 8001 --reload