@echo off
title Resrise Swarm Approval Dashboard (Port 8500)
cd /d "%~dp0"
echo Starting Resrise Swarm Approval Dashboard at http://localhost:8500 ...
python scripts\approval_dashboard.py
pause
