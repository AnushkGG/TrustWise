@echo off
REM TrustWise Web Interface Launcher for Windows

echo ============================================================
echo TrustWise Web Interface (TypeScript)
echo ============================================================
echo.
echo Building TypeScript server...
echo.

cd /d "%~dp0..\frontend"
call npm run build
if errorlevel 1 (
    echo Build failed
    pause
    exit /b 1
)

echo.
echo Starting server...
echo.
echo Once started, open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

call npm start

pause
