@echo off
cd /d "%~dp0"
echo =======================================================
echo  WEEKLY SWING SCANNER  v2  — ENHANCED
echo  Full NSE EQ Universe (~2000+ stocks)
echo  %date%  %time%
echo =======================================================
echo.
echo  New in v2:
echo    - Diagonal neckline cup detection
echo    - Monthly TF cups (multi-year bases)
echo    - WATCH / NEAR / BREAKOUT tiers
echo    - T1 (60%%) + T2 (full) targets
echo    - Volume-gated breakouts
echo.
echo  Run every Saturday. Expected time: 60-90 min.
echo.

echo [1/3] Running full scan...
python scanner.py --top 50 --min-score 50 --workers 8
if errorlevel 1 (
    echo ERROR: scanner.py failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Generating charts (Daily + Weekly + Monthly)...
for /f "tokens=*" %%f in ('python -c "import glob; files=sorted(glob.glob('results/v2_*.csv'),reverse=True); print(files[0] if files else '')"') do set CHART_CSV=%%f
python -X utf8 -c "
import csv, sys, os
sys.path.insert(0,'.')
import gen_charts
rows = list(csv.DictReader(open(r'%CHART_CSV%', encoding='utf-8')))
gen_charts.STOCKS = [r['symbol'].replace('.NS','') for r in rows if r.get('symbol')]
print(f'Generating charts for {len(gen_charts.STOCKS)} stocks')
for s in gen_charts.STOCKS:
    gen_charts.plot(s)
print('Charts done.')
"
if errorlevel 1 (
    echo WARNING: Chart generation failed. Scan results still saved.
)

echo.
echo [3/3] Sending Telegram notification...
python telegram_notify.py --top 15
if errorlevel 1 (
    echo WARNING: Telegram notification failed. Results still saved.
)

echo.
echo =======================================================
echo  Done at %date% %time%
echo  Results : results\v2_%date:~-4,4%-%date:~-7,2%-%date:~-10,2%.csv
echo  Charts  : results\charts\daily\   weekly\   monthly\
echo =======================================================
echo.
pause
