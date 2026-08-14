import os, random, math

OUT = r"H:\Agying3\assets"
os.makedirs(OUT, exist_ok=True)
W, H = 1000, 360

def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)

PINKS = ['#ffd6e8', '#ffb7d5', '#ff9ec4', '#f778ba', '#ffc8dd']
DARK_PINK = '#d96fa0'

def petal_path(scale):
    w = 3.6 * scale; h = 8.5 * scale
    return f'M0,{-h:.1f} Q{w:.1f},0 0,{h:.1f} Q{-w:.1f},0 0,{-h:.1f} Z'

def blossom(cx, cy, scale, rot):
    g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.0f})">']
    for k in range(5):
        col = random.choice(PINKS)
        g.append(f'<g transform="rotate({k*72})"><path d="{petal_path(scale)}" fill="{col}" stroke="#ff8fb8" stroke-width="{0.5*scale:.2f}" opacity="0.95"/></g>')
    g.append(f'<circle r="{2.0*scale:.1f}" fill="#ffd84d"/>')
    for s in range(6):
        a = s * 60
        bx = 1.8 * scale * math.cos(math.radians(a)); by = 1.8 * scale * math.sin(math.radians(a))
        g.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{0.7*scale:.1f}" fill="#ffb300"/>')
    g.append('</g>')
    return ''.join(g)

def ground_y(x):
    pts = [(0, 300), (260, 278), (500, 292), (1000, 296)]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return 296

random.seed(20260813)

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="sakura under night sky">']
svg.append('<defs>'
  '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0%" stop-color="#070b18"/><stop offset="55%" stop-color="#0d1226"/><stop offset="100%" stop-color="#161b2f"/>'
  '</linearGradient>'
  '<radialGradient id="moonG" cx="40%" cy="40%" r="60%"><stop offset="0%" stop-color="#fdf3d0"/><stop offset="100%" stop-color="#d9c48a"/></radialGradient>'
  '<radialGradient id="moonHalo" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#fdf3d0" stop-opacity="0.32"/><stop offset="100%" stop-color="#fdf3d0" stop-opacity="0"/></radialGradient>'
  '<linearGradient id="bark" x1="0" y1="1" x2="0" y2="0"><stop offset="0%" stop-color="#241710"/><stop offset="100%" stop-color="#5a3a24"/></linearGradient>'
  '<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0e1410"/><stop offset="100%" stop-color="#060a08"/></linearGradient>'
  '<radialGradient id="ff" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#eaffb0" stop-opacity="0.95"/><stop offset="100%" stop-color="#eaffb0" stop-opacity="0"/></radialGradient>'
  '</defs>')

# night sky
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#sky)"/>')
for _ in range(95):
    sx = random.uniform(0, W); sy = random.uniform(0, 250); sr = random.uniform(0.5, 1.9)
    svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{sr:.1f}" fill="#e6edf3" opacity="{random.uniform(0.25,0.9):.2f}"/>')
for _ in range(7):
    sx = random.uniform(40, W-40); sy = random.uniform(20, 180); s = random.uniform(3, 6)
    svg.append(f'<path d="M{sx},{sy-s} L{sx+s*0.25},{sy-s*0.25} L{sx+s},{sy} L{sx+s*0.25},{sy+s*0.25} L{sx},{sy+s} L{sx-s*0.25},{sy+s*0.25} L{sx-s},{sy} L{sx-s*0.25},{sy-s*0.25} Z" fill="#fff" opacity="0.85"/>')

# moon
svg.append('<circle cx="838" cy="78" r="74" fill="url(#moonHalo)"/>')
svg.append('<circle cx="838" cy="78" r="38" fill="url(#moonG)"/>')
for dx, dy, dr in [(-10,-8,6),(14,6,4),(-4,16,3),(8,-16,2.5)]:
    svg.append(f'<circle cx="{838+dx}" cy="{78+dy}" r="{dr}" fill="#cdbf86" opacity="0.5"/>')

# far mountains (behind tree)
svg.append(f'<path d="M0,300 L0,288 Q160,262 330,282 T660,274 T1000,284 L1000,300 Z" fill="#0a0f1a" opacity="0.85"/>')
svg.append(f'<path d="M0,300 L0,294 Q220,272 470,290 T1000,290 L1000,300 Z" fill="#070b14" opacity="0.9"/>')

# ground + grass
svg.append(f'<path d="M0,{H} L0,300 Q260,278 500,292 T{W},296 L{W},{H} Z" fill="url(#ground)"/>')
svg.append(f'<path d="M0,300 Q260,278 500,292 T{W},296" fill="none" stroke="#1c2a1d" stroke-width="2" opacity="0.7"/>')
random.seed(7)
for _ in range(90):
    gx = random.uniform(0, W); gh = random.uniform(6, 15); lean = random.uniform(-5, 5)
    gy = ground_y(gx)
    svg.append(f'<path d="M{gx:.1f},{gy:.1f} Q{gx+lean:.1f},{gy-gh/2:.1f} {gx+lean*1.6:.1f},{gy-gh:.1f}" fill="none" stroke="#1f3322" stroke-width="1.4" opacity="0.85"/>')

# trunk + main branches
svg.append('<g fill="none" stroke="url(#bark)" stroke-linecap="round">')
svg.append('<path d="M500,318 C 492,278 512,250 500,205" stroke-width="26"/>')
svg.append('<path d="M500,218 C 470,194 438,192 408,164" stroke-width="14"/>')
svg.append('<path d="M500,218 C 530,194 562,192 594,162" stroke-width="14"/>')
svg.append('<path d="M500,232 C 500,206 500,193 500,171" stroke-width="12"/>')
svg.append('<path d="M408,164 C 386,146 366,146 348,128" stroke-width="9"/>')
svg.append('<path d="M594,162 C 616,144 636,144 654,126" stroke-width="9"/>')
svg.append('<path d="M500,171 C 486,153 470,145 452,133" stroke-width="8"/>')
svg.append('<path d="M500,171 C 514,153 530,145 548,133" stroke-width="8"/>')
svg.append('</g>')
# bark texture
svg.append('<g fill="none" stroke="#1c1109" stroke-width="1.2" opacity="0.5">')
for off in (-7, 0, 7):
    svg.append(f'<path d="M{500+off},316 C {492+off},278 {512+off},250 {500+off},206"/>')
svg.append('</g>')
# tertiary thin branches
svg.append('<g fill="none" stroke="#4a2f1c" stroke-linecap="round" opacity="0.9">')
svg.append('<path d="M348,128 C 336,118 326,116 318,104" stroke-width="4.5"/>')
svg.append('<path d="M348,128 C 360,120 368,116 378,108" stroke-width="4"/>')
svg.append('<path d="M654,126 C 666,116 676,114 686,102" stroke-width="4.5"/>')
svg.append('<path d="M654,126 C 642,118 634,114 624,106" stroke-width="4"/>')
svg.append('<path d="M452,133 C 442,122 436,118 430,108" stroke-width="4"/>')
svg.append('<path d="M548,133 C 558,122 564,118 572,108" stroke-width="4"/>')
svg.append('<path d="M408,164 C 398,152 394,148 388,138" stroke-width="4"/>')
svg.append('<path d="M594,162 C 604,150 608,146 616,136" stroke-width="4"/>')
svg.append('</g>')

# canopy (3 layers: shadow / mid / light) for volume
clusters = [
    (500,128,132),(410,154,96),(592,152,96),(346,124,78),(654,122,78),
    (452,130,74),(548,128,74),(500,84,72),(300,150,48),(700,148,48)
]
# layer 1: dark shadow
random.seed(101)
for (cx, cy, rad) in clusters:
    for _ in range(int(rad*0.7)):
        ang = random.uniform(0, 2*math.pi); dist = rad*math.sqrt(random.random())
        px = cx + dist*math.cos(ang); py = cy + dist*math.sin(ang)*0.82
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{random.uniform(6,16):.1f}" fill="{DARK_PINK}" opacity="0.32"/>')
# layer 2: mid pink
random.seed(102)
for (cx, cy, rad) in clusters:
    for _ in range(int(rad*0.95)):
        ang = random.uniform(0, 2*math.pi); dist = rad*math.sqrt(random.random())
        px = cx + dist*math.cos(ang); py = cy + dist*math.sin(ang)*0.82
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{random.uniform(5,15):.1f}" fill="{random.choice(PINKS)}" opacity="0.7"/>')
# layer 3: light + white cores
random.seed(103)
for (cx, cy, rad) in clusters:
    for _ in range(int(rad*0.6)):
        ang = random.uniform(0, 2*math.pi); dist = rad*math.sqrt(random.random())
        px = cx + dist*math.cos(ang); py = cy + dist*math.sin(ang)*0.82
        col = '#fff0f6' if random.random() > 0.6 else random.choice(['#ffd6e8','#ffc8dd'])
        svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{random.uniform(2.5,5):.1f}" fill="{col}" opacity="{random.uniform(0.5,0.9):.2f}"/>')

# single 5-petal blossoms in foreground
random.seed(21)
for _ in range(40):
    cx, cy, rad = random.choice(clusters)
    ang = random.uniform(0, 2*math.pi); dist = rad*random.uniform(0.3, 1.05)
    px = cx + dist*math.cos(ang); py = cy + dist*math.sin(ang)*0.82
    svg.append(blossom(px, py, random.uniform(6, 11), random.uniform(0, 360)))

# falling petals (pointed)
for _ in range(30):
    px = random.uniform(0, W); py = random.uniform(0, 320); rot = random.uniform(0, 360); sc = random.uniform(0.6, 1.1)
    svg.append(f'<g transform="translate({px:.1f},{py:.1f}) rotate({rot:.0f})"><path d="{petal_path(sc)}" fill="{random.choice(PINKS)}" opacity="0.85"/></g>')
# petals on ground
random.seed(33)
for _ in range(22):
    px = random.uniform(0, W); py = ground_y(px) + random.uniform(-2, 7); rot = random.uniform(0, 360)
    svg.append(f'<g transform="translate({px:.1f},{py:.1f}) rotate({rot:.0f})"><path d="{petal_path(0.7)}" fill="#ffb7d5" opacity="0.6"/></g>')

# fireflies
random.seed(44)
for _ in range(9):
    fx = random.uniform(140, 860); fy = random.uniform(150, 300); fr = random.uniform(3, 6)
    svg.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{fr*2.6:.1f}" fill="url(#ff)"/>')
    svg.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{fr:.1f}" fill="#f4ffb0" opacity="0.9"/>')

svg.append('</svg>')
write("scene_sakura.svg", ''.join(svg))
print("generated scene_sakura.svg with detailed blossoms")
