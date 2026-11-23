@echo off
title Instagram Post Replier - ALL 5 ACCOUNTS (Vision AI + Zero Duplicates)
cd /d "%~dp0"

echo =======================================================
echo   STARTING POST COMMENT REPLIER ACROSS ALL 5 ACCOUNTS
echo   (Skips pinned posts; Zero-duplicate bulletproof replies)
echo =======================================================

echo.
echo [1/5] Running @avanyamehra...
python scripts\ig_replier.py -a avanyamehra

echo.
echo [2/5] Running @mairamehraofficial...
python scripts\ig_replier.py -a mairamehraofficial

echo.
echo [3/5] Running @iamgagankumar...
python scripts\ig_replier.py -a iamgagankumar

echo.
echo [4/5] Running @resrise...
python scripts\ig_replier.py -a resrise

echo.
echo [5/5] Running @gagankumarrocks...
python scripts\ig_replier.py -a gagankumarrocks

echo.
echo =======================================================
echo   ALL 5 ACCOUNTS SUCCESSFULLY PROCESSED!
echo =======================================================
pause
