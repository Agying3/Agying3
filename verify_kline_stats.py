#!/usr/bin/env python3
"""对 gen_kline_synth.py 生成的序列做 stylized-facts 体检。

对照的是学术界公认的"金融收益典型事实"（stylized facts）：
  F1 收益近似不相关      ACF(r) ~ 0
  F2 波动率聚集          ACF(|r|) > 0，缓慢衰减
  F3 厚尾                峰度 >> 3
  F4 轻度负偏            偏度略小于 0
  F5 近似随机游走        方差比 VR(q) ~ 1
  F6 量价正相关          corr(volume, |r|) > 0
  F7 OHLC 一致性         high >= max(o,c), low <= min(o,c)
"""
import math
from datetime import date

from gen_kline_synth import EPOCH, MAX_DAYS, SEED, gen_series


def acf(x, lag):
    n = len(x)
    m = sum(x) / n
    num = sum((x[i] - m) * (x[i - lag] - m) for i in range(lag, n))
    den = sum((v - m) ** 2 for v in x)
    return num / den if den else 0.0


def variance_ratio(rets, q):
    n = len(rets)
    m = sum(rets) / n
    v1 = sum((r - m) ** 2 for r in rets) / n
    if v1 == 0:
        return float("nan")
    qr = [sum(rets[i:i + q]) for i in range(n - q + 1)]
    mq = sum(qr) / len(qr)
    vq = sum((v - mq) ** 2 for v in qr) / len(qr)
    return vq / (q * v1)


def report(label, rows):
    c = [r["c"] for r in rows]
    rets = [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    n = len(rets)
    mean = sum(rets) / n
    sd = (sum((r - mean) ** 2 for r in rets) / n) ** 0.5
    skew = sum(((r - mean) / sd) ** 3 for r in rets) / n
    kurt = sum(((r - mean) / sd) ** 4 for r in rets) / n

    print(f"\n===== {label}  ({len(rows)} bars) =====")
    print(f"F1 ACF(ret)   lag1-5 : " + " ".join(f"{acf(rets, k):+.3f}" for k in range(1, 6)))
    absr = [abs(r) for r in rets]
    print(f"F2 ACF(|ret|) lag1-5 : " + " ".join(f"{acf(absr, k):+.3f}" for k in range(1, 6)))
    print(f"F3 kurtosis          : {kurt:.2f}      (real market 5~30, normal = 3)")
    print(f"F4 skewness          : {skew:+.2f}      (real market slightly < 0)")
    print(f"F5 var-ratio VR(2,5,10): "
          f"{variance_ratio(rets, 2):.2f} {variance_ratio(rets, 5):.2f} {variance_ratio(rets, 10):.2f}"
          f"   (random walk = 1.00)")

    bad = [r for r in rows if not (r["h"] >= max(r["o"], r["c"]) - 1e-9
                                   and r["l"] <= min(r["o"], r["c"]) + 1e-9)]
    print(f"F7 OHLC violations   : {len(bad)}   (must be 0)")

    vols = [r["v"] for r in rows[1:]]
    mv = sum(vols) / len(vols)
    ma = sum(absr) / len(absr)
    num = sum((vols[i] - mv) * (absr[i] - ma) for i in range(len(absr)))
    den = (sum((v - mv) ** 2 for v in vols) * sum((a - ma) ** 2 for a in absr)) ** 0.5
    print(f"F6 corr(vol,|ret|)   : {num/den:+.3f}  (real market > 0)")

    body = [abs(r["c"] - r["o"]) / r["o"] for r in rows]
    ush = [(r["h"] - max(r["o"], r["c"])) / r["o"] for r in rows]
    lsh = [(min(r["o"], r["c"]) - r["l"]) / r["o"] for r in rows]
    print(f"-- 实体/上影/下影 均值: {sum(body)/len(body)*100:.2f}% "
          f"{sum(ush)/len(ush)*100:.2f}% {sum(lsh)/len(lsh)*100:.2f}%")
    gaps = [(r["o"] - rows[i - 1]["c"]) / rows[i - 1]["c"] for i, r in enumerate(rows) if i]
    gm = sum(gaps) / len(gaps)
    gsd = (sum((g - gm) ** 2 for g in gaps) / len(gaps)) ** 0.5
    print(f"-- 隔夜跳空 均值/标准差: {gm*100:+.3f}% / {gsd*100:.3f}%")


def main():
    total = min(MAX_DAYS, (date.today() - EPOCH).days)
    series = gen_series(total, SEED)
    report("FULL SERIES (what the generator produces)", series)
    report("LAST 60 BARS (what the card actually shows)", series[-60:])


if __name__ == "__main__":
    main()
