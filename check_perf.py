import yfinance as yf

picks = [
    ('ACC.NS',        '18-May', 1362.8,  1353.58, 1326.5,  1480.14),
    ('ABDL.NS',       '18-May', 555.35,  600.0,   514.5,   914.7),
    ('KOTYARK.NS',    '22-May', 447.25,  454.0,   392.0,   683.8),
    ('PREMEXPLN.NS',  '22-May', 575.85,  583.25,  485.05,  874.1),
    ('KANSAINER.NS',  '22-May', 222.07,  224.45,  188.98,  321.78),
    ('MONARCH.NS',    '22-May', 315.15,  320.0,   284.79,  414.45),
    ('RUCHIRA.NS',    '22-May', 125.62,  127.99,  112.83,  167.72),
    ('IGL.NS',        '27-May', 166.01,  162.86,  157.98,  183.27),
    ('NBCC.NS',       '27-May', 95.55,   94.79,   91.95,   105.8),
    ('HIKAL.NS',      '27-May', 218.05,  220.37,  190.13,  335.12),
    ('GREAVESCOT.NS', '27-May', 181.51,  183.49,  154.42,  286.0),
    ('LLOYDSME.NS',   '27-May', 1853.7,  1868.0,  1603.38, 2659.3),
    ('ELECTCAST.NS',  '30-May', 77.13,   76.89,   74.58,   94.97),
    ('STARHEALTH.NS', '30-May', 527.95,  524.99,  509.24,  587.09),
    ('KCPSUGIND.NS',  '30-May', 22.92,   22.83,   22.14,   25.69),
    ('ACE.NS',        '04-Jun', 867.1,   863.74,  837.83,  958.72),
    ('21STCENMGM.NS', '04-Jun', 33.16,   32.95,   31.96,   40.32),
    ('ADFFOODS.NS',   '04-Jun', 290.3,   301.65,  252.35,  429.53),
    ('HEXT.NS',       '13-Jun', 498.65,  497.34,  482.42,  573.64),
    ('FIVESTAR.NS',   '13-Jun', 439.15,  435.79,  422.72,  488.81),
    ('SPLPETRO.NS',   '13-Jun', 702.1,   700.95,  679.92,  791.01),
    ('AFFLE.NS',      '13-Jun', 1446.3,  1444.96, 1401.61, 1627.04),
]

results = []
for sym, dt, cmp, bo, sl, tgt in picks:
    try:
        cur = round(float(yf.Ticker(sym).fast_info.last_price), 2)
    except Exception:
        cur = None

    if cur is None:
        st = 'N/A'
        pnl = '-'
    elif cur <= sl:
        st = 'SL HIT'
        pnl = str(round((cur - cmp) / cmp * 100, 1)) + '%'
    elif cur >= tgt:
        st = 'TARGET'
        pnl = '+' + str(round((cur - cmp) / cmp * 100, 1)) + '%'
    elif cur >= bo:
        st = 'ABOVE BO'
        pnl = '+' + str(round((cur - cmp) / cmp * 100, 1)) + '%'
    else:
        st = 'below bo'
        pnl = str(round((cur - cmp) / cmp * 100, 1)) + '%'

    results.append((sym.replace('.NS', ''), dt, cmp, bo, sl, tgt, cur, st, pnl))

header = '{:<14} {:<8} {:<11} {:<10} {:<8} {:<10} {:<10} {:<10} {}'.format(
    'Stock', 'Scan', 'EntryPrice', 'BreakOut', 'SL', 'Target', 'Current', 'Status', 'PnL%')
print(header)
print('-' * 95)
for r in results:
    sym, dt, cmp, bo, sl, tgt, cur, st, pnl = r
    flag = ' <<' if st in ('SL HIT', 'TARGET') else ''
    line = '{:<14} {:<8} {:<11} {:<10} {:<8} {:<10} {:<10} {:<10} {}{}'.format(
        sym, dt, cmp, bo, sl, tgt, str(cur), st, pnl, flag)
    print(line)

print()
print('=== SUMMARY ===')
total    = [r for r in results if r[7] != 'N/A']
tgt_hit  = [r for r in total if r[7] == 'TARGET']
above_bo = [r for r in total if r[7] == 'ABOVE BO']
below_bo = [r for r in total if r[7] == 'below bo']
sl_hit   = [r for r in total if r[7] == 'SL HIT']
print('Total picks : ' + str(len(total)))
print('TARGET hit  : ' + str(len(tgt_hit)))
print('ABOVE BO    : ' + str(len(above_bo)))
print('below bo    : ' + str(len(below_bo)))
print('SL HIT      : ' + str(len(sl_hit)))

if tgt_hit:
    print('\nTargets hit:')
    for r in tgt_hit:
        print('  ' + r[0] + ' (' + r[1] + ')  entry=' + str(r[2]) + '  cur=' + str(r[6]) + '  ' + r[8])

if above_bo:
    print('\nAbove BO (working):')
    for r in above_bo:
        print('  ' + r[0] + ' (' + r[1] + ')  entry=' + str(r[2]) + '  cur=' + str(r[6]) + '  ' + r[8])

if sl_hit:
    print('\nSL hits:')
    for r in sl_hit:
        print('  ' + r[0] + ' (' + r[1] + ')  entry=' + str(r[2]) + '  cur=' + str(r[6]) + '  ' + r[8])
