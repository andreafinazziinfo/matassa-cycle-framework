"""Generate assets/banner.gif — an animated mock of the Matassa indicator.

GitHub's image proxy strips SVG animation, so the banner is a GIF. It renders a
scrolling candlestick chart with the dominant cycle wave (centratura), an FLD
line and min/max pivot labels — a stylised preview of the real indicator.
Rendered at 2x (supersampling) then downscaled and quantized for a small file.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 850, 280
SS = 2
FRAMES = 40
DURATION_MS = 80

# Chart loops seamlessly: scrolls exactly PERIOD candles over FRAMES frames,
# and the price series is periodic with that period.
PERIOD = 20            # candles per market cycle
SCROLL_CANDLES = PERIOD
SPACING = 15           # logical px between candles

OUT = Path(__file__).resolve().parents[1] / "assets" / "banner.gif"
FONTS = Path("C:/Windows/Fonts")

BG_TOP = (8, 11, 21)
BG_BOT = (12, 18, 36)
GRID = (23, 31, 51)
MINT = (9, 241, 184)
BLUE = (14, 165, 233)
VIOLET = (139, 92, 246)
UP = (34, 197, 94)
DOWN = (239, 68, 68)
TXT = (148, 163, 184)
DIM = (71, 85, 105)
WHITE = (236, 240, 248)


def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size * SS)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---- periodic price model (seamless loop) ----
def cycle(w: float) -> float:
    """Dominant market cycle (centratura wave)."""
    return math.sin(2 * math.pi * w / PERIOD)


def price(w: float) -> float:
    """Full price path: cycle + harmonics (all integer over PERIOD -> periodic)."""
    return (
        1.00 * math.sin(2 * math.pi * w / PERIOD)
        + 0.34 * math.sin(2 * math.pi * 2 * w / PERIOD + 0.6)
        + 0.16 * math.sin(2 * math.pi * 3 * w / PERIOD + 1.3)
        + 0.08 * math.sin(2 * math.pi * 5 * w / PERIOD + 2.1)
    )


def bg_gradient() -> Image.Image:
    img = Image.new("RGB", (W * SS, H * SS), BG_TOP)
    px = img.load()
    for y in range(H * SS):
        t = y / (H * SS)
        c = lerp(BG_TOP, BG_BOT, math.sin(t * math.pi) * 0.85)
        for x in range(W * SS):
            px[x, y] = c
    return img


def build_frame(f: int, bg: Image.Image, fonts: dict) -> Image.Image:
    img = bg.copy()
    d = ImageDraw.Draw(img)
    SSx = SS

    # geometry
    mid_y = int(H * 0.5) * SSx
    y_scale = 64 * SSx           # price units -> px
    sp = SPACING * SSx
    scroll = (f / FRAMES) * SCROLL_CANDLES * sp

    def sx(world_w: float) -> float:
        return world_w * sp - scroll + 40 * SSx

    def sy(p: float) -> float:
        return mid_y - p * y_scale

    # --- grid ---
    for gx in range(0, W * SSx, 30 * SSx):
        d.line([(gx, 0), (gx, H * SSx)], fill=GRID, width=1)
    for gy in range(0, H * SSx, 30 * SSx):
        d.line([(0, gy), (W * SSx, gy)], fill=GRID, width=1)

    # world range of candles that fall in view
    w0 = int((scroll - 60 * SSx) / sp)
    w1 = int((scroll + (W + 60) * SSx) / sp) + 1

    # --- glow layer (cycle wave + FLD) ---
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cyc_pts = [(sx(w), sy(cycle(w))) for w in [i * 0.25 for i in range(w0 * 4, w1 * 4)]]
    fld_pts = [(sx(w), sy(cycle(w - PERIOD / 2) * 0.92)) for w in [i * 0.25 for i in range(w0 * 4, w1 * 4)]]
    if len(cyc_pts) > 1:
        gd.line(cyc_pts, fill=(*MINT, 200), width=3 * SSx, joint="curve")
    if len(fld_pts) > 1:
        gd.line(fld_pts, fill=(*VIOLET, 150), width=2 * SSx, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(4 * SSx))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    # --- candlesticks ---
    body_w = int(sp * 0.55)
    for w in range(w0, w1):
        x = sx(w)
        if x < -sp or x > (W + sp) * SSx:
            continue
        o = price(w - 1)
        c = price(w)
        hi = max(o, c) + 0.14 + 0.05 * abs(math.sin(w * 1.7))
        lo = min(o, c) - 0.14 - 0.05 * abs(math.cos(w * 2.1))
        col = UP if c >= o else DOWN
        # wick
        d.line([(x, sy(hi)), (x, sy(lo))], fill=col, width=max(1, SSx))
        # body
        yo, yc = sy(o), sy(c)
        top, bot = min(yo, yc), max(yo, yc)
        if bot - top < 2 * SSx:
            bot = top + 2 * SSx
        d.rectangle([x - body_w / 2, top, x + body_w / 2, bot], fill=col)

    # sharp cycle line on top
    if len(cyc_pts) > 1:
        d.line(cyc_pts, fill=MINT, width=max(1, SSx), joint="curve")
    # dashed FLD (draw as short segments)
    for i in range(0, len(fld_pts) - 4, 8):
        seg = fld_pts[i:i + 4]
        if len(seg) > 1:
            d.line(seg, fill=VIOLET, width=max(1, SSx), joint="curve")

    # --- pivot markers + labels (peaks=max, troughs=min) ---
    label_f = fonts["pivot"]
    for w in range(w0, w1):
        m = w % PERIOD
        x = sx(w)
        if x < 20 * SSx or x > (W - 20) * SSx:
            continue
        if m == 5:  # peak -> max (red)
            y = sy(cycle(w))
            d.polygon([(x, y - 6 * SSx), (x - 5 * SSx, y - 14 * SSx), (x + 5 * SSx, y - 14 * SSx)], fill=DOWN)
            _chip(d, x, y - 30 * SSx, "T-1i", DOWN, label_f, SSx)
        elif m == 15:  # trough -> min (green)
            y = sy(cycle(w))
            d.polygon([(x, y + 6 * SSx), (x - 5 * SSx, y + 14 * SSx), (x + 5 * SSx, y + 14 * SSx)], fill=UP)
            _chip(d, x, y + 18 * SSx, "T+1", UP, label_f, SSx)
        elif m == 0:  # potential
            y = sy(cycle(w))
            d.ellipse([x - 3 * SSx, y - 3 * SSx, x + 3 * SSx, y + 3 * SSx], outline=BLUE, width=max(1, SSx))

    # --- top title bar (compact, lets the chart breathe) ---
    bar = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([0, 0, W * SSx, 40 * SSx], fill=(6, 9, 17, 205))
    bd.line([(0, 40 * SSx), (W * SSx, 40 * SSx)], fill=(*MINT, 90), width=SSx)
    img = Image.alpha_composite(img.convert("RGBA"), bar).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((20 * SSx, 11 * SSx), "MATASSA", font=fonts["brand"], fill=MINT)
    bx = 20 * SSx + int(d.textlength("MATASSA", font=fonts["brand"])) + 8 * SSx
    d.text((bx, 11 * SSx), "CYCLE FRAMEWORK", font=fonts["brand2"], fill=WHITE)
    # right side: legend
    legend = [("CICLO", MINT), ("FLD", VIOLET), ("PIVOT", UP)]
    lx = W * SSx - 20 * SSx
    for label, col in reversed(legend):
        tw = int(d.textlength(label, font=fonts["legend"]))
        lx -= tw
        d.text((lx, 14 * SSx), label, font=fonts["legend"], fill=col)
        lx -= 6 * SSx
        d.ellipse([lx - 8 * SSx, 16 * SSx, lx - 2 * SSx, 22 * SSx], fill=col)
        lx -= 18 * SSx

    # --- bottom strip ---
    bot = Image.new("RGBA", img.size, (0, 0, 0, 0))
    btd = ImageDraw.Draw(bot)
    btd.rectangle([0, (H - 26) * SSx, W * SSx, H * SSx], fill=(6, 9, 17, 205))
    img = Image.alpha_composite(img.convert("RGBA"), bot).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((20 * SSx, (H - 20) * SSx), "T-scale reference tables  ·  BTC 1H demo",
           font=fonts["foot"], fill=TXT)
    rtext = "Full suite @AnDr3HA · invite-only"
    d.text((W * SSx - 20 * SSx - int(d.textlength(rtext, font=fonts["foot"])), (H - 20) * SSx),
           rtext, font=fonts["foot"], fill=DIM)

    return img.resize((W, H), Image.LANCZOS)


def _chip(d: ImageDraw.ImageDraw, cx, cy, text, col, font, SSx):
    tw = int(d.textlength(text, font=font))
    d.rounded_rectangle([cx - tw / 2 - 4 * SSx, cy - 1 * SSx, cx + tw / 2 + 4 * SSx, cy + 14 * SSx],
                        radius=3 * SSx, fill=(6, 9, 17), outline=col, width=max(1, SSx))
    d.text((cx - tw / 2, cy + 1 * SSx), text, font=font, fill=col)


def main() -> None:
    fonts = {
        "brand": fnt("ariblk.ttf", 13),
        "brand2": fnt("arialbd.ttf", 13),
        "legend": fnt("consolab.ttf", 8),
        "pivot": fnt("consolab.ttf", 8),
        "foot": fnt("consola.ttf", 9),
    }
    bg = bg_gradient()
    frames = [build_frame(f, bg, fonts) for f in range(FRAMES)]
    pal = frames[0].convert("RGB").quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE)
    quant = [fr.convert("RGB").quantize(palette=pal, dither=Image.NONE) for fr in frames]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    quant[0].save(OUT, save_all=True, append_images=quant[1:], duration=DURATION_MS,
                  loop=0, optimize=True, disposal=2)
    print(f"Wrote {OUT} ({len(frames)} frames, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
