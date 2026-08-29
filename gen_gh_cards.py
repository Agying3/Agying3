#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_gh_cards.py — 本地渲染 GitHub streak 卡 + activity graph 卡，
直接抓 https://github.com/users/Agying3/contributions 解析 367 个
<td data-date data-level>。

输出：
  streak.svg           vercel/demolab stat 文字卡片（495x220，墨绿流金）
  activity_graph.svg   仿 vercel.app activity-graph 风格（1000x200）

依赖：仅 Python 标准库。
"""

import re
import sys
import os
import urllib.request
from datetime import date

USER = "Agying3"
CONTRIB_URL = f"https://github.com/users/{USER}/contributions"

# 墨绿流金主题（demolab URL 参数：background=0d1117 stroke=2f8f5f ring=1f7a4d fire=d4a24e）
BG = "#0d1117"
GREEN = "#2f8f5f"
RING = "#1f7a4d"
GOLD = "#d4a24e"
TEXT = "#c9d1d9"
DIM = "#8b949e"
BORDER = "#30363d"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


# ---------- 抓取 + 解析 ----------
def fetch_html(url: str, retries: int = 3) -> str:
    last_err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            last_err = e
            sys.stderr.write(f"fetch attempt {i+1} failed: {e}\n")
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def parse_contrib(html: str):
    matches = re.findall(
        r'<td[^>]*data-date="([^"]+)"[^>]*data-level="([^"]+)"[^>]*>',
        html,
    )
    rows = []
    for d, lvl in matches:
        level = int(lvl)
        approx = {0: 0, 1: 2, 2: 5, 3: 8, 4: 12}.get(level, 0)
        rows.append((date.fromisoformat(d), level, approx))
    rows.sort()

    real_total = sum(r[2] for r in rows)
    m = re.search(r'<h2[^>]*id="js-contribution-activity-description"[^>]*>\s*'
                  r'(\d+)\s+contributions?', html)
    if m:
        try:
            real_total = int(m.group(1))
        except ValueError:
            pass
    return rows, real_total


def fmt_month_name(m: int) -> str:
    return ("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())[m - 1]


def compute_streaks(rows):
    total = sum(r[2] for r in rows)
    longest = cur = 0
    longest_end = cur_end = None
    for d, lvl, _ in rows:
        if lvl >= 1:
            cur += 1
            cur_end = d
            if cur > longest:
                longest = cur
                longest_end = d
        else:
            cur = 0
            cur_end = None
    cs = 0
    cs_end = None
    for d, lvl, _ in reversed(rows):
        if lvl >= 1:
            cs += 1
            cs_end = d
        else:
            break
    return total, cs, cs_end, longest, longest_end


# =================================================================
# 1) streak 卡（vercel/demolab stat 文字卡片，墨绿流金主题）
# =================================================================
def render_streak(rows, real_total: int) -> str:
    if not rows:
        return ""
    W, H = 495, 220
    _, cs, cs_end, longest, longest_end = compute_streaks(rows)
    total = real_total
    today = rows[-1][0]
    cs_since = cs_end.strftime("%b %d, %Y") if cs_end else "—"

    fire = chr(0x1F525)
    parts = []
    parts.append(
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" '
        f'fill="{BG}" rx="6" stroke="{GREEN}" stroke-width="1"/>'
    )
    cx = W // 2

    # Total Contributions
    parts.append(
        f'<text x="{cx}" y="28" text-anchor="middle" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="12" '
        f'fill="{TEXT}" letter-spacing="0.4">Total Contributions</text>'
    )
    parts.append(
        f'<text x="{cx}" y="62" text-anchor="middle" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="30" '
        f'font-weight="700" fill="{TEXT}">{total}</text>'
    )

    # Current Streak（金色 label + 🔥 + 数字 + 虚线圆环）
    parts.append(
        f'<text x="{cx}" y="92" text-anchor="middle" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="12" '
        f'font-weight="600" fill="{GOLD}" letter-spacing="0.4">Current Streak</text>'
    )
    fire_x = cx - 28
    num_cx = cx + 10
    parts.append(
        f'<circle cx="{num_cx}" cy="120" r="20" fill="none" '
        f'stroke="{RING}" stroke-width="1.5" stroke-dasharray="3 3"/>'
    )
    parts.append(
        f'<text x="{fire_x}" y="132" text-anchor="middle" '
        f'font-family="Segoe UI Emoji,Apple Color Emoji,Segoe UI,sans-serif" '
        f'font-size="28">{fire}</text>'
    )
    parts.append(
        f'<text x="{num_cx}" y="130" text-anchor="middle" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="30" '
        f'font-weight="700" fill="{TEXT}">{cs}</text>'
    )
    parts.append(
        f'<text x="{cx}" y="155" text-anchor="middle" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="10" '
        f'fill="{TEXT}">since {cs_since}</text>'
    )

    # Longest Streak
    parts.append(
        f'<text x="{cx}" y="180" text-anchor="middle" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="12" '
        f'fill="{TEXT}" letter-spacing="0.4">Longest Streak</text>'
    )
    parts.append(
        f'<text x="{cx}" y="205" text-anchor="middle" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="20" '
        f'font-weight="600" fill="{TEXT}">{longest} days</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n{"".join(parts)}\n</svg>\n'
    )


# =================================================================
# 2) activity graph 卡（仿 github-readme-activity-graph.vercel.app）
# =================================================================
def render_activity(rows, real_total: int) -> str:
    if not rows:
        return ""
    W, H = 1000, 200
    P = 50
    plot_w = W - 2 * P
    plot_h = H - 2 * P
    pl_x0 = P
    pl_y0 = P

    weekly = []
    cur_week = []
    seen_week_start = None
    for d, lvl, n in rows:
        if not cur_week:
            seen_week_start = d
        cur_week.append((d, n))
        wd = (d.weekday() + 1) % 7
        if wd == 6:
            weekly.append((seen_week_start, sum(x[1] for x in cur_week)))
            cur_week = []
    if cur_week:
        weekly.append((seen_week_start, sum(x[1] for x in cur_week)))
    if not weekly:
        return ""
    n_weeks = len(weekly)
    max_v = max((v for _, v in weekly), default=1) or 1
    pts = []
    for i, (d, v) in enumerate(weekly):
        x = pl_x0 + (i / max(1, n_weeks - 1)) * plot_w
        y = pl_y0 + plot_h - (v / max_v) * (plot_h - 18)
        pts.append((x, y, d, v))

    parts = []
    parts.append(
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}" rx="8"/>'
    )
    for i in range(1, 4):
        y = pl_y0 + i * plot_h / 4
        parts.append(
            f'<line x1="{pl_x0}" y1="{y}" x2="{pl_x0+plot_w}" y2="{y}" '
            f'stroke="{BORDER}" stroke-opacity="0.4" stroke-width="1"/>'
        )
    last_m = -1
    for x, y, d, v in pts:
        if d.month != last_m:
            last_m = d.month
            parts.append(
                f'<text x="{x:.2f}" y="{pl_y0+plot_h+18}" '
                f'font-family="Segoe UI,Arial,sans-serif" font-size="11" '
                f'fill="{DIM}">{fmt_month_name(d.month)}</text>'
            )

    def smooth_path(points):
        if len(points) < 2:
            return ""
        d = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
        for i in range(1, len(points)):
            x0, y0 = points[i - 1]
            x1, y1 = points[i]
            cx1 = x0 + (x1 - x0) * 0.4
            cx2 = x1 - (x1 - x0) * 0.4
            d.append(
                f"C {cx1:.2f} {y0:.2f}, {cx2:.2f} {y1:.2f}, {x1:.2f} {y1:.2f}"
            )
        return " ".join(d)

    line_d = smooth_path([(p[0], p[1]) for p in pts])
    area_d = (
        line_d
        + f" L {pts[-1][0]:.2f} {pl_y0+plot_h:.2f}"
        + f" L {pts[0][0]:.2f} {pl_y0+plot_h:.2f} Z"
    )
    parts.append(f'<path d="{area_d}" fill="{GOLD}" fill-opacity="0.18"/>')
    parts.append(
        f'<path d="{line_d}" fill="none" stroke="{GOLD}" '
        f'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    parts.append(
        f'<circle cx="{pts[0][0]:.2f}" cy="{pts[0][1]:.2f}" r="3.5" fill="{GOLD}"/>'
    )
    parts.append(
        f'<circle cx="{pts[-1][0]:.2f}" cy="{pts[-1][1]:.2f}" r="3.5" fill="{GOLD}"/>'
    )
    total = real_total
    parts.append(
        f'<text x="{W-P}" y="{pl_y0-12}" text-anchor="end" '
        f'font-family="Segoe UI,Arial,sans-serif" font-size="12" '
        f'font-weight="600" fill="{TEXT}">Weekly contributions · '
        f'<tspan fill="{GOLD}">{total}</tspan> total</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n{"".join(parts)}\n</svg>\n'
    )


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"[1/2] fetch contributions from {CONTRIB_URL} ...")
    html = fetch_html(CONTRIB_URL)
    rows, real_total = parse_contrib(html)
    if not rows:
        print("NO DATA — abort", file=sys.stderr)
        sys.exit(1)
    print(f"[1/2] parsed {len(rows)} rows, "
          f"{rows[0][0]} → {rows[-1][0]}, real_total={real_total}")
    streak_svg = render_streak(rows, real_total)
    activity_svg = render_activity(rows, real_total)
    assets_dir = os.path.join(out_dir, "assets")
    if not os.path.isdir(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
    for svg, fn in [
        (streak_svg, "streak.svg"),
        (activity_svg, "activity_graph.svg"),
    ]:
        with open(os.path.join(assets_dir, fn), "w", encoding="utf-8") as f:
            f.write(svg)
    print(f"[2/2] wrote assets/streak.svg + assets/activity_graph.svg")


if __name__ == "__main__":
    main()
