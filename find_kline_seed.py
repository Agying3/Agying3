#!/usr/bin/env python3
"""扫描种子，挑一条各项 stylized facts 都达标的合成序列。

固定种子意味着只有一条路径，各项统计好坏全看运气。
这个脚本按真实市场的参考区间给每条路径打分，挑惩罚最小的种子。
"""
import contextlib
import io
import math
from datetime import date

from gen_kline_synth import EPOCH, MAX_DAYS, gen_series
from verify_kline_stats import acf, variance_ratio

CANDIDATES = 240
SEED_BASE = 20260101


def score(rows):
    c = [r["c"] for r in rows]
    rets = [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    n = len(rets)
    mean = sum(rets) / n
    sd = (sum((x - mean) ** 2 for x in rets) / n) ** 0.5
    kurt = sum(((x - mean) / sd) ** 4 for x in rets) / n
    skew = sum(((x - mean) / sd) ** 3 for x in rets) / n
    a_abs = acf([abs(x) for x in rets], 1)
    vr5 = variance_ratio(rets, 5)
    swing = abs(rows[-1]["c"] / rows[0]["o"] - 1)

    pen = 0.0
    pen += max(0.0, 5.0 - kurt) * 1.0      # 厚尾不够
    pen += abs(skew) * 1.5                 # 偏度应贴近 0
    pen += max(0.0, 0.10 - a_abs) * 12.0   # 需要波动率聚集
    pen += abs(vr5 - 1.0) * 3.0            # 随机游走
    pen += max(0.0, swing - 0.8) * 6.0     # 别写成单边
    # 视觉层次：把窗口切成 6 段采样，要求涨段和跌段都存在，避免一条直线
    seg = [c[i] for i in range(0, len(c), max(1, len(c) // 6))]
    up = sum(1 for i in range(1, len(seg)) if seg[i] > seg[i - 1])
    dn = len(seg) - 1 - up
    pen += max(0, 2 - up) * 0.9 + max(0, 2 - dn) * 0.9
    # 影线要与实体同量级（影线太短的 K 线看着很假）
    body = sum(abs(r["c"] - r["o"]) / r["o"] for r in rows) / len(rows)
    shad = sum(((r["h"] - max(r["o"], r["c"])) + (min(r["o"], r["c"]) - r["l"])) / r["o"]
               for r in rows) / len(rows)
    pen += max(0.0, 0.7 - shad / body) * 0.6
    return pen, kurt, skew, a_abs, vr5, swing


def main():
    total = min(MAX_DAYS, (date.today() - EPOCH).days)
    rows = []
    for seed in range(SEED_BASE, SEED_BASE + CANDIDATES):
        with contextlib.redirect_stdout(io.StringIO()):
            s = gen_series(total, seed)
        pf = score(s)
        pw = score(s[-60:])
        rows.append((pf[0] + pw[0] * 1.5, seed, pf, pw))
    rows.sort(key=lambda r: r[0])

    print(f"scanned {CANDIDATES} seeds, total days = {total}\n")
    print(f"{'seed':>10} {'total':>7} {'full':>7} {'win60':>7}  | full: kurt/skew/|r|ac1/VR5/swing")
    for tot, seed, pf, pw in rows[:8]:
        print(f"{seed:>10} {tot:>7.3f} {pf[0]:>7.3f} {pw[0]:>7.3f}  | "
              f"{pf[1]:6.2f} {pf[2]:+5.2f} {pf[3]:+.3f} {pf[4]:5.2f} {pf[5]*100:+6.1f}%"
              f"  || win60 kurt {pw[1]:.2f} |r|ac1 {pw[3]:+.3f}")


if __name__ == "__main__":
    main()
