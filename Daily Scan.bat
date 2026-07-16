@echo off
title TableFlow Daily Scan
cd /d "%~dp0"
echo.
echo  Running Daily Morning Scan...
echo  This checks sector heat + backbone 50 + hot sector stocks
echo.
python daily_scan.py --top 15
echo.
pause
