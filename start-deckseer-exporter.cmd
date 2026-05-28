@echo off
setlocal
title Deckseer Exporter Alerts
cd /d "%~dp0"
call "%~dp0tools\deckseer-play.cmd" %*
set "DECKSEER_EXIT=%ERRORLEVEL%"
if not "%DECKSEER_EXIT%"=="0" (
    echo.
    echo Deckseer exporter alert helper exited with code %DECKSEER_EXIT%.
    echo Press any key to close this window.
    pause >nul
)
exit /b %DECKSEER_EXIT%
