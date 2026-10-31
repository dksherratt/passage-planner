"""Generate the Colours for Health pouch front-panel artwork as SVG."""
import base64, math, random, sys

random.seed(7)
W, H = 1100, 1400
FONTS = "/tmp/cfh/fonts"

PINK, ORANGE, TEAL, YELLOW, CYAN = "#FF2D8E", "#FF6A1A", "#0FA3A8", "#FFC81E", "#33D6F0"
PURPLE, LIME = "#8A4DE0", "#C6F23A"
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
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -9 6.6" result="speck"/>
  <feComposite in="SourceGraphic" in2="speck" operator="in" result="holes"/>
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="4" seed="9" result="m"/>
  <feColorMatrix in="m" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -22 15.6" result="blot"/>
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
<filter id="tear"><feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="3" seed="8"/><feDisplacementMap in="SourceGraphic" scale="9"/></filter>
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
<pattern id="ladder" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(-28)">
  <rect width="26" height="26" fill="{YELLOW}"/><rect width="26" height="9" fill="{BLACK}"/></pattern>
<pattern id="zebra" width="80" height="44" patternUnits="userSpaceOnUse" patternTransform="rotate(-20)">
  <path d="M0,11 C20,-4 40,26 80,11" stroke="{BLACK}" stroke-width="13" fill="none"/><path d="M0,33 C20,18 40,48 80,33" stroke="{BLACK}" stroke-width="13" fill="none"/></pattern>
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



def brush(x1, y1, x2, y2, w, color, n=38, op=1.0):
    """Dry-brush stroke: many bristle lines with ragged starts/ends."""
    L_ = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L_, (y2 - y1) / L_
    nx, ny = -uy, ux
    out = []
    for k in range(n):
        off = (k / (n - 1) - 0.5) * w
        a = random.uniform(0, 0.12) * L_
        b = L_ - random.uniform(0, 0.25) * L_
        if random.random() < 0.25:
            b = a + (b - a) * random.uniform(0.4, 0.9)
        pts = []
        for m in range(7):
            t = a + (b - a) * m / 6
            wob = math.sin(t / L_ * 3.1 + k) * w * 0.04
            pts.append((x1 + ux * t + nx * (off + wob), y1 + uy * t + ny * (off + wob)))
        sw = random.uniform(w / n * 0.8, w / n * 2.4)
        out.append(f'<path d="M' + " L".join(f"{f(px)},{f(py)}" for px, py in pts) +
                   f'" stroke-width="{f(sw)}" stroke-opacity="{f(random.uniform(0.55,1)*op)}"/>')
    return f'<g stroke="{color}" fill="none" stroke-linecap="round" filter="url(#rough)">' + "".join(out) + "</g>"


def blob(cx, cy, r, color):
    pts = [(cx + math.cos(t) * r * random.uniform(0.8, 1.15), cy + math.sin(t) * r * random.uniform(0.8, 1.15))
           for t in [2 * math.pi * k / 14 for k in range(14)]]
    return f'<path d="{torn(pts, r*0.06, 6)}" fill="{color}" filter="url(#rough)"/>' + splatter(cx, cy, r * 0.9, 60, color, r * 0.12)


def zigzag_pattern():
    return ""


# --- full-bleed collage --------------------------------------------------
L.append(f'<rect width="{W}" height="{H}" fill="{PINK}"/>')
L.append(halftone(0, 0, W, H, 18, 16, 4, lambda u, v: 0.5, "#E0187A"))
slab(330, 160, 900, 420, -28, YELLOW, 9)
d = torn([(c[0], c[1]) for c in [(170 + math.cos(t)*240, 190 + math.sin(t)*240) for t in [2*math.pi*k/48 for k in range(48)]]], 3, 8)
L.append(f'<path d="{d}" fill="{ORANGE}" filter="url(#paper)"/>')
clipped(d, halftone(-80, -60, 420, 440, 45, 34, 13, lambda u, v: 1, PINK))
L.append(brush(-20, 470, 640, 90, 120, BLACK, 50))
d = slab(920, 260, 430, 560, 18, CYAN)
clipped(d, '<rect x="680" y="0" width="480" height="560" fill="url(#wave)" opacity="0.35"/>')
L.append(f'<circle cx="980" cy="110" r="160" fill="{RED}" filter="url(#paper)"/>')
d = slab(760, 120, 330, 130, -28, YELLOW, 5)
clipped(d, '<rect x="560" y="0" width="420" height="260" fill="url(#ladder)"/>')
d = slab(720, 560, 420, 300, -28, CREAM)
clipped(d, halftone(480, 380, 960, 760, 18, 13, 6.5, lambda u, v: 0.1 + 0.9 * u, BLACK))
slab(1040, 720, 340, 560, 62, PURPLE)
slab(1020, 900, 300, 520, 18, TEAL)
L.append(palm(880, 980, 340, -62, 24))
L.append(palm(910, 990, 300, -110, 22))
L.append(palm(900, 1000, 260, -18, 20))
L.append(brush(700, 1080, 1120, 560, 70, YELLOW, 34, 0.95))
L.append(f'<circle cx="860" cy="430" r="130" fill="none" stroke="#F6F2EA" stroke-width="4"/>')
L.append(f'<rect x="980" y="560" width="96" height="96" fill="none" stroke="{BLACK}" stroke-width="3" transform="rotate(18 1028 608)"/>')
d = slab(200, 1300, 560, 260, -28, CREAM)
clipped(d, '<rect x="-100" y="1100" width="640" height="400" fill="url(#zebra)"/>')
L.append(brush(-30, 1380, 520, 1080, 90, LIME, 40))
d = slab(620, 1320, 520, 200, 18, ORANGE)
clipped(d, halftone(340, 1180, 900, 1460, 18, 12, 5.5, lambda u, v: 0.2 + 0.8 * v, "#B83A00"))
d = slab(690, 900, 200, 380, 62, YELLOW)
clipped(d, '<rect x="480" y="700" width="420" height="400" fill="url(#stripesK)" opacity="0.8"/>')
L.append(citrus(1010, 1300, 230))
L.append(blob(1060, 470, 46, BLACK))
L.append(splatter(1020, 470, 120, 160, BLACK, 5))
L.append(splatter(560, 140, 90, 120, CREAM, 4))
L.append(splatter(760, 1180, 80, 120, CREAM, 4))
L.append(splatter(40, 700, 120, 120, BLACK, 5))
# left edge strips peeking past the cards
d = slab(20, 820, 80, 520, 4, CYAN, 6)
clipped(d, halftone(-40, 540, 80, 1100, 45, 10, 4.5, lambda u, v: v, BLACK))

# --- pasted black cards for logo and copy ---------------------------------
def card(x0, y0, x1, y1):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    L.append(f'<path d="{torn(pts, 4, 6)}" fill="#000" opacity="0.35" transform="translate(7,9)" filter="url(#rough)"/>')
    L.append(f'<path d="{torn(pts, 2, 5)}" fill="{INK}" filter="url(#tear)"/>')

def tape(cx, cy, w, ang):
    L.append(f'<path d="{torn(rect(cx, cy, w, 34, ang), 2.5, 5)}" fill="#F1EBDD" opacity="0.78"/>')

card(44, 330, 690, 728)
card(44, 752, 590, 1340)
tape(80, 336, 120, -32); tape(660, 724, 110, -30); tape(560, 760, 100, 34)

X0, LW = 82, 570
s1 = LW / (width_of("COLOURS", 1))
s2 = LW / (width_of("FOR HEALTH", 1))
y1 = 372 + s1 * 0.86
y2 = y1 + 16 + s2 * 0.86

logo_svg = (f'<g filter="url(#foilTex)">'
            f'<text x="{X0}" y="{f(y1)}" font-family="Anton" font-size="{f(s1)}" fill="url(#foil)">COLOURS</text>'
            f'<text x="{X0}" y="{f(y2)}" font-family="Anton" font-size="{f(s2)}" fill="url(#foil)">FOR HEALTH</text></g>')

bar = ""
for i, c in enumerate([PINK, ORANGE, YELLOW, LIME, TEAL, CYAN, PURPLE]):
    bar += f'<rect x="{X0 + i*30}" y="790" width="26" height="12" fill="{c}"/>'
bar += f'<line x1="{X0 + 220}" y1="796" x2="550" y2="796" stroke="#EDEAE4" stroke-width="1.5"/>'

txt = f"""
<text class="cap" x="{X0}" y="852" font-size="29" font-weight="600" style="letter-spacing:0.2em">DAILY ESSENTIALS</text>
<text class="cap" x="{X0}" y="890" font-size="18" font-weight="400">NUTRITIONAL SUPPORT</text>
<text class="cap" x="{X0}" y="916" font-size="18" font-weight="400">FOR A MORE VIBRANT YOU</text>
<rect x="{X0}" y="944" width="40" height="4" fill="{PINK}"/>
<text x="{X0}" y="992" font-family="Mont" font-weight="700" font-size="27" style="letter-spacing:0.14em"><tspan fill="{ORANGE}">TROPICAL</tspan> <tspan fill="{PINK}">PUNCH</tspan></text>
<text class="cap" x="{X0}" y="1021" font-size="15" font-weight="400">NATURALLY FLAVOURED</text>
"""
for i, (b, c) in enumerate([("ENERGY", ORANGE), ("IMMUNITY", PINK), ("FOCUS", TEAL), ("OVERALL WELLBEING", YELLOW)]):
    yy = 1070 + i * 34
    txt += (f'<rect x="{X0+4}" y="{yy-14}" width="15" height="15" fill="{c}"/>'
            f'<text class="cap" x="{X0+38}" y="{yy}" font-size="16" font-weight="600">{b}<tspan font-size="10" dy="-7">1</tspan></text>')
txt += f"""
<line x1="{X0}" y1="1200" x2="550" y2="1200" stroke="#EDEAE4" stroke-width="1.5"/>
<text class="cap" x="{X0}" y="1243" font-size="19" font-weight="700">DAILY POWDER</text>
<text class="cap" x="{X0}" y="1272" font-size="14" font-weight="400">FOOD SUPPLEMENT</text>
<text class="cap" x="{X0}" y="1293" font-size="14" font-weight="400">WITH SWEETENER</text>
<line x1="{X0+290}" y1="1222" x2="{X0+290}" y2="1305" stroke="#EDEAE4" stroke-width="1.5"/>
<text class="cap" x="{X0+312}" y="1250" font-size="32" font-weight="700" style="letter-spacing:0.06em">30</text>
<text class="cap" x="{X0+312}" y="1271" font-size="13" font-weight="400">SERVINGS</text>
<text class="cap" x="{X0+312}" y="1300" font-size="19" font-weight="600" style="letter-spacing:0.06em">300 g ℮</text>
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

