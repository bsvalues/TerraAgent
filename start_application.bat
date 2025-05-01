@echo off
REM TerraAgent - One-Click Deployment Script for Windows
REM This script sets up and runs the TerraAgent application

echo Starting TerraAgent - PACS Training Assistant...
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH. Please install Python 3.10 or later.
    pause
    exit /b 1
)

REM Check if virtual environment exists, if not create it
if not exist venv\ (
    echo Setting up virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install or update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists, if not create a template
if not exist .env (
    echo Creating .env file template...
    echo # TerraAgent Environment Variables> .env
    echo # Replace these values with your actual credentials>> .env
    echo.>> .env
    echo # Database configuration (PostgreSQL)>> .env
    echo DATABASE_URL=postgresql://user:password@localhost:5432/cama_data>> .env
    echo.>> .env
    echo # OpenAI API configuration>> .env
    echo OPENAI_API_KEY=your_api_key_here>> .env
    echo.>> .env
    echo # Session security>> .env
    echo SESSION_SECRET=your_secure_random_string_here>> .env
    
    echo .env template created. Please edit it with your actual values.
    echo Please edit the .env file with your credentials before continuing.
    notepad .env
    exit /b 1
)

REM Start the application
echo Starting TerraAgent application...
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

echo TerraAgent is running at http://localhost:5000
pause