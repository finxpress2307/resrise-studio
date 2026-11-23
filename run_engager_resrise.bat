@echo off
title Instagram Network Engager - @resrise (Studio Agency)
cd /d "%~dp0"
echo Running network engager for @resrise (Following accounts only)...
python scripts\ig_network_engager.py -a resrise
pause
