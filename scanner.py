"""
Weekly Swing Setup Scanner  v2  — Enhanced
Incorporates all tuned detectors from scanner-training analysis.

Changes vs v1:
  - Cup & Handle: diagonal neckline, variable cup-length sweep (60-240d), WATCH tier
  - Monthly TF cup detector added
  - Tuned Double Bottom (full measured-move, window sweep)
  - Descending Wedge detector
  - Two targets: target_1 (~60% move) and target_2 (full measured move)
  - Volume-gated BREAKOUT, 2-close confirmation

Usage:
  python scanner.py                  # full scan, top 30
  python scanner.py --top 50
  python scanner.py --min-score 50
  python scanner.py --test           # quick test on 50 stocks
"""

import os, sys, time, argparse, warnings
import pandas as pd
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.nse_eq import fetch_nse_eq_universe
from data.loader import _fetch_nse, _resample_weekly

# Tuned detectors (v2)
from patterns.cup_handle         import detect_cup_handle, detect_cup_handle_weekly
from patterns.cup_handle_monthly import detect_cup_handle_monthly, resample_monthly
from patterns.double_bottom      import detect_double_bottom
from patterns.wedge              import detect_descending_wedge
from patterns.breakout           import detect_breakout
from patterns.break_retest       import detect_break_retest
from patterns.channel            import detect_descending_channel, detect_ascending_channel
from patterns.triangle           import detect_triangle
from patterns.darvas_box         import detect_darvas_box
from patterns.flags              import detect_flag_pennant
from patterns.sr_levels          import detect_sr_levels
from patterns.retest             import detect_retest
from patterns.compression        import detect_compression

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

MIN_CANDLES = 140
MAX_WORKERS = 4


def _detect_pattern(df_daily, df_weekly):
    dfm = resample_monthly(df_daily)
    return (
        detect_cup_handle_monthly(dfm) or
        detect_cup_handle_weekly(df_weekly) or
        detect_cup_handle(df_daily) or
        detect_double_bottom(df_daily) or
        detect_descending_channel(df_daily) or
        detect_ascending_channel(df_daily) or
        detect_triangle(df_daily) or
        detect_darvas_box(df_daily) or
        detect_flag_pennant(df_daily) or
        detect_descending_wedge(df_daily) or
        detect_sr_levels(df_daily) or
        detect_break_retest(df_daily) or
        detect_retest(df_daily) or
        detect_compression(df_daily) or
        detect_breakout(df_daily)
    )


def _add_targets(result):
    breakout = result.get("breakout", 0)
    target2  = result.get("target", 0)
    if breakout > 0 and target2 > breakout:
        move = target2 - breakout
        result["target_1"] = round(breakout + move * 0.60, 2)
        result["target_2"] = round(target2, 2)
    else:
        result["target_1"] = result.get("target", 0)
        result["target_2"] = result.get("target", 0)
    return result


def _score(result):
    cmp      = result.get("cmp", 0)
    target   = result.get("target_1", result.get("target", 0))
    stop     = result.get("stop_loss", 0)
    breakout = result.get("breakout", 0)

    if cmp <= 0 or stop <= 0 or stop >= cmp:
        return 0, 0

    upside = (target - cmp) / cmp * 100
    risk   = (cmp - stop) / cmp * 100
    rr     = upside / risk if risk > 0 else 0

    score = 0
    if rr >= 3:   score += 40
    elif rr >= 2: score += 30
    elif rr >= 1: score += 15

    if result.get("volume"):                  score += 20
    status = result.get("status", "")
    if status == "BREAKOUT": score += 25
    elif status == "NEAR":   score += 12
    elif status == "WATCH":  score += 5

    dist = abs(cmp - breakout) / breakout if breakout else 1
    if dist < 0.02:   score += 20
    elif dist < 0.05: score += 12
    elif dist < 0.10: score += 6

    pat = result.get("pattern", "")
    pat_bonus = {
        "Cup & Handle (Monthly)":        30,
        "Cup & Handle (Weekly)":         25,
        "Cup & Handle":                  20,
        "Double Bottom":                 18,
        "Ascending Triangle":            15,
        "Symmetrical Triangle":          12,
        "Darvas Box":                    15,
        "Bullish Flag":                  12,
        "Descending Wedge":              14,
        "Break & Retest":                10,
        "S&R Breakout":                  10,
        "Channel Breakout (Descending)": 22,
        "Channel Breakout (Ascending)":  18,
        "Channel Breakout":              10,
    }
    score += pat_bonus.get(pat, 5)
    # Normalise to 0-100 (max theoretical ~155)
    normalised = round(min(score / 155 * 100, 100), 1)
    return normalised, round(rr, 2)


def _fetch_parallel(symbols, workers=MAX_WORKERS):
    print(f"  Pre-fetching price data ({workers} workers)...")
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_fetch_nse, s.replace(".NS",""), 730): s for s in symbols}
        done = 0
        for f in as_completed(futures, timeout=600):
            done += 1
            sym = futures[f]
            try:
                df = f.result(timeout=30)
                if df is not None and len(df) >= MIN_CANDLES:
                    results[sym] = df
            except Exception:
                pass
            if done % 100 == 0:
                print(f"    {done}/{len(symbols)} fetched...")
    print(f"  Ready: {len(results)} stocks")
    return results


def main():
    parser = argparse.ArgumentParser(description="Weekly Swing Scanner v2")
    parser.add_argument("--top",       type=int,   default=30)
    parser.add_argument("--min-score", type=float, default=50)
    parser.add_argument("--workers",   type=int,   default=MAX_WORKERS)
    parser.add_argument("--test",      action="store_true")
    args = parser.parse_args()

    print("=" * 65)
    print("  WEEKLY SWING SCANNER  v2  — ENHANCED")
    print(f"  Full NSE EQ Universe | {date.today()}")
    print("=" * 65)

    print("\n[1/4] Loading NSE EQ universe...")
    symbols = fetch_nse_eq_universe()
    if not symbols:
        print("  Failed. Exiting.")
        return
    if args.test:
        symbols = symbols[:50]
        print(f"  TEST MODE: {len(symbols)} stocks")
    else:
        print(f"  Universe: {len(symbols)} stocks")

    print(f"\n[2/4] Pre-fetching price data...")
    price_cache = _fetch_parallel(symbols, args.workers)

    print(f"\n[3/4] Scanning {len(price_cache)} stocks...\n")
    results = []
    for sym, df in price_cache.items():
        try:
            df_weekly = _resample_weekly(df)
            result = _detect_pattern(df, df_weekly)
            if not result:
                continue
            result = _add_targets(result)
            score, rr = _score(result)
            if rr <= 0 or score < args.min_score:
                continue

            cmp  = result.get("cmp", 0)
            t1   = result.get("target_1", 0)
            stop = result.get("stop_loss", 0)
            row = {
                "symbol":    sym,
                "pattern":   result.get("pattern"),
                "status":    result.get("status"),
                "cmp":       round(cmp, 2),
                "breakout":  round(result.get("breakout", 0), 2),
                "stop_loss": round(stop, 2),
                "target_1":  round(t1, 2),
                "target_2":  round(result.get("target_2", 0), 2),
                "upside_%":  round((t1 - cmp) / cmp * 100, 2) if cmp else 0,
                "risk_%":    round((cmp - stop) / cmp * 100, 2) if cmp else 0,
                "rr":        rr,
                "volume":    result.get("volume", False),
                "neckline":  result.get("neckline_kind", ""),
                "score":     score,
            }
            results.append(row)
            print(f"  {sym:<20} FOUND | {result.get('pattern')} | {result.get('status')} | score={score} | rr={rr}")
        except Exception:
            continue

    print(f"\n[4/4] Saving results...")
    if not results:
        print("  No setups found.")
        return

    df_out   = pd.DataFrame(results).sort_values("score", ascending=False).head(args.top)
    out_path = os.path.join(RESULTS_DIR, f"v2_{date.today()}.csv")
    df_out.to_csv(out_path, index=False)

    print(f"\n{'='*65}")
    print(f"  SCAN COMPLETE — {date.today()}")
    print(f"  Setups found : {len(results)}")
    print(f"  Top score    : {df_out['score'].iloc[0]} ({df_out['symbol'].iloc[0]})")
    print(f"{'='*65}")
    print(f"\n  TOP {len(df_out)} SETUPS")
    print(f"  {'Symbol':<20} {'Pattern':<28} {'Score':>5} {'RR':>5} {'T1%':>7} {'Status'}")
    print("  " + "-"*78)
    for _, row in df_out.iterrows():
        print(f"  {row['symbol']:<20} {row['pattern']:<28} {row['score']:>5} "
              f"{row['rr']:>5} {row['upside_%']:>6}%  {row['status']}")

    print(f"\n  Saved: {out_path}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
