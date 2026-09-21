#!/usr/bin/env python3
"""合成 K 线生成器 —— 数据是随机生成的，但"变化规律"按真实市场的统计特征复刻。

复刻的真实特征：
  1. 收益率近似正态 + 厚尾           (不是 uniform 均匀分布)
  2. 波动率聚集 GARCH(1,1)           (大波动后面跟着大波动)
  3. 几何随机游走，长期无漂移          (不再单边上涨)
  4. 日内用布朗桥求 high/low          (影线长度天然合理，且保证 h>=max(o,c)，l<=min(o,c))
  5. 成交量与波动正相关 + 对数正态右偏
  6. 只走交易日（自动跳过周末）
  7. 固定种子 + 序列长度随日期增长      (历史稳定，每天向前推进一根)

用法:
    python gen_kline_synth.py                # 默认 60 根
    python gen_kline_synth.py AGY/USD 90
"""
import math
import os
import random
import sys
from datetime import date, timedelta

TICKER = sys.argv[1] if len(sys.argv) > 1 else "AGY/USD"
BARS = int(sys.argv[2]) if len(sys.argv) > 2 else 60
OUT = os.path.dirname(os.path.abspath(__file__))

SEED = 20260197                # 由 find_kline_seed.py 按 stylized-facts 打分挑出的种子
EPOCH = date(2025, 1, 1)
MAX_DAYS = 3000               # 必须大于 (今天-EPOCH) 的天数；否则长度被封顶，K 线就永远不动了
P0 = 100.0
ALPHA, BETA = 0.08, 0.90
SIGMA2_LONG = 0.0004          # 长期日方差 -> 日波动约 2%
INTRADAY_STEPS = 64
GAP_SIGMA = 0.0025            # 隔夜跳空标准差（约 0.25%）

THEMES = {
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "grid": "#1f242c",
        "text": "#e6edf3", "dim": "#8b949e",
        "up": "#f85149", "up_fill": "#f8514955",
        "dn": "#3fb950", "dn_fill": "#3fb95055",
        "ma": "#d29922",
    },
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "grid": "#e7ebef",
        "text": "#1f2328", "dim": "#656d76",
        "up": "#cf222e", "up_fill": "#cf222e44",
        "dn": "#1a7f37", "dn_fill": "#1a7f3744",
        "ma": "#9a6700",
    },
}


def trading_days(end, count):
    days, d = [], end
    while len(days) < count:
        if d.weekday() < 5:
            days.append(d)
        d -= timedelta(days=1)
    return list(reversed(days))


def _student_t(rng, df):
    """标准化的 Student-t 抽样（方差归一），用来复刻真实收益的厚尾。"""
    z = rng.gauss(0.0, 1.0)
    v = sum(rng.gauss(0.0, 1.0) ** 2 for _ in range(df))
    return z / math.sqrt(v / df) / math.sqrt(df / (df - 2.0))


def gen_series(n_days, seed):
    """GARCH(1,1) 波动率 + 日内布朗桥，返回 OHLCV 序列。"""
    rng = random.Random(seed)
    omega = SIGMA2_LONG * (1 - ALPHA - BETA)
    s2 = SIGMA2_LONG
    price = P0
    out = []
    mu = 0.0
    for _ in range(n_days):
        # AR(1) 随机漂移：趋势段自然出现（半衰期约 23 天），长期均值为 0，
        # 不会像固定漂移段那样一路累积成单边直线。
        mu = 0.97 * mu + rng.gauss(0.0, 0.0008)
        z = _student_t(rng, 5)
        r = mu + math.sqrt(s2) * z                          # 当日对数收益
        o = price * math.exp(_student_t(rng, 6) * GAP_SIGMA)   # 隔夜跳空
        c = o * math.exp(r)

        # 日内路径：布朗桥，端点固定为 0 与 log(c/o)
        step_sigma = math.sqrt(s2 / INTRADAY_STEPS)
        w = [0.0]
        for _k in range(INTRADAY_STEPS):
            w.append(w[-1] + rng.gauss(0.0, step_sigma))
        tgt = math.log(c / o)
        m = INTRADAY_STEPS
        path = [w[k] - (k / m) * w[m] + (k / m) * tgt for k in range(m + 1)]

        hi = o * math.exp(max(path))
        lo = o * math.exp(min(path))
        hi = max(hi, o, c)
        lo = min(lo, o, c)

        # 成交量：与当日波动正相关，对数正态右偏
        vol = math.exp(0.7 * min(abs(r) / math.sqrt(SIGMA2_LONG), 3.0)
                       + rng.gauss(0.0, 0.35)) * 1000.0
        out.append({"o": o, "h": hi, "l": lo, "c": c, "v": vol})
        price = c
        s2 = omega + ALPHA * r * r + BETA * s2

    # ---- 真实性体检 ----
    rets = [math.log(out[i]["c"] / out[i - 1]["c"]) for i in range(1, len(out))]
    mean = sum(rets) / len(rets)
    sd = (sum((x - mean) ** 2 for x in rets) / len(rets)) ** 0.5
    m4 = sum(((x - mean) / sd) ** 4 for x in rets) / len(rets)
    ac1 = 0.0
    if len(rets) > 2:
        num = sum((rets[i] - mean) * (rets[i - 1] - mean) for i in range(1, len(rets)))
        den = sum((x - mean) ** 2 for x in rets)
        ac1 = num / den if den else 0.0
    lo_p = min(x["l"] for x in out)
    hi_p = max(x["h"] for x in out)
    absr = [abs(x) for x in rets]
    ma_abs = sum(absr) / len(absr)
    ac1_abs = 0.0
    if len(absr) > 2:
        num = sum((absr[i] - ma_abs) * (absr[i - 1] - ma_abs) for i in range(1, len(absr)))
        den = sum((x - ma_abs) ** 2 for x in absr)
        ac1_abs = num / den if den else 0.0
    print(f"[check] n={len(out)}  ret.mean={mean*100:+.3f}%  ret.sd={sd*100:.2f}%  "
          f"kurt={m4:.2f}  ac1={ac1:+.3f}  |r|ac1={ac1_abs:+.3f}")
    print(f"[check] price {lo_p:.2f} ~ {hi_p:.2f}  "
          f"(start {P0:.0f}, end-vs-start {(out[-1]['c']/out[0]['o']-1)*100:+.1f}%)")
    return out


def sma(vals, n):
    return [None if i + 1 < n else sum(vals[i + 1 - n:i + 1]) / n for i in range(len(vals))]


def fmt_price(p):
    if p >= 10000:
        return f"{p:,.0f}"
    if p >= 100:
        return f"{p:,.1f}"
    return f"{p:,.2f}"


def render(rows, days, theme_name):
    T = THEMES[theme_name]
    W, H = 1000, 340
    pl, pr = 22, 74
    price_top, price_bot = 78, 232
    vol_top, vol_bot = 250, 312
    plot_w = W - pl - pr
    n = len(rows)
    pitch = plot_w / n
    cw = max(2.0, min(9.0, pitch * 0.62))

    hi = max(r["h"] for r in rows)
    lo = min(r["l"] for r in rows)
    pad = (hi - lo) * 0.06
    hi, lo = hi + pad, lo - pad
    span = hi - lo
    vs = sorted(r["v"] for r in rows)
    vmax = vs[min(len(vs) - 1, int(len(vs) * 0.95))] or 1.0

    def py(p):
        return price_bot - (p - lo) / span * (price_bot - price_top)

    ma20 = sma([r["c"] for r in rows], 20)
    last, prev = rows[-1]["c"], rows[-2]["c"]
    chg = (last - prev) / prev * 100
    up_day = last >= prev
    chg_col = T["up"] if up_day else T["dn"]

    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" '
             f'fill="{T["bg"]}" stroke="{T["border"]}" stroke-width="1"/>')
    s.append(f'<text x="{pl}" y="30" font-family="ui-sans-serif,Segoe UI,sans-serif" '
             f'font-size="15" font-weight="600" fill="{T["text"]}">{TICKER}</text>')
    s.append(f'<text x="{pl}" y="48" font-family="ui-sans-serif,Segoe UI,sans-serif" '
             f'font-size="11" fill="{T["dim"]}">1D · {n} bars · MA20</text>')
    s.append(f'<text x="{W-pr}" y="30" text-anchor="end" '
             f'font-family="ui-monospace,Consolas,monospace" font-size="17" '
             f'font-weight="600" fill="{T["text"]}">{fmt_price(last)}</text>')
    arrow = "\u25b2" if up_day else "\u25bc"
    s.append(f'<text x="{W-pr}" y="48" text-anchor="end" '
             f'font-family="ui-monospace,Consolas,monospace" font-size="11" '
             f'fill="{chg_col}">{arrow} {chg:+.2f}%</text>')

    for i in range(5):
        p = lo + span * i / 4
        y = py(p)
        s.append(f'<line x1="{pl}" y1="{y:.2f}" x2="{W-pr}" y2="{y:.2f}" '
                 f'stroke="{T["grid"]}" stroke-width="0.5"/>')
        s.append(f'<text x="{W-pr+8}" y="{y+3.5:.2f}" '
                 f'font-family="ui-monospace,Consolas,monospace" font-size="10" '
                 f'fill="{T["dim"]}">{fmt_price(p)}</text>')

    for i, r in enumerate(rows):
        cx = pl + pitch * (i + 0.5)
        up = r["c"] >= r["o"]
        col = T["up"] if up else T["dn"]
        fill = T["up_fill"] if up else T["dn_fill"]
        s.append(f'<line x1="{cx:.2f}" y1="{py(r["h"]):.2f}" x2="{cx:.2f}" '
                 f'y2="{py(r["l"]):.2f}" stroke="{col}" stroke-width="1"/>')
        y1, y2 = py(max(r["o"], r["c"])), py(min(r["o"], r["c"]))
        s.append(f'<rect x="{cx-cw/2:.2f}" y="{y1:.2f}" width="{cw:.2f}" '
                 f'height="{max(1.0, y2-y1):.2f}" fill="{fill}" stroke="{col}" stroke-width="1"/>')
        vh = min(1.0, r["v"] / vmax) * (vol_bot - vol_top)
        s.append(f'<rect x="{cx-cw/2:.2f}" y="{vol_bot-vh:.2f}" width="{cw:.2f}" '
                 f'height="{vh:.2f}" fill="{col}" opacity="0.35"/>')

    pts = [f"{pl + pitch*(i+0.5):.2f},{py(m):.2f}" for i, m in enumerate(ma20) if m is not None]
    s.append(f'<polyline points="{" ".join(pts)}" fill="none" '
             f'stroke="{T["ma"]}" stroke-width="1.5" stroke-linejoin="round"/>')

    for frac in (0.0, 0.5, 1.0):
        i = min(n - 1, int(frac * (n - 1)))
        x = pl + pitch * (i + 0.5)
        anchor = "start" if frac == 0 else ("end" if frac == 1 else "middle")
        s.append(f'<text x="{x:.2f}" y="{H-10}" text-anchor="{anchor}" '
                 f'font-family="ui-monospace,Consolas,monospace" font-size="10" '
                 f'fill="{T["dim"]}">{days[i].isoformat()}</text>')

    s.append('</svg>')
    return "\n".join(s)


def main():
    today = date.today()
    total = min(MAX_DAYS, (today - EPOCH).days)
    series = gen_series(total, SEED)
    days = trading_days(today, len(series))
    rows, days = series[-BARS:], days[-BARS:]
    for name in THEMES:
        path = os.path.join(OUT, f"kline_synth_{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(rows, days, name))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
