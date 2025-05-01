@echo off
REM TerraAgent Desktop Shortcut Creator
REM This script creates a desktop shortcut to launch TerraAgent

echo Creating TerraAgent Desktop Shortcut
echo ===================================

set CURRENT_DIR=%CD%
set DESKTOP_DIR=%USERPROFILE%\Desktop
set SHORTCUT_NAME=TerraAgent.lnk

REM Create the shortcut
echo Creating shortcut on desktop...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP_DIR%\%SHORTCUT_NAME%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CURRENT_DIR%\start_application.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Start TerraAgent PACS Training Assistant" >> CreateShortcut.vbs
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,41" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript /nologo CreateShortcut.vbs
del CreateShortcut.vbs

if exist "%DESKTOP_DIR%\%SHORTCUT_NAME%" (
    echo Desktop shortcut created successfully!
    echo You can now start TerraAgent by double-clicking the shortcut on your desktop.
) else (
    echo Failed to create desktop shortcut.
    echo Please run start_application.bat directly to launch TerraAgent.
)

pause