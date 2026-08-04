@echo off
REM Start Admin Portal Backend (port 8001)

echo ========================================
echo   Starting Admin Portal Backend...
echo ========================================
cd backend_admin

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies if needed
pip install -r requirements.txt -q

REM Run admin backend
echo.
echo Admin backend starting on http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.
uvicorn main:admin_app --host 0.0.0.0 --port 8001 --reload

pause