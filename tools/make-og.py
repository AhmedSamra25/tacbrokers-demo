#!/usr/bin/env python3
"""
Generate the TacBrokers social-sharing assets.

Outputs (relative to the repo root, one level up from this file):
    assets/og-image.png      1200x630  Open Graph / Twitter card
    assets/favicon-180.png     180x180  apple-touch-icon

Usage:
    pip install pillow
    python3 tools/make-og.py

The Manrope variable font is downloaded once into tools/fonts/ and cached.
If the download is unavailable the script falls back to a system sans-serif,
so it still runs offline (the wordmark just won't be set in Manrope).

Everything here is drawn from the brand tokens in assets/style.css.
"""

import os
import sys
import urllib.request

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required:  pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf"
FONT_FILE = os.path.join(FONT_DIR, "Manrope[wght].ttf")

# --- brand tokens ------------------------------------------------------------
NAVY = (0x00, 0x15, 0x41)
NAVY_MID = (0x00, 0x2a, 0x8f)
BLUE_DEEP = (0x00, 0x33, 0xb8)
BLUE_LIT = (0x01, 0x56, 0xf2)
BLUE_BRIGHT = (0x00, 0x68, 0xfc)
SKY = (0x8f, 0xbc, 0xff)          # light blue used for the "B" and "Brokers"
MIST = (0xc3, 0xd7, 0xff)         # tagline text

W, H = 1200, 630
CX = W // 2


# --- helpers -----------------------------------------------------------------
def load_font(size, weight=700):
    """Manrope at the requested weight, or a system fallback."""
    if not os.path.exists(FONT_FILE):
        os.makedirs(FONT_DIR, exist_ok=True)
        try:
            print("downloading Manrope ...")
            data = urllib.request.urlopen(FONT_URL, timeout=30).read()
            with open(FONT_FILE, "wb") as fh:
                fh.write(data)
        except Exception as exc:                       # offline: fall back
            print("  font download failed (%s), using a system font" % exc)
    if os.path.exists(FONT_FILE):
        font = ImageFont.truetype(FONT_FILE, size)
        try:
            font.set_variation_by_axes([weight])
        except Exception:
            pass
        return font
    for path in ("/System/Library/Fonts/Helvetica.ttc",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "C:/Windows/Fonts/segoeuib.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ramp(stops, t):
    """Multi-stop colour ramp. stops = [(pos, rgb), ...] sorted by pos."""
    if t <= stops[0][0]:
        return stops[0][1]
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            return lerp(c0, c1, (t - p0) / (p1 - p0))
    return stops[-1][1]


def gradient(size):
    """Navy -> blue, left to right with a slight downward tilt: the logo's
    move from the navy 'T' to the blue 'B'."""
    w, h = size
    stops = [(0.00, NAVY), (0.34, NAVY_MID), (0.62, BLUE_DEEP),
             (0.86, BLUE_LIT), (1.00, BLUE_BRIGHT)]
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / w) * 0.86 + (y / h) * 0.14      # tilt
            px[x, y] = ramp(stops, min(1.0, t))
    return img


def glow(img, centre, radius, colour, strength):
    """Soft radial light, drawn small and scaled up so it stays cheap."""
    s = 90
    layer = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(layer)
    for i in range(s // 2, 0, -1):
        t = i / (s / 2)
        d.ellipse([s / 2 - i, s / 2 - i, s / 2 + i, s / 2 + i],
                  fill=int(255 * strength * (1 - t) ** 2))
    layer = layer.resize((radius * 2, radius * 2), Image.BICUBIC)
    tint = Image.new("RGB", layer.size, colour)
    img.paste(tint, (centre[0] - radius, centre[1] - radius), layer)


def rounded(draw, box, r, fill=None, outline=None, width=2):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


# --- the eight service glyphs, drawn inside a 54x54 tile ----------------------
# Same family as the inline SVG icons on the page: 1.5-unit strokes on a 56 grid.
def glyph(d, i, x, y, s, col):
    """i = service index, (x, y) = tile top-left, s = tile size."""
    u = s / 56.0
    lw = max(2, round(3.1 * u))

    def p(a, b):
        return (x + a * u, y + b * u)

    def box(a, b, c, e):
        return [p(a, b), p(c, e)]

    if i == 0:                                   # trading - rising bars
        for bx, bh in ((17, 11), (25, 19), (33, 27)):
            d.rounded_rectangle(box(bx, 40 - bh, bx + 6, 40), radius=2 * u, fill=col)
    elif i == 1:                                 # gold - bullion bar
        pts = [p(17, 24), p(39, 24), p(44, 39), p(12, 39), p(17, 24)]
        d.line(pts, fill=col, width=lw, joint="curve")
        d.line([p(19, 31), p(37, 31)], fill=col, width=lw)
    elif i == 2:                                 # savings - a goal to hit
        d.ellipse(box(14, 14, 42, 42), outline=col, width=lw)
        d.ellipse(box(24, 24, 32, 32), fill=col)
    elif i == 3:                                 # gam3ia - a circle of members
        import math
        for k in range(6):
            a = math.radians(k * 60 - 90)
            cxp, cyp = 28 + 12 * math.cos(a), 28 + 12 * math.sin(a)
            r = 5.6 if k == 0 else 4.1
            d.ellipse(box(cxp - r, cyp - r, cxp + r, cyp + r), fill=col)
    elif i == 4:                                 # online payment - a bill
        d.rounded_rectangle(box(17, 13, 39, 43), radius=3 * u, outline=col, width=lw)
        d.rounded_rectangle(box(22, 22, 34, 25), radius=1.5 * u, fill=col)
        d.rounded_rectangle(box(22, 30, 30, 33), radius=1.5 * u, fill=col)
    elif i == 5:                                 # gateways - a card
        d.rounded_rectangle(box(11, 18, 45, 39), radius=4 * u, outline=col, width=lw)
        d.rectangle(box(11, 23, 45, 27), fill=col)
    elif i == 6:                                 # wallet
        d.rounded_rectangle(box(11, 17, 45, 39), radius=5 * u, outline=col, width=lw)
        d.ellipse(box(33, 25, 40, 32), fill=col)
    elif i == 7:                                 # payroll - a person
        d.ellipse(box(22, 13, 34, 25), outline=col, width=lw)
        d.arc(box(15, 29, 41, 53), start=180, end=360, fill=col, width=lw)


def tb_monogram(im, cx, cy, size, t_col, b_col):
    """The TB monogram, on the same 64-unit grid as assets/favicon.svg.
    Drawn through masks so the B keeps its two counters."""
    u = size / 64.0
    ox, oy = cx - size / 2, cy - size / 2

    def p(a, b):
        return (ox + a * u, oy + b * u)

    def box(a, b, c, e):
        return [p(a, b), p(c, e)]

    pad = 4
    mt = Image.new("L", (int(size) + pad * 2, int(size) + pad * 2), 0)
    mb = mt.copy()
    ox, oy = pad, pad                                    # masks are local space
    dt, db = ImageDraw.Draw(mt), ImageDraw.Draw(mb)

    # T
    dt.polygon([p(13, 18), p(33, 18), p(33, 24), p(26, 24),
                p(26, 46), p(20, 46), p(20, 24), p(13, 24)], fill=255)
    # B - stem, then a bowl and its counter, twice
    db.rectangle(box(38, 18, 44, 46), fill=255)
    for top in (18, 31):
        db.pieslice(box(36, top, 51, top + 15), start=-90, end=90, fill=255)
        db.rectangle(box(38, top, 43.5, top + 15), fill=255)
    for top in (22, 35):
        db.pieslice(box(40, top, 47, top + 7), start=-90, end=90, fill=0)
        db.rectangle(box(42, top, 43.5, top + 7), fill=0)

    at = (int(cx - size / 2) - pad, int(cy - size / 2) - pad)
    im.paste(Image.new("RGBA", mt.size, t_col), at, mt)
    im.paste(Image.new("RGBA", mb.size, b_col), at, mb)


# --- the card ----------------------------------------------------------------
def build_og():
    img = gradient((W, H))
    glow(img, (980, 120), 430, BLUE_BRIGHT, 0.55)
    glow(img, (120, 560), 380, NAVY, 0.45)
    img = img.convert("RGBA")

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # monogram in a soft tile - safe inside WhatsApp's square crop
    tile = 124
    rounded(d, [CX - tile / 2, 108, CX + tile / 2, 108 + tile], 30,
            fill=(255, 255, 255, 26), outline=(255, 255, 255, 64), width=2)
    tb_monogram(overlay, CX, 108 + tile / 2, 74, (255, 255, 255, 255), SKY + (255,))

    # wordmark: Tac in white, Brokers in sky blue
    f_word = load_font(92, 800)
    a, b = "Tac", "Brokers"
    wa, wb = f_word.getlength(a), f_word.getlength(b)
    x0 = CX - (wa + wb) / 2
    d.text((x0, 262), a, font=f_word, fill=(255, 255, 255, 255))
    d.text((x0 + wa, 262), b, font=f_word, fill=SKY + (255,))

    # tagline
    f_tag = load_font(33, 500)
    d.text((CX, 396), "One account to invest, save, get paid and pay",
           font=f_tag, fill=MIST + (255,), anchor="mm")

    # eight services along the bottom
    n, s, gap = 8, 54, 20
    total = n * s + (n - 1) * gap
    gx = CX - total / 2
    for i in range(n):
        x = gx + i * (s + gap)
        rounded(d, [x, 470, x + s, 470 + s], 15,
                fill=(255, 255, 255, 30), outline=(255, 255, 255, 56), width=1)
        glyph(d, i, x, 470, s, (255, 255, 255, 235))

    out = Image.alpha_composite(img, overlay).convert("RGB")
    path = os.path.join(ASSETS, "og-image.png")
    out.save(path, "PNG", optimize=True)

    # keep it well under WhatsApp's fetch ceiling
    if os.path.getsize(path) > 300 * 1024:
        out.convert("P", palette=Image.ADAPTIVE, colors=256).save(
            path, "PNG", optimize=True)
    print("assets/og-image.png  %d x %d  %.0f KB"
          % (W, H, os.path.getsize(path) / 1024))


def build_touch_icon():
    size = 180
    img = gradient((size, size))
    glow(img, (int(size * 0.78), int(size * 0.2)), 110, BLUE_BRIGHT, 0.5)
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    tb_monogram(overlay, size / 2, size / 2, 118, (255, 255, 255, 255), SKY + (255,))
    out = Image.alpha_composite(img, overlay).convert("RGB")
    path = os.path.join(ASSETS, "favicon-180.png")
    out.save(path, "PNG", optimize=True)
    print("assets/favicon-180.png  %d x %d  %.0f KB"
          % (size, size, os.path.getsize(path) / 1024))


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    build_og()
    build_touch_icon()
