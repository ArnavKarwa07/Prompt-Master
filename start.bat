@echo off
echo Starting Prompt Master (Full Stack)...
echo.

echo Starting Backend (Port 8000)...
start "Prompt Master Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 5 /nobreak > nul

echo Starting Frontend (Port 3000)...
start "Prompt Master Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both servers are starting...
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Opening browser...
timeout /t 5 /nobreak > nul
start http://localhost:3000
