@echo off
title Instagram Network Engager - ALL 5 ACCOUNTS (Following Priority)
cd /d "%~dp0"

echo =======================================================
echo   STARTING NETWORK ENGAGER ACROSS ALL 5 ACCOUNTS
echo   (Engages followed creators only; 8-10s resting pacing)
echo =======================================================

echo.
echo [1/5] Running @avanyamehra...
python scripts\ig_network_engager.py -a avanyamehra

echo.
echo [2/5] Running @mairamehraofficial...
python scripts\ig_network_engager.py -a mairamehraofficial

echo.
echo [3/5] Running @iamgagankumar...
python scripts\ig_network_engager.py -a iamgagankumar

echo.
echo [4/5] Running @resrise...
python scripts\ig_network_engager.py -a resrise

echo.
echo [5/5] Running @gagankumarrocks...
python scripts\ig_network_engager.py -a gagankumarrocks

echo.
echo =======================================================
echo   ALL 5 ACCOUNTS SUCCESSFULLY PROCESSED!
echo =======================================================
pause
