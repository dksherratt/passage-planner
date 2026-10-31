"""Generate the Colours for Health pouch front-panel artwork as SVG."""
import base64, math, random, sys

random.seed(7)
W, H = 1100, 1400
FONTS = "/tmp/cfh/fonts"

PINK, ORANGE, TEAL, YELLOW, CYAN = "#FF2D8E", "#FF6A1A", "#0FA3A8", "#FFC81E", "#33D6F0"
RED, CREAM, BLACK, INK = "#FF3B2F", "#E9E1D3", "#0D0D0F", "#141416"


def b64(name):
    return base64.b64encode(open(f"{FONTS}/{name}", "rb").read()).decode()


def f(x):
    return f"{x:.1f}"


def torn(pts, jit=6, step=9):
    """Roughen a polygon's edges so it reads as torn paper."""
    out = []
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x2 - x1, y2 - y1)
        k = max(1, int(L / step))
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        for j in range(k):
            t = j / k
            o = random.uniform(-jit, jit) if j else 0
            out.append((x1 + (x2 - x1) * t + nx * o, y1 + (y2 - y1) * t + ny * o))
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in out) + "Z"


def rect(cx, cy, w, h, ang):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        pts.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
    return pts


def halftone(x0, y0, x1, y1, ang, cell, rmax, fn, color):
    """True halftone: dot radius driven by fn(u,v) in 0..1 across the box."""
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + cell
    dots = []
    i = -R
    while i < R:
        j = -R
        while j < R:
            x, y = cx + i * c - j * s, cy + i * s + j * c
            if x0 <= x <= x1 and y0 <= y <= y1:
                u, v = (x - x0) / (x1 - x0), (y - y0) / (y1 - y0)
                r = rmax * fn(u, v)
                if r > 0.5:
                    dots.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}"/>')
            j += cell
        i += cell
    return f'<g fill="{color}">' + "".join(dots) + "</g>"


def palm(x, y, length, ang, blades=26, color=BLACK):
    """Palm frond: curved spine with tapering blades off both sides."""
    a = math.radians(ang)
    parts = []
    spine = []
    for k in range(blades + 1):
        t = k / blades
        bend = math.sin(t * math.pi * 0.9) * length * 0.12
        px = x + math.cos(a) * length * t - math.sin(a) * bend
        py = y + math.sin(a) * length * t + math.cos(a) * bend
        spine.append((px, py))
    for k in range(1, blades):
        t = k / blades
        px, py = spine[k]
        qx, qy = spine[k + 1]
        d = math.atan2(qy - py, qx - px)
        bl = length * 0.42 * math.sin(t * math.pi) ** 0.7 * (1 - 0.35 * t)
        for side in (-1, 1):
            da = d + side * math.radians(48 + 20 * t)
            tipx, tipy = px + math.cos(da) * bl, py + math.sin(da) * bl
            wv = 7 * (1 - t) + 3
            parts.append(
                f'<path d="M{f(px)},{f(py)} Q{f((px+tipx)/2 + math.cos(d)*wv)},{f((py+tipy)/2 + math.sin(d)*wv)} '
                f'{f(tipx)},{f(tipy)} Q{f((px+tipx)/2 + math.cos(d)*wv*2.2)},{f((py+tipy)/2 + math.sin(d)*wv*2.2)} '
                f'{f(qx)},{f(qy)}Z"/>'
            )
    sp = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in spine)
    return (f'<g fill="{color}">' + "".join(parts) + "</g>"
            f'<path d="{sp}" stroke="{color}" stroke-width="5" fill="none" stroke-linecap="round"/>')


def citrus(cx, cy, r):
    seg = []
    n = 11
    for k in range(n):
        a0 = 2 * math.pi * k / n + 0.06
        a1 = 2 * math.pi * (k + 1) / n - 0.06
        ri, ro = r * 0.07, r * 0.80
        pts = [(cx + math.cos(a0) * ri * 3, cy + math.sin(a0) * ri * 3)]
        for m in range(9):
            aa = a0 + (a1 - a0) * m / 8
            pts.append((cx + math.cos(aa) * ro, cy + math.sin(aa) * ro))
        pts.append((cx + math.cos(a1) * ri * 3, cy + math.sin(a1) * ri * 3))
        seg.append(f'<path d="{torn(pts, 1.5, 6)}" fill="{RED}"/>')
        # juice vesicles
        for _ in range(9):
            aa = random.uniform(a0 + 0.05, a1 - 0.05)
            rr = random.uniform(ro * 0.35, ro * 0.9)
            seg.append(f'<path d="M{f(cx+math.cos(aa)*rr*0.8)},{f(cy+math.sin(aa)*rr*0.8)} L{f(cx+math.cos(aa)*rr)},{f(cy+math.sin(aa)*rr)}" '
                       f'stroke="{PINK}" stroke-width="3" stroke-linecap="round"/>')
    return (f'<g filter="url(#paper)"><circle cx="{cx}" cy="{cy}" r="{r}" fill="{ORANGE}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.9}" fill="{CREAM}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.83}" fill="#FFD9C9"/>' + "".join(seg) + "</g>")


def splatter(cx, cy, spread, n, color, rmax=6):
    out = []
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        d = abs(random.gauss(0, spread))
        r = max(0.6, rmax * random.random() ** 3)
        out.append(f'<circle cx="{f(cx+math.cos(a)*d)}" cy="{f(cy+math.sin(a)*d)}" r="{f(r)}"/>')
    return f'<g fill="{color}">' + "".join(out) + "</g>"


def width_of(text, size):
    from fontTools.ttLib import TTFont
    ft = TTFont(f"{FONTS}/Anton.ttf")
    cm, hm, upm = ft.getBestCmap(), ft["hmtx"], ft["head"].unitsPerEm
    return sum(hm[cm[ord(c)]][0] for c in text) / upm * size


defs = f"""
<style>
@font-face {{ font-family: 'Anton'; src: url(data:font/ttf;base64,{b64('Anton.ttf')}); }}
@font-face {{ font-family: 'Mont'; font-weight: 400; src: url(data:font/ttf;base64,{b64('Mont-400.ttf')}); }}
@font-face {{ font-family: 'Mont'; font-weight: 600; src: url(data:font/ttf;base64,{b64('Mont-600.ttf')}); }}
@font-face {{ font-family: 'Mont'; font-weight: 700; src: url(data:font/ttf;base64,{b64('Mont-700.ttf')}); }}
.cap {{ font-family: 'Mont'; letter-spacing: 0.16em; fill: #EDEAE4; }}
</style>
<filter id="paper" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -7 4.9" result="speck"/>
  <feComposite in="SourceGraphic" in2="speck" operator="in" result="holes"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="4" seed="9" result="m"/>
  <feColorMatrix in="m" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -16 11.2" result="blot"/>
  <feComposite in="holes" in2="blot" operator="in" result="distressed"/>
  <feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="1" seed="5" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.5 -0.22" result="grain"/>
  <feComposite in="grain" in2="distressed" operator="in" result="grainIn"/>
  <feMerge><feMergeNode in="distressed"/><feMergeNode in="grainIn"/></feMerge>
</filter>
<filter id="foilTex" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.07 0.11" numOctaves="2" seed="11" result="t"/>
  <feColorMatrix in="t" type="saturate" values="0" result="tg"/>
  <feComponentTransfer in="tg" result="tc"><feFuncR type="gamma" exponent="0.7" amplitude="1.25"/><feFuncG type="gamma" exponent="0.7" amplitude="1.25"/><feFuncB type="gamma" exponent="0.7" amplitude="1.25"/></feComponentTransfer>
  <feBlend in="SourceGraphic" in2="tc" mode="multiply" result="b"/>
  <feComposite in="b" in2="SourceAlpha" operator="in"/>
</filter>
<filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="2"/><feDisplacementMap in="SourceGraphic" scale="5"/></filter>
<linearGradient id="foil" x1="0" y1="0" x2="1" y2="0.55">
  <stop offset="0" stop-color="#FFFFFF"/><stop offset="0.14" stop-color="#9C9CA2"/>
  <stop offset="0.27" stop-color="#F4F4F6"/><stop offset="0.42" stop-color="#7C7C84"/>
  <stop offset="0.55" stop-color="#FFFFFF"/><stop offset="0.7" stop-color="#A4A4AA"/>
  <stop offset="0.84" stop-color="#EDEDF0"/><stop offset="1" stop-color="#8A8A90"/>
</linearGradient>
<pattern id="stripes" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(-28)">
  <rect width="22" height="11" fill="{YELLOW}"/></pattern>
<pattern id="stripesK" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(62)">
  <rect width="14" height="5" fill="{BLACK}"/></pattern>
<pattern id="check" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(-28)">
  <rect width="20" height="20" fill="{BLACK}"/><rect x="20" y="20" width="20" height="20" fill="{BLACK}"/></pattern>
<pattern id="dotsK" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(18)">
  <circle cx="6" cy="6" r="3.2" fill="{BLACK}"/></pattern>
<pattern id="wave" width="60" height="30" patternUnits="userSpaceOnUse" patternTransform="rotate(-28)">
  <path d="M0,15 Q15,0 30,15 T60,15" stroke="{BLACK}" stroke-width="7" fill="none"/></pattern>
"""

L = []  # collage layers, back to front


def slab(cx, cy, w, h, ang, fill, jit=7, extra=""):
    d = torn(rect(cx, cy, w, h, ang), jit)
    L.append(f'<path d="{d}" fill="{fill}" filter="url(#paper)" {extra}/>')
    return d


clip_id = [0]


def clipped(d, inner):
    clip_id[0] += 1
    cid = f"c{clip_id[0]}"
    L.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})" filter="url(#paper)">{inner}</g>')


# --- background collage ---------------------------------------------------
L.append(f'<circle cx="930" cy="250" r="190" fill="{PINK}" filter="url(#paper)"/>')
L.append(f'<circle cx="760" cy="80" r="120" fill="{ORANGE}" filter="url(#paper)"/>')
slab(820, 120, 900, 260, -28, PINK)
d = slab(980, 470, 360, 520, 62, CREAM)
clipped(d, halftone(700, 220, 1200, 760, 18, 13, 6.5, lambda u, v: 0.15 + 0.85 * u, BLACK))
slab(700, 330, 520, 120, -28, ORANGE)
d = slab(560, 140, 420, 150, 18, CREAM)
clipped(d, f'<rect x="300" y="0" width="560" height="320" fill="url(#check)" opacity="0.9"/>')
slab(1040, 700, 280, 560, 18, TEAL)
L.append(palm(860, 820, 330, -60, 24))
L.append(palm(900, 830, 280, -105, 22))
L.append(palm(880, 840, 250, -20, 20))
d = slab(820, 980, 560, 170, -28, YELLOW)
clipped(d, '<rect x="500" y="850" width="700" height="300" fill="url(#stripesK)" opacity="0.85"/>')
slab(1000, 1000, 240, 300, 62, ORANGE)
d = slab(760, 640, 250, 300, 18, PINK)
clipped(d, halftone(600, 470, 920, 820, 45, 11, 5.5, lambda u, v: v, BLACK))
d = slab(1060, 210, 220, 300, -28, CYAN)
clipped(d, '<rect x="900" y="40" width="320" height="360" fill="url(#wave)" opacity="0.8"/>')
L.append(f'<circle cx="840" cy="610" r="115" fill="none" stroke="#F6F2EA" stroke-width="4"/>')
d = slab(900, 1240, 520, 160, 18, PINK)
clipped(d, halftone(600, 1100, 1200, 1400, 18, 12, 6, lambda u, v: 0.2 + 0.8 * (1 - u), "#7A0F3E"))
L.append(citrus(1010, 1290, 220))
d = slab(700, 1350, 380, 120, -28, CREAM)
clipped(d, '<rect x="450" y="1250" width="500" height="200" fill="url(#dotsK)"/>')
slab(1080, 860, 70, 260, 18, BLACK, 4)
slab(640, 520, 50, 240, 62, BLACK, 4)
L.append(splatter(980, 120, 70, 140, BLACK, 5))
L.append(splatter(860, 1120, 60, 120, CREAM, 4))

# --- left black torn panel (keeps text legible) ---------------------------
panel = [(-40, 230), (300, 140), (520, 330), (650, 520), (610, 760), (680, 1000), (620, 1180), (660, 1450), (-40, 1450)]
pd = torn(panel, 9, 7)
L.append(f'<path d="{pd}" fill="{INK}"/>')
# halftone fade bleeding off the panel edge
L.append(halftone(560, 300, 760, 1300, 18, 12, 5.2, lambda u, v: max(0, 1 - u * 1.4), INK))
# left-edge colour strip like the mock
d = torn(rect(10, 760, 70, 620, 4), 8)
L.append(f'<path d="{d}" fill="{PINK}" filter="url(#paper)"/>')
d = torn(rect(4, 1090, 50, 260, -6), 8)
L.append(f'<path d="{d}" fill="{ORANGE}" filter="url(#paper)"/>')
L.append(halftone(0, 440, 120, 1200, 45, 10, 4.2, lambda u, v: max(0, 1 - u * 1.6) * 0.9, INK))
L.append(splatter(330, 230, 90, 160, PINK, 5))
L.append(splatter(560, 300, 50, 70, ORANGE, 4))

# --- logo ------------------------------------------------------------------
X0, LW = 78, 560
s1 = LW / (width_of("COLOURS", 1))
s2 = LW / (width_of("FOR HEALTH", 1))
y1 = 410 + s1 * 0.86
y2 = y1 + 16 + s2 * 0.86


def logo(fill, dx=0, dy=0, extra=""):
    return (f'<g transform="translate({dx},{dy})" {extra}>'
            f'<text x="{X0}" y="{f(y1)}" font-family="Anton" font-size="{f(s1)}" fill="{fill}">COLOURS</text>'
            f'<text x="{X0}" y="{f(y2)}" font-family="Anton" font-size="{f(s2)}" fill="{fill}">FOR HEALTH</text></g>')


logo_svg = (logo(CYAN, -5, 4, 'opacity="0.9" style="mix-blend-mode:screen"')
            + logo(PINK, 5, -3, 'opacity="0.95" style="mix-blend-mode:screen"')
            + logo("url(#foil)", 0, 0, 'filter="url(#foilTex)"'))

# colour bar — print registration strip, the brand's "colours" device
bar_y = y2 + 30
bar = ""
for i, c in enumerate([PINK, ORANGE, YELLOW, TEAL, CYAN, CREAM]):
    bar += f'<rect x="{X0 + i*30}" y="{f(bar_y)}" width="26" height="12" fill="{c}"/>'
bar += f'<line x1="{X0 + 190}" y1="{f(bar_y+6)}" x2="{X0+LW}" y2="{f(bar_y+6)}" stroke="#EDEAE4" stroke-width="1.5"/>'

ty = bar_y + 72
txt = f"""
<text class="cap" x="{X0}" y="{f(ty)}" font-size="30" font-weight="600" style="letter-spacing:0.2em">DAILY ESSENTIALS</text>
<text class="cap" x="{X0}" y="{f(ty+44)}" font-size="19" font-weight="400">NUTRITIONAL SUPPORT</text>
<text class="cap" x="{X0}" y="{f(ty+72)}" font-size="19" font-weight="400">FOR A MORE VIBRANT YOU</text>
<rect x="{X0}" y="{f(ty+110)}" width="40" height="4" fill="{PINK}"/>
<text x="{X0}" y="{f(ty+160)}" font-family="Mont" font-weight="700" font-size="28" style="letter-spacing:0.14em"><tspan fill="{ORANGE}">TROPICAL</tspan> <tspan fill="{PINK}">PUNCH</tspan></text>
<text class="cap" x="{X0}" y="{f(ty+192)}" font-size="16" font-weight="400">NATURALLY FLAVOURED</text>
"""
by = ty + 255
for i, (b, c) in enumerate([("ENERGY", ORANGE), ("IMMUNITY", PINK), ("FOCUS", TEAL), ("OVERALL WELLBEING", YELLOW)]):
    yy = by + i * 40
    txt += (f'<rect x="{X0+4}" y="{f(yy-15)}" width="16" height="16" fill="{c}"/>'
            f'<text class="cap" x="{X0+40}" y="{f(yy)}" font-size="17" font-weight="600">{b}<tspan font-size="10" dy="-7">1</tspan></text>')
fy = by + 200
txt += f"""
<line x1="{X0}" y1="{f(fy)}" x2="{X0+470}" y2="{f(fy)}" stroke="#EDEAE4" stroke-width="1.5"/>
<text class="cap" x="{X0}" y="{f(fy+48)}" font-size="20" font-weight="700">DAILY POWDER</text>
<text class="cap" x="{X0}" y="{f(fy+80)}" font-size="15" font-weight="400">FOOD SUPPLEMENT</text>
<text class="cap" x="{X0}" y="{f(fy+102)}" font-size="15" font-weight="400">WITH SWEETENER</text>
<line x1="{X0+300}" y1="{f(fy+24)}" x2="{X0+300}" y2="{f(fy+112)}" stroke="#EDEAE4" stroke-width="1.5"/>
<text class="cap" x="{X0+325}" y="{f(fy+58)}" font-size="34" font-weight="700" style="letter-spacing:0.06em">30</text>
<text class="cap" x="{X0+325}" y="{f(fy+80)}" font-size="14" font-weight="400">SERVINGS</text>
<text class="cap" x="{X0+325}" y="{f(fy+108)}" font-size="20" font-weight="600" style="letter-spacing:0.06em">300 g ℮</text>
"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{defs}</defs>
<rect width="{W}" height="{H}" fill="{INK}"/>
{''.join(L)}
{logo_svg}
{bar}
{txt}
</svg>"""
open(sys.argv[1], "w").write(svg)
print("text bottom", fy + 112)
