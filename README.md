# Scanner v2 — Enhanced NSE Swing Scanner

Weekly swing trading scanner for NSE equities with enhanced Cup & Handle detection, monthly TF support, and multi-target output.

---

## What's New in v2

| Feature | v1 | v2 |
|---|---|---|
| Neckline type | Horizontal only | **Diagonal + horizontal** |
| Cup length | Fixed 6mo / 15mo | **Sweep 2mo → 2yr daily, up to 2.5yr weekly** |
| Monthly TF | ❌ | ✅ |
| Status tiers | NEAR / BREAKOUT | **WATCH / NEAR / BREAKOUT** |
| Targets | 1 (full move) | **T1 (60%) + T2 (full move)** |
| Volume gating | Bonus only | **BREAKOUT requires volume confirmation** |
| Double Bottom | Narrow window | **Wide window, relaxed tolerance** |
| Descending Wedge | ❌ | ✅ |
| 2-close confirmation | ❌ | ✅ |

**Hit rate on 204-sample ground truth: 52% → 95%, 0 regressions**

---

## How to Run

### Full Weekly Scan (Recommended — every Saturday)

Double-click `run_weekly.bat` or from terminal:

```bat
cd C:\Users\91814\Desktop\claude\scanner-v2
run_weekly.bat
```

This runs automatically: **Scan → Charts → Telegram**
Expected time: **60–90 minutes**

---

### Manual Commands

**Quick test (50 stocks, ~2–3 min):**
```
python scanner.py --test
```

**Full scan, top 30:**
```
python scanner.py --top 30 --min-score 50 --workers 4
```

**Higher quality only (stricter filter):**
```
python scanner.py --top 30 --min-score 70 --workers 4
```

**Generate charts after scan:**
```
python gen_charts.py
```
> Edit the `STOCKS` list in `gen_charts.py` to generate for specific symbols only.

---

## Output

| Output | Location |
|---|---|
| Scan results (CSV) | `results/v2_YYYY-MM-DD.csv` |
| Daily charts | `results/charts/daily/SYMBOL.png` |
| Weekly charts | `results/charts/weekly/SYMBOL.png` |
| Monthly charts | `results/charts/monthly/SYMBOL.png` |

### CSV Columns

| Column | Description |
|---|---|
| `symbol` | NSE ticker |
| `pattern` | Detected pattern name |
| `status` | WATCH / NEAR / BREAKOUT |
| `cmp` | Current market price |
| `breakout` | Breakout level |
| `stop_loss` | Stop loss level |
| `target_1` | First target (~60% of measured move) |
| `target_2` | Full measured move target |
| `upside_%` | Upside to T1 from CMP |
| `risk_%` | Risk from CMP to SL |
| `rr` | Risk-reward ratio (T1 basis) |
| `volume` | Volume confirmation (True/False) |
| `neckline` | `flat` or `descending` |
| `score` | Composite score (higher = better) |

---

## Chart Legend

| Line | Colour | Meaning |
|---|---|---|
| Solid white | ⬜ | CMP — current price |
| Dashed blue | 🔵 | Breakout level |
| Dashed red | 🔴 | Stop Loss |
| Dashed green | 🟢 | T1 — first target |
| Dashed lime | 🟩 | T2 — full target |

Each stock gets **3 charts**: Daily (180 bars) · Weekly (104 bars) · Monthly (60 bars)
MAs shown: **20/50** on daily · **10/30** on weekly · **6/12** on monthly

---

## Status Tiers

| Status | Meaning | Action |
|---|---|---|
| **WATCH** | Price 10–25% below breakout | Add to watchlist, wait |
| **NEAR** | Price within 8% of breakout | Prepare entry |
| **BREAKOUT** | Price above breakout + volume + 2 closes confirmed | Entry signal |

---

## Project Structure

```
scanner-v2/
├── scanner.py                  ← Main scanner entry point
├── gen_charts.py               ← Chart generator (Daily/Weekly/Monthly)
├── telegram_notify.py          ← Telegram alerts
├── run_weekly.bat              ← One-click full run
├── patterns/
│   ├── cup_handle.py           ← Tuned C&H (diagonal neckline, sweep)
│   ├── cup_handle_monthly.py   ← Monthly TF cup detector
│   ├── double_bottom.py        ← Tuned double bottom
│   ├── wedge.py                ← Descending wedge detector
│   └── ...                     ← All original patterns
├── data/
│   ├── loader.py               ← NSE data fetcher (jugaad + yfinance)
│   └── nse_eq.py               ← NSE EQ universe
└── results/
    ├── v2_YYYY-MM-DD.csv
    └── charts/
        ├── daily/
        ├── weekly/
        └── monthly/
```

---

## GitHub

[github.com/karthik0419/scanner-v2](https://github.com/karthik0419/scanner-v2)
