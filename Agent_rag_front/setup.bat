@echo off
REM RAG Chatbot - Quick Setup Script (Windows)

setlocal enabledelayedexpansion

echo 🚀 RAG Chatbot Setup
echo ====================
echo.

REM Check for Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js not found!
    echo Install from: https://nodejs.org/
    exit /b 1
)

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo Install from: https://www.python.org/
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do echo ✅ Node.js version: %%i
for /f "tokens=*" %%i in ('python --version') do echo ✅ Python version: %%i
echo.

REM Install dependencies
echo 📦 Installing dependencies...
call npm install
echo ✅ Dependencies installed
echo.

REM Setup environment
if not exist .env.local (
    echo ⚙️  Setting up environment...
    copy .env.example .env.local
    echo ✅ Created .env.local (please edit if needed)
    echo.
)

REM Start application
echo 🎯 Starting RAG Chatbot...
echo.
echo 📍 Frontend: http://localhost:5173
echo 📍 Backend:  http://localhost:5000
echo.
echo Press Ctrl+C to stop
echo.

call npm run dev
