@echo off
REM TerraAgent Deployment Builder for Windows
REM This script creates a deployment package for TerraAgent

echo Building TerraAgent Deployment Package
echo ======================================

REM Create deployment directory
set DEPLOY_DIR=terraagent_deployment
if exist %DEPLOY_DIR% rmdir /s /q %DEPLOY_DIR%
mkdir %DEPLOY_DIR%

REM Copy necessary files
echo Copying application files...
xcopy /E /I templates %DEPLOY_DIR%\templates
xcopy /E /I static %DEPLOY_DIR%\static
xcopy /E /I utils %DEPLOY_DIR%\utils
xcopy /E /I chains %DEPLOY_DIR%\chains
xcopy *.py %DEPLOY_DIR%\
copy dependencies.md %DEPLOY_DIR%\
copy README.md %DEPLOY_DIR%\
copy start_application.sh %DEPLOY_DIR%\
copy start_application.bat %DEPLOY_DIR%\
copy create_desktop_shortcut.bat %DEPLOY_DIR%\
if exist .env.example copy .env.example %DEPLOY_DIR%\.env.example

REM Create .env template file
echo Creating .env template...
echo # TerraAgent Environment Variables> %DEPLOY_DIR%\.env
echo # Replace these values with your actual credentials>> %DEPLOY_DIR%\.env
echo.>> %DEPLOY_DIR%\.env
echo # Database configuration (PostgreSQL)>> %DEPLOY_DIR%\.env
echo DATABASE_URL=postgresql://user:password@localhost:5432/cama_data>> %DEPLOY_DIR%\.env
echo.>> %DEPLOY_DIR%\.env
echo # OpenAI API configuration>> %DEPLOY_DIR%\.env
echo OPENAI_API_KEY=your_api_key_here>> %DEPLOY_DIR%\.env
echo.>> %DEPLOY_DIR%\.env
echo # Session security>> %DEPLOY_DIR%\.env
echo SESSION_SECRET=your_secure_random_string_here>> %DEPLOY_DIR%\.env

REM Create brief instructions
echo Creating quick start guide...
echo # TerraAgent Quick Start Guide> %DEPLOY_DIR%\QUICK_START.md
echo.>> %DEPLOY_DIR%\QUICK_START.md
echo ## Windows Users>> %DEPLOY_DIR%\QUICK_START.md
echo Option 1 - Desktop Shortcut:>> %DEPLOY_DIR%\QUICK_START.md
echo 1. Double-click the `create_desktop_shortcut.bat` file>> %DEPLOY_DIR%\QUICK_START.md
echo 2. A shortcut will be created on your desktop>> %DEPLOY_DIR%\QUICK_START.md
echo 3. Double-click the desktop shortcut to start TerraAgent>> %DEPLOY_DIR%\QUICK_START.md
echo 4. Follow the on-screen instructions>> %DEPLOY_DIR%\QUICK_START.md
echo 5. Edit the .env file with your credentials when prompted>> %DEPLOY_DIR%\QUICK_START.md
echo.>> %DEPLOY_DIR%\QUICK_START.md
echo Option 2 - Direct Start:>> %DEPLOY_DIR%\QUICK_START.md
echo 1. Double-click the `start_application.bat` file>> %DEPLOY_DIR%\QUICK_START.md
echo 2. Follow the on-screen instructions>> %DEPLOY_DIR%\QUICK_START.md
echo 3. Edit the .env file with your credentials when prompted>> %DEPLOY_DIR%\QUICK_START.md
echo 4. The application will start automatically at http://localhost:5000>> %DEPLOY_DIR%\QUICK_START.md
echo.>> %DEPLOY_DIR%\QUICK_START.md
echo ## Linux/Mac Users>> %DEPLOY_DIR%\QUICK_START.md
echo 1. Open a terminal in this directory>> %DEPLOY_DIR%\QUICK_START.md
echo 2. Run `chmod +x start_application.sh`>> %DEPLOY_DIR%\QUICK_START.md
echo 3. Run `./start_application.sh`>> %DEPLOY_DIR%\QUICK_START.md
echo 4. Edit the .env file with your credentials when prompted>> %DEPLOY_DIR%\QUICK_START.md
echo 5. The application will start automatically at http://localhost:5000>> %DEPLOY_DIR%\QUICK_START.md
echo.>> %DEPLOY_DIR%\QUICK_START.md
echo ## Need Help?>> %DEPLOY_DIR%\QUICK_START.md
echo See the full README.md file for more detailed instructions and troubleshooting.>> %DEPLOY_DIR%\QUICK_START.md

REM Check if 7-Zip is available
where 7z >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Creating deployment archive with 7-Zip...
    7z a -tzip terraagent_deployment.zip %DEPLOY_DIR%
) else (
    echo 7-Zip not found. Please manually zip the %DEPLOY_DIR% folder.
    echo You can download 7-Zip from https://www.7-zip.org/
)

REM Cleanup
echo Cleaning up...
rmdir /s /q %DEPLOY_DIR%

echo Deployment package created: terraagent_deployment.zip
echo Share this file with users for easy installation.
pause