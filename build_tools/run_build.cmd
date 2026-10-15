@echo off
setlocal
pushd "%~dp0.."
if defined DK_PYTHON3 (
    "%DK_PYTHON3%" "%~dp0compiler.py" %*
) else (
    python "%~dp0compiler.py" %*
)
set "DK_BUILD_EXIT=%ERRORLEVEL%"
popd
exit /b %DK_BUILD_EXIT%
