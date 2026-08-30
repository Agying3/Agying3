#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_wakatime_cards.py —— WakaTime Profile 卡片预览设计稿（三张，全本地 SVG，零外链）

卡1 wakatime_langs.svg    语言时间方形环（环 + 色点图例 + 中心周总时长）
卡2 wakatime_daily.svg    每日编码时长条形（今日金色高亮 + 均值虚线）
卡3 wakatime_day.svg      一天 24h 编码时间线（项目色块 + 最长 session 标注）

数据：WakaTime REST API（stats 语言占比 + durations 逐日/时段）。key 从 ~/.wakatime.cfg。
口径：总时长/每日/时段均用 durations 合计；语言占比用 stats。
"""
import os
import json
import base64
import time
import urllib.request
import datetime

W, = (1000,)
BG, BORDER, TRACK = "#0d1117", "#21262d", "#161b22"
TXT, MUTED, FAINT = "#c9d1d9", "#8b949e", "#30363d"
GREEN, GOLD = "#2f8f5f", "#d4a24e"
FONT = "Segoe UI, Helvetica, Arial, sans-serif"

LANG_COLORS = {
    "Python": "#4d8fd6", "Other": "#6e7681", "Markdown": "#7d96cc",
    "PowerShell": "#3a76c4", "HTML": "#e34c26", "CSV": "#98a3b0",
    "Rust": "#dea584", "Java": "#d19a66", "Go": "#3fb6d8",
    "JavaScript": "#f1e05a", "TypeScript": "#7cb2f0", "CSS": "#a48bd4",
    "Shell": "#89e051", "JSON": "#9aa4b2", "YAML": "#e06c75", "TOML": "#d78860",
}
PROJ_COLORS = {"1qbot": "#2f8f5f", "workkrow": "#d4a24e", "API_GUI": "#4d8fd6", "DMShoot": "#e0716b"}


def get_key():
    k = os.environ.get("WAKATIME_API_KEY")
    if k:
        return k
    for p in [os.path.expanduser("~/.wakatime.cfg"), r"C:/Users/Administrator/.wakatime.cfg"]:
        if os.path.exists(p):
            for line in open(p, encoding="utf-8", errors="ignore"):
                s = line.strip()
                if s.startswith("api_key"):
                    return s.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def api(path, key, retries=3):
    """带重试的 WakaTime 请求。本地代理(127.0.0.1:18081)经常 502，瞬时 SSL 超时可自动恢复。"""
    hdr = {"Authorization": "Basic " + base64.b64encode(key.encode()).decode()}
    url = "https://wakatime.com/api/v1" + path
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=hdr)
            return json.load(urllib.request.urlopen(req, timeout=20))
        except Exception as e:      # URLError / TimeoutError / HTTPError / JSON 解析失败
            last = e
            if i < retries - 1:
                time.sleep(3 + i * 3)
    raise last


def fmt_hm(seconds):
    h, m = int(seconds // 3600), int(seconds % 3600 // 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"


def fmt_h(seconds):
    return f"{seconds / 3600:.1f}h" if seconds >= 3600 else f"{int(seconds // 60)}m"


def svg_open(w, h, title, desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" font-family="{FONT}">\n'
            f'<title>{title}</title>\n<desc>{desc}</desc>\n'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" '
            f'fill="{BG}" stroke="{BORDER}"/>\n')


def header(title, right, right_fill=MUTED, right_size=13):
    s = (f'<text x="40" y="54" font-size="15" letter-spacing="3" fill="{MUTED}">{title}</text>\n')
    if right:
        s += (f'<text x="{W - 40}" y="54" font-size="{right_size}" fill="{right_fill}" '
              f'text-anchor="end" font-weight="500">{right}</text>\n')
    return s


def watermark(h):
    return f'<text x="{W - 40}" y="{h - 24}" font-size="12" fill="{FAINT}" text-anchor="end">wakatime</text>\n'


def point_at(d, m):
    d %= 4 * m
    k = int(d // m)
    l = d - k * m
    if k == 0:
        return (l, 0)
    if k == 1:
        return (m, l)
    if k == 2:
        return (m - l, m)
    return (0, m - l)


def seg_path(d0, d1, m):
    pts = [point_at(d0, m)]
    for c in (m, 2 * m, 3 * m, 4 * m):
        if d0 < c < d1:
            pts.append(point_at(c, m))
    pts.append(point_at(d1, m))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def render_langs(langs, total_secs, out):
    h = 360
    m, th = 186, 22
    x0, y0 = 97, 117          # ring local origin; ring center = (x0+93, y0+93) = (190, 210)
    per = 4 * m
    s = svg_open(W, h, "WakaTime 语言时间方形环卡片", "方形环按占比展示语言时间分布，中心为本周总时长")
    s += header("CODING TIME · LANGUAGES", "last 7 days")
    s += f'<g transform="translate({x0},{y0})">\n'
    s += f'<rect x="0" y="0" width="{m}" height="{m}" fill="none" stroke="{TRACK}" stroke-width="{th}"/>\n'
    dist = 0.0
    for name, pct, color in langs:
        d1 = dist + pct / 100.0 * per
        s += (f'<path d="{seg_path(dist, min(d1, per), m)}" stroke="{color}" '
              f'stroke-width="{th}" fill="none"/>\n')
        dist = d1
    s += "</g>\n"
    s += (f'<text x="190" y="206" font-size="30" font-weight="500" fill="{TXT}" '
          f'text-anchor="middle">{fmt_hm(total_secs)}</text>\n')
    s += f'<text x="190" y="236" font-size="14" fill="{MUTED}" text-anchor="middle">this week</text>\n'
    cols = [430, 700]
    for i, (name, pct, color) in enumerate(langs):
        col, row = i % 2, i // 2
        x, y = cols[col], 150 + row * 60
        hrs = pct / 100.0 * total_secs
        s += f'<circle cx="{x}" cy="{y - 6}" r="7" fill="{color}"/>\n'
        s += f'<text x="{x + 22}" y="{y}" font-size="18" fill="{TXT}">{name}</text>\n'
        s += (f'<text x="{cols[col] + 230}" y="{y}" font-size="15" fill="{MUTED}" '
              f'text-anchor="end">{fmt_h(hrs)} · {pct:.1f}%</text>\n')
    s += watermark(h)
    s += "</svg>\n"
    open(out, "w", encoding="utf-8").write(s)


def render_daily(daily, total_secs, out):
    h = 300
    x_l, x_r, base, top = 70, 930, 240, 100
    mx = max(v for _, _, v in daily) or 1.0
    scale = (base - top - 10) / mx
    pitch = (x_r - x_l) / len(daily)
    bw = 56
    avg = total_secs / 7 / 3600
    s = svg_open(W, h, "WakaTime 每日编码时长条形卡片", "最近 7 天每天编码小时数，今日金色高亮，虚线为日均值")
    s += header("CODING TIME · DAILY", fmt_hm(total_secs), GOLD, 22)
    s += f'<text x="{W - 40}" y="76" font-size="13" fill="{MUTED}" text-anchor="end">this week</text>\n'
    s += f'<line x1="{x_l}" y1="{base}" x2="{x_r}" y2="{base}" stroke="{BORDER}"/>\n'
    for i, (day, is_today, hrs) in enumerate(daily):
        cx = x_l + pitch * (i + 0.5)
        bh = max(hrs * scale, 3)
        color = GOLD if is_today else GREEN
        s += f'<rect x="{cx - bw / 2:.1f}" y="{base - bh:.1f}" width="{bw}" height="{bh:.1f}" rx="4" fill="{color}"/>\n'
        lab_fill = GOLD if is_today else (TXT if hrs == mx else MUTED)
        s += (f'<text x="{cx:.1f}" y="{base - bh - 12:.1f}" font-size="14" fill="{lab_fill}" '
              f'text-anchor="middle">{hrs:.1f}h</text>\n')
        s += (f'<text x="{cx:.1f}" y="{base + 28}" font-size="15" fill="{lab_fill}" '
              f'text-anchor="middle">{day}</text>\n')
    ay = base - avg * scale
    s += f'<line x1="{x_l}" y1="{ay:.1f}" x2="{x_r}" y2="{ay:.1f}" stroke="{FAINT}" stroke-dasharray="5 5"/>\n'
    s += (f'<text x="{x_r - 4}" y="{ay - 8:.1f}" font-size="13" fill="{MUTED}" '
          f'text-anchor="end">avg {avg:.1f}h/day</text>\n')
    s += watermark(h)
    s += "</svg>\n"
    open(out, "w", encoding="utf-8").write(s)


def render_timeline(day_label, blocks, total_secs, out):
    h = 118
    x_l, x_r = 70, 930
    ty, th = 46, 20               # 上 band：24h 轨道
    pxm = (x_r - x_l) / 1440.0
    # 合并：同项目且间隔 <=8min
    merged = []
    for st, dur, proj in blocks:
        if merged and proj == merged[-1][2] and st - (merged[-1][0] + merged[-1][1]) <= 8 * 60:
            merged[-1][1] = st + dur - merged[-1][0]
        else:
            merged.append([st, dur, proj])
    longest = max(merged, key=lambda b: b[1])
    projects = sorted({p for _, _, p in merged})
    colors = {}
    order = []
    fallback = ["#6e7681", "#9aa4b2"]
    extra = 0
    for _, _, p in merged:
        if p not in colors:
            if p in PROJ_COLORS:
                colors[p] = PROJ_COLORS[p]
            else:
                colors[p] = fallback[extra % len(fallback)]
                extra += 1
            if p not in order:
                order.append(p)
    s = svg_open(W, h, "WakaTime 一天编码时间线卡片", "扁卡：上 band 24h 轨道 + 下 band 图例，共享时间栅格")
    # 顶部标题：左=日期，右=总时长 + session 数（合并到一行，省一行高度）
    s += (f'<text x="40" y="30" font-size="14" letter-spacing="3" fill="{MUTED}">'
          f'ONE DAY · {day_label}</text>\n')
    s += (f'<text x="960" y="30" font-size="16" fill="{GOLD}" text-anchor="end" font-weight="500">'
          f'{fmt_hm(total_secs)} coded · {len(merged)} sessions</text>\n')
    # 共享 24h 栅格（贯穿 track + 标签区，动态统一）
    grid_top, grid_bot = 40, 84
    for hr in (0, 6, 12, 18, 24):
        x = x_l + hr * 60 * pxm
        s += f'<line x1="{x:.1f}" y1="{grid_top}" x2="{x:.1f}" y2="{grid_bot}" stroke="#1b222b"/>\n'
    for hr in range(3, 24, 3):
        x = x_l + hr * 60 * pxm
        s += f'<line x1="{x:.1f}" y1="{grid_top}" x2="{x:.1f}" y2="{grid_bot}" stroke="#161b22"/>\n'
    # 上 band：轨道 + 昼夜暗带
    s += f'<rect x="{x_l}" y="{ty}" width="{x_r - x_l}" height="{th}" rx="6" fill="{TRACK}"/>\n'
    for a, b in ((0, 6), (18, 24)):
        x0 = x_l + a * 60 * pxm
        x1 = x_l + b * 60 * pxm
        s += f'<rect x="{x0:.1f}" y="{ty}" width="{x1 - x0:.1f}" height="{th}" fill="#0e131a"/>\n'
    for st, dur, proj in merged:
        x = x_l + st / 60.0 * pxm
        w = max(dur / 60.0 * pxm - 2, 1.5)
        s += f'<rect x="{x:.1f}" y="{ty}" width="{w:.1f}" height="{th}" rx="2" fill="{colors[proj]}"/>\n'
    # 6h 主标签
    for hr in (0, 6, 12, 18, 24):
        x = x_l + hr * 60 * pxm
        s += (f'<text x="{x:.1f}" y="{ty + th + 16}" font-size="11" fill="{MUTED}" '
              f'text-anchor="middle">{hr:02d}:00</text>\n')
    # 最长段：时长写在色块内部
    lx = x_l + (longest[0] + longest[1] / 2) / 60.0 * pxm
    if longest[1] / 60.0 * pxm > 34:
        s += (f'<text x="{lx:.1f}" y="{ty + th / 2 + 4}" font-size="11" fill="{BG}" '
              f'text-anchor="middle" font-weight="500">{int(longest[1] // 60)}m</text>\n')
    # 下 band：图例（与栅格底部对齐）
    lx0 = x_l
    for p in order:
        s += f'<circle cx="{lx0}" cy="100" r="5" fill="{colors[p]}"/>\n'
        s += f'<text x="{lx0 + 12}" y="104" font-size="13" fill="{TXT}">{p}</text>\n'
        lx0 += 12 + 8 * len(p) + 40
    s += "</svg>\n"
    open(out, "w", encoding="utf-8").write(s)


def main():
    key = get_key()
    if not key:
        raise SystemExit("no wakatime api key")
    today = datetime.date.today()

    stats = api("/users/current/stats?range=last_7_days", key)["data"]
    langs = []
    for l in stats.get("languages", []):
        if l["percent"] >= 0.3:
            langs.append((l["name"], l["percent"], LANG_COLORS.get(l["name"], "#8b949e")))
    if len(langs) < 2 or sum(p for _, p, _ in langs) < 50:
        raise SystemExit("language data too thin")

    daily, total, all_days = [], 0.0, []        # all_days: [(date, durations, secs)] 按时间正序
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        dur = api(f"/users/current/durations?date={d.isoformat()}", key).get("data", [])
        secs = sum(x.get("duration", 0) for x in dur)
        total += secs
        daily.append((d.strftime("%a"), i == 0, round(secs / 3600, 1)))
        all_days.append((d, dur, secs))

    # 时间线选哪一天：优先“最近一个编码满 2h 的日子”，全都不满就取最活跃的一天。
    # 否则遇到昨天/今天几乎没写代码，卡片会只剩一根孤零零的色块，看起来像坏了。
    MIN_SECS = 2 * 3600
    substantial = [x for x in all_days if x[2] >= MIN_SECS]
    d, dur, _ = (substantial[-1] if substantial
                 else max(all_days, key=lambda x: x[2]))
    blocks = []
    for x in dur:
        st = datetime.datetime.fromtimestamp(x["time"])
        mins = (st.hour * 60 + st.minute) * 60 + st.second
        blocks.append((mins, x.get("duration", 0), x.get("project") or "Unknown"))
    blocks.sort()

    root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(root, "assets")
    if not os.path.isdir(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
    render_langs(langs, total, os.path.join(assets_dir, "wakatime_langs.svg"))
    render_daily(daily, total, os.path.join(assets_dir, "wakatime_daily.svg"))
    label = d.strftime("%a %b %d").upper()
    render_timeline(label, blocks, sum(b[1] for b in blocks), os.path.join(assets_dir, "wakatime_day.svg"))
    print("langs:", [(n, p) for n, p, _ in langs])
    print("daily:", daily)
    print("total:", fmt_hm(total), "| timeline day:", label, "blocks:", len(blocks))


if __name__ == "__main__":
    main()
