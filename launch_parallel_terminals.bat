@echo off
title RESRISE STUDIO - Multi-Terminal Automation Launcher (Feed: 10-12 | Stories: 10-12 | Sleep: 15-20m)
cd /d "%~dp0"

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" launch_parallel_terminals.py --accounts avanyamehra mairamehraofficial iamgagankumar resrise --task run_account --mode both --feed-min 10 --feed-max 12 --story-min 10 --story-max 12 --sleep-min 15 --sleep-max 20 %*

pause
