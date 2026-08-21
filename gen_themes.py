import os, random, math

OUT = r"H:\Agying3\assets"
os.makedirs(OUT, exist_ok=True)

# ---- 调色板：墨绿流金（深松绿 → 暖金）----
DARK = dict(
    bg0="#0d1117", bg1="#161b22", bg2="#21262d",
    surface="#161b22", surface2="#0d1117", border="#30363d",
    text="#e6edf3", sub="#8b949e",
    blue="#1f7a4d", purple="#3fae8a", pink="#d4a24e",
    red="#ff7b72", green="#3fb950", yellow="#e3b341",
    sky0="#0b0e1a", sky1="#161b22", star="#e6edf3",
    winbg="#0a0d16", winfill="#1b2230", cityglow="#d4a24e",
    ground="#11151c", groundline="#222a35",
    mon0="#1f7a4d", mon1="#d4a24e",
    foottext="#0d1117",
)
LIGHT = dict(
    bg0="#f6f8fa", bg1="#eaeef2", bg2="#d0d7de",
    surface="#ffffff", surface2="#f6f8fa", border="#d0d7de",
    text="#1f2328", sub="#656d76",
    blue="#1f7a4d", purple="#2f8f5f", pink="#b8860b",
    red="#cf222e", green="#1a7f37", yellow="#9a6700",
    sky0="#acc6e6", sky1="#dce9f5", star="#ffffff",
    winbg="#cdd6e0", winfill="#aeb9c7", cityglow="#bf8700",
    ground="#e1e6eb", groundline="#c9d1d9",
    mon0="#1f7a4d", mon1="#b8860b",
    foottext="#ffffff",
)

def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)

# ---------- 内嵌 Terminus 字体（子集化，base64）----------
# 让没有安装 Terminus 的查看者也看到一致字体（全员一致）。
import base64
_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_REG_B64, _BOLD_B64 = None, None

def terminus_fontface():
    global _REG_B64, _BOLD_B64
    if _REG_B64 is None:
        with open(os.path.join(_FONT_DIR, "terminus_regular.subset.ttf"), "rb") as f:
            _REG_B64 = base64.b64encode(f.read()).decode("ascii")
        with open(os.path.join(_FONT_DIR, "terminus_bold.subset.ttf"), "rb") as f:
            _BOLD_B64 = base64.b64encode(f.read()).decode("ascii")
    return (
        '<style>'
        "@font-face{font-family:'Terminus';font-weight:400;font-style:normal;"
        f"src:url(data:font/ttf;base64,{_REG_B64}) format('truetype');}}"
        "@font-face{font-family:'Terminus';font-weight:700;font-style:normal;"
        f"src:url(data:font/ttf;base64,{_BOLD_B64}) format('truetype');}}"
        '</style>'
    )

FONT = "'Terminus', monospace"

# 随机闪烁星屑（多处复用）
def sparkles(P, n, W, H, seed=1, rmax=2.2, opacity=0.8, ymax=None):
    random.seed(seed)
    ymax = ymax or H
    out=[]
    for _ in range(n):
        x=random.uniform(0,W); y=random.uniform(0,ymax); r=random.uniform(0.5,rmax)
        op=random.uniform(0.2,opacity); dur=round(random.uniform(1.5,3.5),2)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{P["star"]}" opacity="{op:.2f}">'
                   f'<animate attributeName="opacity" values="{op:.2f};0.1;{op:.2f}" dur="{dur}s" repeatCount="indefinite"/>'
                   f'</circle>')
    return ''.join(out)

# ---------- banner ----------
def banner(P):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="240" viewBox="0 0 1000 240" role="img" aria-label="Agying3 banner">
  <defs>
    {terminus_fontface()}
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{P['bg0']}"/>
      <stop offset="55%" stop-color="{P['bg1']}"/>
      <stop offset="100%" stop-color="{P['bg2']}"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{P['blue']}"/>
      <stop offset="50%" stop-color="{P['purple']}"/>
      <stop offset="100%" stop-color="{P['pink']}"/>
    </linearGradient>
    <radialGradient id="glow" cx="82%" cy="18%" r="65%">
      <stop offset="0%" stop-color="{P['purple']}" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="{P['purple']}" stop-opacity="0"/>
    </radialGradient>
    <filter id="neon" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5"/></filter>
  </defs>
  <rect x="0" y="0" width="1000" height="240" rx="24" fill="url(#bg)"/>
  <rect x="0" y="0" width="1000" height="240" rx="24" fill="url(#glow)"/>
  {sparkles(P, 16, 1000, 240, seed=21, rmax=1.8)}
  <text x="40" y="120" font-family="{FONT}" font-size="52" font-weight="800" fill="url(#accent)" filter="url(#neon)">Agying3<animate attributeName="opacity" values="0.35;0.9;0.35" dur="2.4s" repeatCount="indefinite"/></text>
  <text x="40" y="120" font-family="{FONT}" font-size="52" font-weight="800" fill="url(#accent)">Agying3</text>
  <text x="42" y="162" font-family="{FONT}" font-size="16" fill="{P['sub']}">~/Agying3 $ _</text>
  <rect x="170" y="148" width="11" height="18" rx="2" fill="url(#accent)">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.55;1" dur="1.1s" repeatCount="indefinite"/>
  </rect>
</svg>'''

# ---------- kline ----------
def kline(P):
    """滚动 K 线：价格随机游走生成 varied 蜡烛，整组向左平移形成「实时前进」感；
    后半段按索引取模复制前半段，使平移一个屏幕宽度后无缝循环。
    注：GitHub 以 <img> 渲染 SVG 时剥离 <script>，无法真正随机；
    这里用固定种子生成多样序列来模拟实时跳动。"""
    random.seed(42)
    W,H = 1000, 300
    padL, padR, padT, padB = 60, 20, 24, 24
    plotW = W - padL - padR; plotH = H - padT - padB
    pitch = 26; cw = 15
    visibleN = int(plotW / pitch)            # 一屏可见蜡烛数
    N = visibleN * 2 + 8                      # 总数（后半复制前半，并多留几根保证滚动覆盖）
    price = 100.0
    o=[]; c=[]; h=[]; l=[]
    for i in range(visibleN):
        change = random.uniform(-6, 6.5)
        oo = price; cc = oo + change
        hi = max(oo,cc) + random.uniform(0,3); lo = min(oo,cc) - random.uniform(0,3)
        o.append(oo); c.append(cc); h.append(hi); l.append(lo); price = cc
    for j in range(visibleN, N):              # 复制前半（取模），保证无缝循环
        k = j % visibleN
        o.append(o[k]); c.append(c[k]); h.append(h[k]); l.append(l[k])
    minP = min(min(l), min(o)) - 2; maxP = max(max(h), max(c)) + 2
    def x(i): return padL + pitch*(i+0.5)
    def y(p): return padT + plotH*(1-(p-minP)/(maxP-minP))
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="K-line">']
    svg.append(f'<defs><linearGradient id="kbg" x1="0" y1="0" x2="0" y2="1">'
               f'<stop offset="0%" stop-color="{P["bg0"]}"/>'
               f'<stop offset="100%" stop-color="{P["bg1"]}"/></linearGradient></defs>')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#kbg)"/>')
    svg.append(f'<g stroke="{P["border"]}" stroke-width="1" opacity="0.4">')
    for g in range(5):
        gy = padT + plotH*g/4
        svg.append(f'<line x1="{padL}" y1="{gy:.1f}" x2="{W-padR}" y2="{gy:.1f}"/>')
    svg.append('</g>')
    # 滚动组：蜡烛 + 均线一起向左平移
    g=[]
    ma=[sum(c[max(0,i-3):i+1])/min(i+1,4) for i in range(N)]
    pts=' '.join(f'{x(i):.1f},{y(ma[i]):.1f}' for i in range(N))
    g.append(f'<polyline fill="none" stroke="{P["blue"]}" stroke-width="2" opacity="0.8" points="{pts}"/>')
    for i in range(N):
        col = P["red"] if c[i] >= o[i] else P["green"]
        cx = x(i); yo=y(o[i]); yc=y(c[i]); top=min(yo,yc); hgt=max(abs(yc-yo),1.5)
        g.append(f'<line x1="{cx:.1f}" y1="{y(h[i]):.1f}" x2="{cx:.1f}" y2="{y(l[i]):.1f}" stroke="{col}" stroke-width="1.5"/>')
        g.append(f'<rect x="{cx-cw/2:.1f}" y="{top:.1f}" width="{cw:.1f}" height="{hgt:.1f}" fill="{col}" rx="1"/>')
    dur = 14
    svg.append(f'<g>{"".join(g)}'
               f'<animateTransform attributeName="transform" type="translate" '
               f'values="0 0;{-visibleN*pitch} 0" dur="{dur}s" '
               f'calcMode="linear" repeatCount="indefinite"/></g>')
    # 扫描线（上下扫动，装饰）
    svg.append(f'<rect x="{padL}" y="{padT}" width="{plotW}" height="2" fill="{P["blue"]}" opacity="0.5">'
               f'<animate attributeName="y" values="{padT};{padT+plotH};{padT}" dur="4.5s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values="0.1;0.7;0.1" dur="4.5s" repeatCount="indefinite"/>'
               f'</rect>')
    # 右侧「当前价」虚线，强化实时感（固定位置，不随滚动）
    svg.append(f'<line x1="{W-padR}" y1="{padT}" x2="{W-padR}" y2="{padT+plotH}" '
               f'stroke="{P["pink"]}" stroke-width="1" stroke-dasharray="3 4" opacity="0.6"/>')
    svg.append('</svg>')
    return ''.join(svg)

# ---------- scene: night coding ----------
def scene_night(P):
    W,H=1000,360
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="night coding">']
    svg.append('<defs>'
      f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{P["sky0"]}"/><stop offset="100%" stop-color="{P["sky1"]}"/></linearGradient>'
      f'<linearGradient id="mon" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{P["mon0"]}"/><stop offset="100%" stop-color="{P["mon1"]}"/></linearGradient>'
      '<radialGradient id="moon" cx="40%" cy="40%" r="60%"><stop offset="0%" stop-color="#f5e6b8"/><stop offset="100%" stop-color="#d9c48a"/></radialGradient>'
      '<linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#39d98a"/><stop offset="50%" stop-color="#d4a24e"/><stop offset="100%" stop-color="#39d98a"/></linearGradient>'
      '</defs>')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#sky)"/>')
    # 极光带
    svg.append('<g opacity="0.22">'
      '<path d="M-60,30 Q250,0 500,30 T1060,30 L1060,150 Q500,90 -60,150 Z" fill="url(#aurora)"/>'
      '<animate attributeName="opacity" values="0.12;0.32;0.12" dur="5s" repeatCount="indefinite"/>'
      '</g>')
    # 星空 + 闪烁
    random.seed(7)
    for _ in range(55):
        sx=random.uniform(0,W); sy=random.uniform(0,300); sr=random.uniform(0.6,1.8)
        op=random.uniform(0.3,0.9)
        if _ % 3 == 0:
            dur=round(random.uniform(1.8,3.6),2)
            svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr:.1f}" fill="{P["star"]}" opacity="{op:.1f}">'
                       f'<animate attributeName="opacity" values="{op:.1f};0.15;{op:.1f}" dur="{dur}s" repeatCount="indefinite"/>'
                       f'</circle>')
        else:
            svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr:.1f}" fill="{P["star"]}" opacity="{op:.1f}"/>')
    # 流星
    for k in range(2):
        sx = 220 + k*520; sy = 25 + k*40
        svg.append(f'<g>'
          f'<line x1="0" y1="0" x2="46" y2="15" stroke="{P["star"]}" stroke-width="2.4" stroke-linecap="round" opacity="0">'
          f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.8;1" dur="{6+k*2.5}s" begin="{k*3.5}s" repeatCount="indefinite"/>'
          f'</line>'
          f'<animateTransform attributeName="transform" type="translate" from="{sx} {sy}" to="{sx+300} {sy+95}" dur="{6+k*2.5}s" begin="{k*3.5}s" repeatCount="indefinite"/>'
          f'</g>')
    svg.append('<circle cx="150" cy="90" r="36" fill="url(#moon)"/>')
    svg.append('<circle cx="138" cy="80" r="7" fill="#c9b878" opacity="0.6"/>')
    svg.append('<circle cx="165" cy="100" r="5" fill="#c9b878" opacity="0.5"/>')
    svg.append(f'<rect x="60" y="55" width="190" height="175" rx="12" fill="{P["winbg"]}" stroke="{P["border"]}" stroke-width="3"/>')
    for cx0 in range(75,235,22):
        ch=random.uniform(40,110)
        svg.append(f'<rect x="{cx0}" y="{215-ch:.1f}" width="16" height="{ch:.1f}" fill="{P["winfill"]}"/>')
        if random.random()>0.5:
            svg.append(f'<rect x="{cx0+4}" y="{218-ch:.1f}" width="3" height="3" fill="{P["cityglow"]}" opacity="0.8"/>')
    svg.append(f'<rect x="0" y="300" width="{W}" height="60" fill="{P["ground"]}"/>')
    svg.append(f'<rect x="0" y="300" width="{W}" height="4" fill="{P["groundline"]}"/>')
    mx,my,mw,mh=560,130,380,190
    svg.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="14" fill="{P["surface2"]}" stroke="url(#mon)" stroke-width="3"/>')
    random.seed(3)
    cxc=mx+18; cyc=my+22; lh=13
    colors=[P["blue"],P["purple"],P["pink"],P["green"],P["yellow"],P["sub"]]
    for i in range(12):
        yy=cyc+i*lh; w=random.uniform(50,300); ind=random.uniform(0,30) if i%3==0 else 0
        col=random.choice(colors)
        svg.append(f'<rect x="{cxc+ind:.1f}" y="{yy}" width="{w:.1f}" height="6" rx="3" fill="{col}" opacity="0.85"/>')
    svg.append(f'<rect x="{mx+mw/2-12}" y="{my+mh}" width="24" height="22" fill="{P["groundline"]}"/>')
    svg.append(f'<rect x="{mx+mw/2-40}" y="{my+mh+22}" width="80" height="8" rx="4" fill="{P["groundline"]}"/>')
    cupx,cupy=470,255
    svg.append(f'<rect x="{cupx}" y="{cupy}" width="34" height="40" rx="6" fill="{P["surface"]}" stroke="{P["border"]}" stroke-width="2"/>')
    svg.append(f'<path d="M{cupx+34} {cupy+10} q16 4 0 20" fill="none" stroke="{P["border"]}" stroke-width="3"/>')
    for s in range(3):
        bx=cupx+8+s*9
        svg.append(f'<path d="M{bx} {cupy-2} q-4 -10 2 -18 q5 -8 0 -16" fill="none" stroke="{P["sub"]}" stroke-width="2" opacity="0.5"/>')
    px=120; py=300
    svg.append(f'<path d="M{px} {py} l10 -34 l10 34 z" fill="{P["green"]}"/>')
    svg.append(f'<path d="M{px+10} {py-10} q-14 -6 -16 -22 q14 2 16 18 z" fill="{P["green"]}"/>')
    svg.append(f'<path d="M{px+10} {py-10} q14 -6 16 -22 q-14 2 -16 18 z" fill="{P["green"]}"/>')
    svg.append(f'<rect x="{px+2}" y="{py}" width="16" height="16" rx="2" fill="#7a4b2b"/>')
    svg.append('</svg>')
    return ''.join(svg)

# ---------- scene: now playing ----------
def scene_music(P):
    W,H=1000,360
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="now playing">']
    svg.append('<defs>'
      f'<linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{P["bg0"]}"/><stop offset="100%" stop-color="{P["bg1"]}"/></linearGradient>'
      f'<linearGradient id="al" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{P["purple"]}"/><stop offset="100%" stop-color="{P["pink"]}"/></linearGradient>'
      '<linearGradient id="eqc" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{P["purple"]}"><animate attributeName="stop-color" values="{P["purple"]};{P["pink"]};{P["blue"]};{P["purple"]}" dur="4s" repeatCount="indefinite"/></stop>'
        f'<stop offset="100%" stop-color="{P["pink"]}"><animate attributeName="stop-color" values="{P["pink"]};{P["blue"]};{P["purple"]};{P["pink"]}" dur="4s" repeatCount="indefinite"/></stop>'
      '</linearGradient>'
      '</defs>')
    svg.append(terminus_fontface())
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#bg2)"/>')
    cardx,cardy,cardw,cardh=120,60,760,240
    svg.append(f'<rect x="{cardx}" y="{cardy}" width="{cardw}" height="{cardh}" rx="20" fill="{P["surface2"]}" stroke="{P["border"]}" stroke-width="1.5"/>')
    ax,ay,as_=170,100,150
    svg.append(f'<rect x="{ax}" y="{ay}" width="{as_}" height="{as_}" rx="16" fill="url(#al)"/>')
    # 唱片旋转
    svg.append(f'<g>'
      f'<circle cx="{ax+as_/2:.0f}" cy="{ay+as_/2:.0f}" r="{as_/2-18:.0f}" fill="none" stroke="{P["surface2"]}" stroke-width="2" opacity="0.6"/>'
      f'<circle cx="{ax+as_/2:.0f}" cy="{ay+as_/2:.0f}" r="10" fill="{P["surface2"]}"/>'
      f'<animateTransform attributeName="transform" type="rotate" from="0 {ax+as_/2:.0f} {ay+as_/2:.0f}" to="360 {ax+as_/2:.0f} {ay+as_/2:.0f}" dur="6s" repeatCount="indefinite"/>'
      f'</g>')
    random.seed(11)
    for b in range(7):
        bx=ax+18+b*18; bh=random.uniform(30,120)
        y0=ay+as_-10-bh
        dur=round(random.uniform(0.7,1.4),2)
        svg.append(f'<rect x="{bx}" y="{y0:.1f}" width="10" height="{bh:.1f}" rx="4" fill="url(#eqc)">'
                   f'<animate attributeName="height" values="{bh:.1f};{bh*0.35:.1f};{bh:.1f}" dur="{dur}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="y" values="{y0:.1f};{ay+as_-10-bh*0.35:.1f};{y0:.1f}" dur="{dur}s" repeatCount="indefinite"/>'
                   f'</rect>')
    # 飘动的音符
    for k in range(3):
        nx = ax+as_+150 + k*120
        svg.append(f'<text x="{nx}" y="{ay+as_-20}" font-family="{FONT}" font-size="22" fill="{P["purple"]}" opacity="0">♪'
          f'<animate attributeName="opacity" values="0;0.9;0" dur="3s" begin="{k*1}s" repeatCount="indefinite"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 0; 0 -130" dur="3s" begin="{k*1}s" repeatCount="indefinite"/>'
          f'</text>')
    tx=ax+as_+50
    svg.append(f'<text x="{tx}" y="{ay+45}" font-family="{FONT}" font-size="15" fill="{P["sub"]}">♪ now playing</text>')
    svg.append(f'<text x="{tx}" y="{ay+82}" font-family="{FONT}" font-size="24" font-weight="700" fill="{P["text"]}">lo-fi &amp; late night</text>')
    svg.append(f'<text x="{tx}" y="{ay+112}" font-family="{FONT}" font-size="15" fill="{P["sub"]}">Agying3 · coding mix</text>')
    pw=420; p0=ay+150
    svg.append(f'<rect x="{tx}" y="{p0}" width="{pw}" height="6" rx="3" fill="{P["border"]}"/>')
    svg.append(f'<rect x="{tx}" y="{p0}" width="{pw*0.42:.0f}" height="6" rx="3" fill="url(#al)"/>')
    svg.append(f'<circle cx="{tx+pw*0.42:.0f}" cy="{p0+3}" r="7" fill="{P["text"]}"/>')
    svg.append(f'<circle cx="{tx+22}" cy="{ay+200}" r="18" fill="url(#al)"/>')
    svg.append(f'<path d="M{tx+16} {ay+192} l16 8 l-16 8 z" fill="{P["surface2"]}"/>')
    svg.append('</svg>')
    return ''.join(svg)

# ---------- footer ----------
def footer(P):
    FW, FH = 1000, 100
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}" role="img" aria-label="footer">']
    svg.append('<defs>' + terminus_fontface() + '<linearGradient id="fbg" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0%" stop-color="{P["blue"]}"/><stop offset="100%" stop-color="{P["pink"]}"/></linearGradient></defs>')
    svg.append(f'<rect x="0" y="0" width="{FW}" height="{FH}" fill="{P["bg0"]}"/>')
    svg.append(f'<line x1="0" y1="50" x2="{FW}" y2="50" stroke="{P["border"]}" stroke-width="1" opacity="0.4"/>')
    svg.append(f'<rect x="0" y="54" width="{FW}" height="2" fill="url(#fbg)" opacity="0.7"/>')
    svg.append(f'<text x="{FW/2}" y="42" font-family="{FONT}" font-size="14" fill="{P["text"]}" text-anchor="middle" font-weight="700">Agying3</text>')
    svg.append(f'<circle cx="{FW/2}" cy="72" r="3" fill="{P["pink"]}" opacity="0.6"/>')
    svg.append('</svg>')
    return ''.join(svg)

# ---------- wheel (vinyl turntable) ----------
def wheel(P):
    W,H=1000,360
    cx,cy,R=500,180,150
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="vibe turntable">']
    svg.append('<defs>'
      f'<linearGradient id="wbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{P["bg0"]}"/><stop offset="100%" stop-color="{P["bg1"]}"/></linearGradient>'
      f'<radialGradient id="lbl" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{P["pink"]}"/><stop offset="100%" stop-color="{P["blue"]}"/></radialGradient>'
      f'<radialGradient id="wglow" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{P["pink"]}" stop-opacity="0.3"/><stop offset="100%" stop-color="{P["pink"]}" stop-opacity="0"/></radialGradient>'
      '</defs>')
    svg.append(terminus_fontface())
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#wbg)"/>')
    # 外发光呼吸
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R+24}" fill="url(#wglow)">'
               f'<animate attributeName="opacity" values="0.4;0.85;0.4" dur="3.4s" repeatCount="indefinite"/></circle>')
    # 黑胶盘（整体旋转，像在放唱片）
    svg.append('<g>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{P["bg2"]}" stroke="{P["border"]}" stroke-width="1.5"/>')
    for i in range(1, 6):
        rr = R * (0.34 + i*0.11)
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{P["sub"]}" stroke-width="1" opacity="0.45"/>')
    # 高光弧（独立旋转，制造反光）
    svg.append(f'<path d="M {cx-R*0.72:.1f} {cy-R*0.64:.1f} A {R*0.72:.1f} {R*0.72:.1f} 0 0 1 {cx+R*0.72:.1f} {cy-R*0.64:.1f}" '
               f'fill="none" stroke="{P["pink"]}" stroke-width="3" opacity="0.4" stroke-linecap="round">'
               f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="6s" repeatCount="indefinite"/></path>')
    # 中心标签（呼吸）
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R*0.3:.1f}" fill="url(#lbl)">'
               f'<animate attributeName="opacity" values="0.85;1;0.85" dur="2.6s" repeatCount="indefinite"/></circle>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{R*0.05:.1f}" fill="{P["bg0"]}"/>')
    svg.append(f'<text x="{cx}" y="{cy+6}" font-family="{FONT}" font-size="26" font-weight="800" fill="{P["foottext"]}" text-anchor="middle">VIBE</text>')
    svg.append(f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="8s" repeatCount="indefinite"/>')
    svg.append('</g>')
    svg.append('</svg>')
    return ''.join(svg)

# ---------- 波浪分隔 ----------
def wave(P):
    W,H=1000,80
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="divider">']
    svg.append(f'<line x1="0" y1="{H-1}" x2="{W}" y2="{H-1}" stroke="{P["border"]}" stroke-width="1" opacity="0.35"/>')
    path = "M 30 44 C 200 36, 380 52, 520 40 C 660 30, 820 48, 970 42"
    svg.append(f'<path d="{path}" fill="none" stroke="{P["blue"]}" stroke-width="2" stroke-linecap="round" opacity="0.4"/>')
    svg.append(f'<circle cx="520" cy="18" r="2.5" fill="{P["pink"]}" opacity="0.45"/>')
    svg.append('</svg>')
    return ''.join(svg)

# ---------- avatar（左摇右晃）----------
def avatar():
    # 把头像 PNG 内嵌进去，保证全员可见；并以底部为支点做钟摆式左右摇摆。
    # 画布放大到 270x250、支点下移，使头像在 ±9° 摆动时始终完整落在 viewBox 内，
    # 避免被边缘裁切（旧版 200x200 会被切出"白边"）。
    ap = os.path.join(OUT, "avatar.png")
    if os.path.exists(ap):
        with open(ap, "rb") as f:
            href = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
    else:
        href = "avatar.png"
    cx, cy, r = 135, 118, 97          # 头像圆心 / 裁切半径
    ring = 103                        # 墨绿→暖金圆环
    ix, iy = cx - r, cy - r           # 头像图片左上角
    px, py = 135, 245                 # 钟摆支点（底部中央，落在画布内）
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="270" height="250" viewBox="0 0 270 250" role="img" aria-label="Agying3 avatar">
  <defs>
    <clipPath id="ac"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
    <radialGradient id="aring" cx="50%" cy="50%" r="50%">
      <stop offset="76%" stop-color="#1f7a4d"/>
      <stop offset="90%" stop-color="#d4a24e"/>
      <stop offset="100%" stop-color="#1f7a4d"/>
    </radialGradient>
  </defs>
  <g>
    <circle cx="{cx}" cy="{cy}" r="{ring}" fill="url(#aring)"/>
    <g clip-path="url(#ac)"><image x="{ix}" y="{iy}" width="194" height="194" href="{href}" preserveAspectRatio="xMidYMid slice"/></g>
    <animateTransform attributeName="transform" type="rotate"
      values="-9 {px} {py}; 9 {px} {py}; -9 {px} {py}"
      keyTimes="0;0.5;1" calcMode="spline"
      keySplines="0.42 0 0.58 1; 0.42 0 0.58 1"
      dur="3.2s" repeatCount="indefinite"/>
  </g>
</svg>'''

# ---------- 生成 ----------
write("avatar.svg", avatar())  # 主题无关，生成一份
for P, sfx in [(DARK, "dark"), (LIGHT, "light")]:
    write(f"banner_{sfx}.svg", banner(P))
    write(f"kline_{sfx}.svg", kline(P))
    write(f"scene_night_{sfx}.svg", scene_night(P))
    write(f"scene_music_{sfx}.svg", scene_music(P))
    write(f"wheel_{sfx}.svg", wheel(P))
    write(f"footer_{sfx}.svg", footer(P))
    write(f"wave_{sfx}.svg", wave(P))

print("generated:", sorted(os.listdir(OUT)))
