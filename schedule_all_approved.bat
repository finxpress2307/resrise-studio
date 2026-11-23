@echo off
title Schedule All Approved Posts (Instagram Native Scheduler)
cd /d "%~dp0"
echo Scheduling all APPROVED posts from swarm_queue.json natively on Instagram...
python scripts\ig_publisher.py --account all --schedule
pause
