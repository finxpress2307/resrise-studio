@echo off
title RESRISE STUDIO - Multi-Terminal Feed Browsing & Likes
cd /d "%~dp0"

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" launch_parallel_terminals.py --accounts avanyamehra mairamehraofficial iamgagankumar resrise --task browsing %*

pause
