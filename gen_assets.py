import os, random, math

OUT = r"H:\Agying3\assets"
os.makedirs(OUT, exist_ok=True)

BG="#0d1117"; SURFACE="#161b22"; BORDER="#30363d"
TEXT="#e6edf3"; SUB="#8b949e"
BLUE="#58a6ff"; PURPLE="#bc8cff"; PINK="#f778ba"
RED="#ff7b72"; GREEN="#3fb950"; YELLOW="#e3b341"

def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)

# ---------- banner (name + vibe only, no bio) ----------
banner = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="240" viewBox="0 0 1000 240" role="img" aria-label="Agying3 banner">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="55%" stop-color="#161b22"/>
      <stop offset="100%" stop-color="#21262d"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="50%" stop-color="#bc8cff"/>
      <stop offset="100%" stop-color="#f778ba"/>
    </linearGradient>
    <radialGradient id="glow" cx="82%" cy="18%" r="65%">
      <stop offset="0%" stop-color="#bc8cff" stop-opacity="0.30"/>
      <stop offset="100%" stop-color="#bc8cff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="1000" height="240" rx="24" fill="url(#bg)"/>
  <rect x="0" y="0" width="1000" height="240" rx="24" fill="url(#glow)"/>
  <g stroke="#30363d" stroke-width="1" opacity="0.35">
    <line x1="0" y1="60" x2="1000" y2="60"/>
    <line x1="0" y1="120" x2="1000" y2="120"/>
    <line x1="0" y1="180" x2="1000" y2="180"/>
  </g>
  <circle cx="92" cy="120" r="54" fill="#0d1117" stroke="url(#accent)" stroke-width="3"/>
  <text x="92" y="132" font-family="Segoe UI, Arial, sans-serif" font-size="36" font-weight="800" fill="url(#accent)" text-anchor="middle">A3</text>
  <text x="172" y="108" font-family="Segoe UI, Arial, sans-serif" font-size="46" font-weight="800" fill="#e6edf3">Agying3</text>
  <text x="174" y="150" font-family="Segoe UI, Arial, sans-serif" font-size="18" fill="#58a6ff">代码是船，vibe 是帆。</text>
  <text x="174" y="184" font-family="Consolas, monospace" font-size="15" fill="#8b949e">~/Agying3 $ _</text>
</svg>'''
write("banner.svg", banner)

# ---------- kline (no caption) ----------
random.seed(42)
W,H = 1000, 300
padL, padR, padT, padB = 60, 20, 24, 24
plotW = W - padL - padR
plotH = H - padT - padB
n = 32
price = 100.0
opens=[]; closes=[]; highs=[]; lows=[]
for i in range(n):
    change = random.uniform(-6, 6.5)
    o = price; c = o + change
    hi = max(o,c) + random.uniform(0,3); lo = min(o,c) - random.uniform(0,3)
    opens.append(o); closes.append(c); highs.append(hi); lows.append(lo)
    price = c
minP = min(min(lows), min(opens)) - 2
maxP = max(max(highs), max(closes)) + 2
def x(i): return padL + (plotW)*(i+0.5)/n
def y(p): return padT + plotH*(1-(p-minP)/(maxP-minP))
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="K-line">']
svg.append(f'<defs><linearGradient id="kbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0d1117"/><stop offset="100%" stop-color="#161b22"/></linearGradient></defs>')
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#kbg)"/>')
svg.append('<g stroke="#30363d" stroke-width="1" opacity="0.4">')
for g in range(5):
    gy = padT + plotH*g/4
    svg.append(f'<line x1="{padL}" y1="{gy:.1f}" x2="{W-padR}" y2="{gy:.1f}"/>')
svg.append('</g>')
svg.append('<polyline fill="none" stroke="#58a6ff" stroke-width="2" opacity="0.8" points="')
pts=[]
for i in range(n):
    ma = sum(closes[max(0,i-3):i+1])/min(i+1,4)
    pts.append(f'{x(i):.1f},{y(ma):.1f}')
svg.append(' '.join(pts)+'"/>')
cw = plotW/n*0.6
for i in range(n):
    o,c,h,l = opens[i],closes[i],highs[i],lows[i]
    col = RED if c>=o else GREEN
    cx = x(i)
    svg.append(f'<line x1="{cx:.1f}" y1="{y(h):.1f}" x2="{cx:.1f}" y2="{y(l):.1f}" stroke="{col}" stroke-width="1.5"/>')
    yo=y(o); yc=y(c); top=min(yo,yc); hgt=max(abs(yc-yo),1.5)
    svg.append(f'<rect x="{cx-cw/2:.1f}" y="{top:.1f}" width="{cw:.1f}" height="{hgt:.1f}" fill="{col}" rx="1"/>')
svg.append('</svg>')
write("kline.svg", ''.join(svg))

# ---------- scene: night coding ----------
W,H=1000,360
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="night coding">']
svg.append('<defs>'
  '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0b0e1a"/><stop offset="100%" stop-color="#161b22"/></linearGradient>'
  '<linearGradient id="mon" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#58a6ff"/><stop offset="100%" stop-color="#bc8cff"/></linearGradient>'
  '<radialGradient id="moon" cx="40%" cy="40%" r="60%"><stop offset="0%" stop-color="#f5e6b8"/><stop offset="100%" stop-color="#d9c48a"/></radialGradient>'
  '</defs>')
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#sky)"/>')
random.seed(7)
for _ in range(55):
    sx=random.uniform(0,W); sy=random.uniform(0,300); sr=random.uniform(0.6,1.8)
    svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr:.1f}" fill="#e6edf3" opacity="{random.uniform(0.3,0.9):.1f}"/>')
svg.append('<circle cx="150" cy="90" r="36" fill="url(#moon)"/>')
svg.append('<circle cx="138" cy="80" r="7" fill="#c9b878" opacity="0.6"/>')
svg.append('<circle cx="165" cy="100" r="5" fill="#c9b878" opacity="0.5"/>')
svg.append('<rect x="60" y="55" width="190" height="175" rx="12" fill="#0a0d16" stroke="#30363d" stroke-width="3"/>')
for cx0 in range(75,235,22):
    ch=random.uniform(40,110)
    svg.append(f'<rect x="{cx0}" y="{215-ch:.1f}" width="16" height="{ch:.1f}" fill="#1b2230"/>')
    if random.random()>0.5:
        svg.append(f'<rect x="{cx0+4}" y="{218-ch:.1f}" width="3" height="3" fill="#ffd479" opacity="0.8"/>')
svg.append(f'<rect x="0" y="300" width="{W}" height="60" fill="#11151c"/>')
svg.append(f'<rect x="0" y="300" width="{W}" height="4" fill="#222a35"/>')
mx,my,mw,mh=560,130,380,190
svg.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" rx="14" fill="#0d1117" stroke="url(#mon)" stroke-width="3"/>')
random.seed(3)
cxc=mx+18; cyc=my+22; lh=13
colors=[BLUE,PURPLE,PINK,GREEN,YELLOW,"#8b949e"]
for i in range(12):
    yy=cyc+i*lh; w=random.uniform(50,300); ind=random.uniform(0,30) if i%3==0 else 0
    col=random.choice(colors)
    svg.append(f'<rect x="{cxc+ind:.1f}" y="{yy}" width="{w:.1f}" height="6" rx="3" fill="{col}" opacity="0.85"/>')
svg.append(f'<rect x="{mx+mw/2-12}" y="{my+mh}" width="24" height="22" fill="#222a35"/>')
svg.append(f'<rect x="{mx+mw/2-40}" y="{my+mh+22}" width="80" height="8" rx="4" fill="#222a35"/>')
cupx,cupy=470,255
svg.append(f'<rect x="{cupx}" y="{cupy}" width="34" height="40" rx="6" fill="#161b22" stroke="#30363d" stroke-width="2"/>')
svg.append(f'<path d="M{cupx+34} {cupy+10} q16 4 0 20" fill="none" stroke="#30363d" stroke-width="3"/>')
for s in range(3):
    bx=cupx+8+s*9
    svg.append(f'<path d="M{bx} {cupy-2} q-4 -10 2 -18 q5 -8 0 -16" fill="none" stroke="#8b949e" stroke-width="2" opacity="0.5"/>')
px=120; py=300
svg.append(f'<path d="M{px} {py} l10 -34 l10 34 z" fill="#2ea043"/>')
svg.append(f'<path d="M{px+10} {py-10} q-14 -6 -16 -22 q14 2 16 18 z" fill="#3fb950"/>')
svg.append(f'<path d="M{px+10} {py-10} q14 -6 16 -22 q-14 2 -16 18 z" fill="#3fb950"/>')
svg.append(f'<rect x="{px+2}" y="{py}" width="16" height="16" rx="2" fill="#7a4b2b"/>')
svg.append('</svg>')
write("scene_night.svg", ''.join(svg))

# ---------- scene: now playing / equalizer ----------
W,H=1000,360
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="now playing">']
svg.append('<defs>'
  '<linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0d1117"/><stop offset="100%" stop-color="#161b22"/></linearGradient>'
  '<linearGradient id="al" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#bc8cff"/><stop offset="100%" stop-color="#f778ba"/></linearGradient>'
  '</defs>')
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#bg2)"/>')
cardx,cardy,cardw,cardh=120,60,760,240
svg.append(f'<rect x="{cardx}" y="{cardy}" width="{cardw}" height="{cardh}" rx="20" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>')
ax,ay,as_=170,100,150
svg.append(f'<rect x="{ax}" y="{ay}" width="{as_}" height="{as_}" rx="16" fill="url(#al)"/>')
random.seed(11)
for b in range(7):
    bx=ax+18+b*18; bh=random.uniform(30,120)
    svg.append(f'<rect x="{bx}" y="{ay+as_-10-bh:.1f}" width="10" height="{bh:.1f}" rx="4" fill="#0d1117" opacity="0.5"/>')
tx=ax+as_+50
svg.append(f'<text x="{tx}" y="{ay+45}" font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#8b949e">♪ now playing</text>')
svg.append(f'<text x="{tx}" y="{ay+82}" font-family="Segoe UI, Arial, sans-serif" font-size="24" font-weight="700" fill="#e6edf3">lo-fi &amp; late night</text>')
svg.append(f'<text x="{tx}" y="{ay+112}" font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#8b949e">Agying3 · coding mix</text>')
pw=420; p0=ay+150
svg.append(f'<rect x="{tx}" y="{p0}" width="{pw}" height="6" rx="3" fill="#30363d"/>')
svg.append(f'<rect x="{tx}" y="{p0}" width="{pw*0.42:.0f}" height="6" rx="3" fill="url(#al)"/>')
svg.append(f'<circle cx="{tx+pw*0.42:.0f}" cy="{p0+3}" r="7" fill="#e6edf3"/>')
svg.append(f'<circle cx="{tx+22}" cy="{ay+200}" r="18" fill="url(#al)"/>')
svg.append(f'<path d="M{tx+16} {ay+192} l16 8 l-16 8 z" fill="#0d1117"/>')
svg.append('</svg>')
write("scene_music.svg", ''.join(svg))

# ---------- footer (no "小天地" text) ----------
FW, FH = 1000, 100
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}" role="img" aria-label="footer">']
svg.append(f'<defs><linearGradient id="fbg" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#58a6ff"/><stop offset="50%" stop-color="#bc8cff"/><stop offset="100%" stop-color="#f778ba"/></linearGradient></defs>')
svg.append(f'<rect x="0" y="0" width="{FW}" height="{FH}" fill="#0d1117"/>')
path = "M0,55 "
for x in range(0, FW+20, 20):
    yv = 55 + 16*math.sin(x/70.0)
    path += f"L{x},{yv:.1f} "
path += f"L{FW},100 L0,100 Z"
svg.append(f'<path d="{path}" fill="url(#fbg)" opacity="0.9"/>')
svg.append(f'<text x="{FW/2}" y="62" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#0d1117" text-anchor="middle" font-weight="700">Agying3</text>')
svg.append('</svg>')
write("footer.svg", ''.join(svg))

print("generated:", sorted(os.listdir(OUT)))
