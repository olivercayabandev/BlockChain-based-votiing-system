@echo off
echo === Blockchain Voting System - Defense Setup ===
echo.

:: Step 1: Kill any existing processes on port 8000
echo Step 1: Checking port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
  echo   Killing process %%a...
  taskkill /PID %%a /F >nul
)
timeout /t 2 >nul

:: Step 2: Start backend in a new window
echo Step 2: Starting backend server...
start "Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 3 >nul

:: Step 3: Verify backend is running
echo Step 3: Verifying backend...
netstat -ano | findstr :8000 >nul
if errorlevel 1 (
    echo   ERROR: Backend failed to start!
    pause
    exit /b 1
)
echo   Backend running on port 8000

:: Step 4: Start tunnel in a new window
echo Step 4: Starting localtunnel...
start "Tunnel" cmd /k "lt --port 8000 --subdomain blockchain-voting-defense"
timeout /t 5 >nul

:: Step 5: Display results
echo.
echo === SYSTEM READY FOR DEFENSE ===
echo.
echo Public URL (share with defense panel):
echo   https://blockchain-voting-defense.loca.lt
echo.
echo Local URL (for your screen):
echo   http://localhost:8000
echo.
echo Test the URL now to make sure it works!
echo.
pause
