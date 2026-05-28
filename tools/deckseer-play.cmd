@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0deckseer_play.ps1" %*
exit /b %ERRORLEVEL%
