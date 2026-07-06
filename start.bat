@echo off
title HEI Student Activity Record Launcher
echo =======================================================
echo     Starting HEI Student Activity Record Platform
echo =======================================================
echo.

echo [1/2] Starting Backend API on port 8000...
start "HEI Backend Server" cmd /k ".\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000"

echo [2/2] Starting Frontend Server on port 5500...
start "HEI Frontend Server" cmd /k ".\venv\Scripts\python.exe -m http.server 5500 --directory frontend"

echo.
echo =======================================================
echo Both servers have been launched in separate windows!
echo - Backend API ^& Mounted Frontend: http://localhost:8000
echo - Standalone Frontend Developer Link: http://localhost:5500
echo =======================================================
echo.
pause
