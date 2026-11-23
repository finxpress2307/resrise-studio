@echo off
title Instagram Post Replier - @resrise (Studio Agency)
cd /d "%~dp0"
echo Running comment replier for @resrise...
python scripts\ig_replier.py -a resrise
pause
