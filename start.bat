@echo off
echo ========================================
echo Multi-Agent Game - Starting...
echo ========================================
echo.

echo [1/2] Starting Backend...
cd backend
start "Backend" cmd /k "..\venv\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo Backend starting... (http://localhost:8000)
echo.

echo [2/2] Starting Frontend...
cd ..\frontend
start "Frontend" cmd /k "npm run dev"
echo Frontend starting... (http://localhost:3000)
echo.

echo ========================================
echo Services Started!
echo Backend API: http://localhost:8000/docs
echo Frontend App: http://localhost:3000
echo ========================================
echo.
echo Press any key to close...
pause >nul
