@echo off
call "%~dp0build_tools\run_build.cmd" --mode release %*
exit /b %ERRORLEVEL%
