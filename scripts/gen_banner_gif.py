"""Generate assets/banner.gif — a Matassa-style indicator that draws itself.

GitHub strips SVG animation, so the banner is a GIF. The chart prints one candle
at a time (slow, readable), overlays the cycle wave (centratura) and the FLD
(azure), marks the true swing highs/lows with pivot labels, then projects the
next cycle forward with target boxes — mirroring the real indicator.

Rendered at 2x then downscaled (LANCZOS) and quantized for a small file.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 850, 280
SS = 2

N = 36                # solid candles (history)
PROJC = 12            # projected candles
BUILD_HOLD = 3        # frames between candles is implicit; we reveal 1/ frame
PROJ_FRAMES = 14      # frames to animate the projection
HOLD = 16             # frames holding the finished frame
FRAMES = N + PROJ_FRAMES + HOLD
DURATION_MS = 130     # slow, readable

PERIOD = 20.0         # candles per cycle  -> maxima at 5,25,45 ; minima at 15,35

OUT = Path(__file__).resolve().parents[1] / "assets" / "banner.gif"
FONTS = Path("C:/Windows/Fonts")

BG_TOP = (8, 11, 21)
BG_BOT = (12, 18, 36)
GRID = (23, 31, 51)
MINT = (9, 241, 184)
AZURE = (56, 189, 248)     # FLD
UP = (34, 197, 94)
DOWN = (239, 68, 68)
TXT = (148, 163, 184)
DIM = (71, 85, 105)
WHITE = (236, 240, 248)

PAD = 18
TOPBAR = 40
BOTBAR = 26
SPLIT = 0.70           # history | projection divider (fraction of width)


def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size * SS)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def trend(i: float) -> float:
    return 0.009 * i - 0.16


def cyc(i: float) -> float:
    return trend(i) + 0.92 * math.sin(2 * math.pi * i / PERIOD)


def fld(i: float) -> float:
    # cycle displaced half a period (classic FLD)
    return trend(i) + 0.92 * math.sin(2 * math.pi * (i - PERIOD / 2) / PERIOD)


def price(i: float) -> float:
    return (
        cyc(i)
        + 0.26 * math.sin(2 * math.pi * 2 * i / PERIOD + 0.6)
        + 0.13 * math.sin(2 * math.pi * 3 * i / PERIOD + 1.3)
        + 0.06 * math.sin(2 * math.pi * 5 * i / PERIOD + 2.1)
    )


def ohlc(i: int):
    o = price(i - 1)
    c = price(i)
    hi = max(o, c) + 0.10 + 0.05 * abs(math.sin(i * 1.7))
    lo = min(o, c) - 0.10 - 0.05 * abs(math.cos(i * 2.1))
    return o, c, hi, lo


def bg_gradient() -> Image.Image:
    img = Image.new("RGB", (W * SS, H * SS), BG_TOP)
    px = img.load()
    for y in range(H * SS):
        t = y / (H * SS)
        col = lerp(BG_TOP, BG_BOT, math.sin(t * math.pi) * 0.85)
        for x in range(W * SS):
            px[x, y] = col
    return img


def dashed(d, pts, fill, width, dash=4, gap=4):
    i = 0
    while i < len(pts) - 1:
        seg = pts[i:i + dash]
        if len(seg) > 1:
            d.line(seg, fill=fill, width=width, joint="curve")
        i += dash + gap


def build_frame(f: int, bg: Image.Image, fonts: dict) -> Image.Image:
    img = bg.copy()
    d = ImageDraw.Draw(img)

    # layout (in SS px)
    pad = PAD * SS
    top = (TOPBAR + 6) * SS
    bot = (H - BOTBAR - 6) * SS
    base_y = (top + bot) // 2
    y_scale = 42 * SS
    split_x = int(W * SPLIT) * SS
    spacing = (split_x - pad) / (N - 1)
    body_w = spacing * 0.55

    def sx(i: float) -> float:
        return pad + i * spacing

    def sy(v: float) -> float:
        return base_y - v * y_scale

    # reveal state
    if f < N:
        revealed = f + 1
        proj_t = 0.0
    else:
        revealed = N
        proj_t = min(1.0, (f - N) / PROJ_FRAMES)
    proj_revealed = int(proj_t * PROJC)

    # --- grid ---
    for gx in range(0, W * SS, 30 * SS):
        d.line([(gx, top - 6 * SS), (gx, bot + 6 * SS)], fill=GRID, width=1)
    for gy in range(top, bot, 30 * SS):
        d.line([(0, gy), (W * SS, gy)], fill=GRID, width=1)

    # projection zone tint + divider
    d.rectangle([split_x, top - 6 * SS, W * SS, bot + 6 * SS], fill=(10, 15, 30))
    dashed(d, [(split_x, y) for y in range(top, bot, 6 * SS)], fill=DIM, width=SS, dash=1, gap=1)

    # --- glow: cycle wave + FLD up to revealed ---
    last = revealed - 1 + (proj_t * PROJC)
    samples = [i * 0.2 for i in range(0, int(last * 5) + 1)]
    cyc_pts = [(sx(w), sy(cyc(w))) for w in samples]
    fld_pts = [(sx(w), sy(fld(w))) for w in samples]

    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    if len(cyc_pts) > 1:
        gd.line(cyc_pts, fill=(*MINT, 190), width=3 * SS, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(4 * SS))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    # --- candles (history) ---
    for i in range(revealed):
        x = sx(i)
        o, c, hi, lo = ohlc(i)
        col = UP if c >= o else DOWN
        d.line([(x, sy(hi)), (x, sy(lo))], fill=col, width=max(1, SS))
        yo, yc = sy(o), sy(c)
        a, b = min(yo, yc), max(yo, yc)
        if b - a < 2 * SS:
            b = a + 2 * SS
        d.rectangle([x - body_w / 2, a, x + body_w / 2, b], fill=col)

    # --- projected candles (faint, dashed look via outline) ---
    for j in range(proj_revealed):
        i = N + j
        x = sx(i)
        o, c, hi, lo = ohlc(i)
        col = UP if c >= o else DOWN
        d.line([(x, sy(hi)), (x, sy(lo))], fill=lerp((10, 15, 30), col, 0.45), width=max(1, SS))
        yo, yc = sy(o), sy(c)
        a, b = min(yo, yc), max(yo, yc)
        if b - a < 2 * SS:
            b = a + 2 * SS
        d.rectangle([x - body_w / 2, a, x + body_w / 2, b],
                    outline=col, width=max(1, SS))

    # --- cycle (solid mint) and FLD (azure) up to revealed ---
    split_idx = sum(1 for w in samples if w <= revealed - 1)
    if split_idx > 1:
        d.line(cyc_pts[:split_idx], fill=MINT, width=max(1, SS), joint="curve")
        dashed(d, fld_pts[:split_idx], fill=AZURE, width=max(1, SS), dash=5, gap=4)
    # projected continuation (dashed)
    if proj_revealed > 0 and len(cyc_pts) > split_idx:
        dashed(d, cyc_pts[split_idx:], fill=lerp(MINT, (10, 15, 30), 0.25), width=max(1, SS), dash=4, gap=4)
        dashed(d, fld_pts[split_idx:], fill=lerp(AZURE, (10, 15, 30), 0.25), width=max(1, SS), dash=4, gap=4)

    # --- pivots on TRUE swing highs/lows ---
    def place_pivots(upto_i: int, projected: bool):
        # maxima near k*PERIOD + PERIOD/4 ; minima near k*PERIOD + 3PERIOD/4
        for center, kind in _pivot_centers():
            if center > upto_i:
                continue
            if (center >= N) != projected:
                continue
            if kind == "max":
                # true local high in window
                win = [w for w in range(max(0, center - 2), min(N + PROJC, center + 3))]
                bi = max(win, key=lambda w: ohlc(w)[2])
                _, _, hi, _ = ohlc(bi)
                x, y = sx(bi), sy(hi)
                col = DOWN
                d.polygon([(x, y - 7 * SS), (x - 5 * SS, y - 15 * SS), (x + 5 * SS, y - 15 * SS)], fill=col)
                _chip(d, x, y - 31 * SS, "T-1i", col, fonts["pivot"])
            else:
                win = [w for w in range(max(0, center - 2), min(N + PROJC, center + 3))]
                bi = min(win, key=lambda w: ohlc(w)[3])
                _, _, _, lo = ohlc(bi)
                x, y = sx(bi), sy(lo)
                col = UP
                d.polygon([(x, y + 7 * SS), (x - 5 * SS, y + 15 * SS), (x + 5 * SS, y + 15 * SS)], fill=col)
                _chip(d, x, y + 19 * SS, "T+1", col, fonts["pivot"])

    place_pivots(revealed - 1, projected=False)

    # --- projection target boxes (appear with projection) ---
    if proj_revealed > 0:
        for center, kind in _pivot_centers():
            if center < N or center > N + proj_revealed:
                continue
            x = sx(center)
            if kind == "max":
                y = sy(cyc(center))
                _target(d, x, y, "T-1 H", DOWN, fonts["pivot"])
            else:
                y = sy(cyc(center))
                _target(d, x, y, "T+1 L", UP, fonts["pivot"])

    # --- top bar ---
    bar = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([0, 0, W * SS, TOPBAR * SS], fill=(6, 9, 17, 210))
    bd.line([(0, TOPBAR * SS), (W * SS, TOPBAR * SS)], fill=(*MINT, 90), width=SS)
    img = Image.alpha_composite(img.convert("RGBA"), bar).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((PAD * SS, 11 * SS), "MATASSA", font=fonts["brand"], fill=MINT)
    bx = PAD * SS + int(d.textlength("MATASSA", font=fonts["brand"])) + 8 * SS
    d.text((bx, 11 * SS), "CYCLE FRAMEWORK", font=fonts["brand2"], fill=WHITE)
    legend = [("CICLO", MINT), ("FLD", AZURE), ("PIVOT", UP), ("PROIEZIONE", DIM)]
    lx = W * SS - PAD * SS
    for label, col in reversed(legend):
        tw = int(d.textlength(label, font=fonts["legend"]))
        lx -= tw
        d.text((lx, 14 * SS), label, font=fonts["legend"], fill=col)
        lx -= 6 * SS
        d.ellipse([lx - 8 * SS, 16 * SS, lx - 2 * SS, 22 * SS], fill=col)
        lx -= 16 * SS

    # --- bottom bar ---
    bb = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bbd = ImageDraw.Draw(bb)
    bbd.rectangle([0, (H - BOTBAR) * SS, W * SS, H * SS], fill=(6, 9, 17, 210))
    img = Image.alpha_composite(img.convert("RGBA"), bb).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((PAD * SS, (H - 19) * SS), "T-scale reference tables  ·  BTC 1H demo",
           font=fonts["foot"], fill=TXT)
    rt = "Full suite @AnDr3HA · invite-only"
    d.text((W * SS - PAD * SS - int(d.textlength(rt, font=fonts["foot"])), (H - 19) * SS),
           rt, font=fonts["foot"], fill=DIM)

    return img.resize((W, H), Image.LANCZOS)


def _pivot_centers():
    out = []
    k = 0
    while True:
        mx = k * PERIOD + PERIOD / 4
        mn = k * PERIOD + 3 * PERIOD / 4
        if mx > N + PROJC and mn > N + PROJC:
            break
        out.append((int(round(mx)), "max"))
        out.append((int(round(mn)), "min"))
        k += 1
    return out


def _chip(d, cx, cy, text, col, font):
    tw = int(d.textlength(text, font=font))
    d.rounded_rectangle([cx - tw / 2 - 4 * SS, cy - 1 * SS, cx + tw / 2 + 4 * SS, cy + 14 * SS],
                        radius=3 * SS, fill=(6, 9, 17), outline=col, width=max(1, SS))
    d.text((cx - tw / 2, cy + 1 * SS), text, font=font, fill=col)


def _target(d, cx, cy, text, col, font):
    # hollow target box on the projection zone
    r = 6 * SS
    d.line([(cx - r, cy), (cx + r, cy)], fill=col, width=SS)
    d.line([(cx, cy - r), (cx, cy + r)], fill=col, width=SS)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(1, SS))
    _chip(d, cx, cy - 24 * SS if col == DOWN else cy + 12 * SS, text, col, font)


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
    pal = frames[-1].convert("RGB").quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE)
    quant = [fr.convert("RGB").quantize(palette=pal, dither=Image.NONE) for fr in frames]

    # slower at the end: longer hold on the final composed frame
    durations = [DURATION_MS] * FRAMES
    for i in range(FRAMES - HOLD, FRAMES):
        durations[i] = 90
    durations[-1] = 1400  # pause before loop restart

    OUT.parent.mkdir(parents=True, exist_ok=True)
    quant[0].save(OUT, save_all=True, append_images=quant[1:], duration=durations,
                  loop=0, optimize=True, disposal=2)
    print(f"Wrote {OUT} ({len(frames)} frames, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
