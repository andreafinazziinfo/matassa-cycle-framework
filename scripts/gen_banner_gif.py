"""Generate assets/banner.gif — Matassa-style chart that draws itself.

- Large white intro title with cyan star sparkles, then persistent top title
- One candle every few frames (slow)
- FLD in bright cyan
- Projection zone: dashed lines only (no hollow candles)
- T-scale reference table panel (like TradingView screenshots)
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 460
SS = 2

N = 32
PROJC = 10
TITLE_INTRO = 14
CANDLE_FRAMES = 4
PROJ_FRAMES = 18
HOLD = 14
FRAMES = TITLE_INTRO + N * CANDLE_FRAMES + PROJ_FRAMES + HOLD
DURATION_MS = 200

PERIOD = 20.0

ASSETS = Path(__file__).resolve().parents[1] / "assets"
OUT = ASSETS / "matassa-banner.gif"  # unique name — GitHub ignores ?v= on gif cache
FONTS = Path("C:/Windows/Fonts")

BG_TOP = (8, 11, 21)
BG_BOT = (12, 18, 36)
GRID = (23, 31, 51)
MINT = (9, 241, 184)
CYAN = (0, 229, 255)       # FLD — bright cyan
VIOLET = (139, 92, 246)
UP = (34, 197, 94)
DOWN = (239, 68, 68)
TXT = (148, 163, 184)
DIM = (71, 85, 105)
WHITE = (236, 240, 248)
TABLE_HDR = (15, 23, 42)
TABLE_ROW = (11, 17, 32)
TABLE_ALT = (14, 21, 38)

PAD = 18
TOPBAR = 68
BOTBAR = 28
TABLE_W = 300
SPLIT = 0.54

# Compact rows from m-1-0x (Ciclo | CRYPTO)
TABLE_ROWS = [
    ("T+2", "45g 12h"),
    ("T+1", "22g 18h"),
    ("T", "11g 9h"),
    ("T-1", "5g 16h"),
    ("T-2", "2g 20h"),
    ("T-3", "1g 10h"),
]


def fnt(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size * SS)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def trend(i: float) -> float:
    return 0.009 * i - 0.16


def cyc(i: float) -> float:
    return trend(i) + 0.92 * math.sin(2 * math.pi * i / PERIOD)


def fld(i: float) -> float:
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


def dashed(d, pts, fill, width, dash=5, gap=4):
    i = 0
    while i < len(pts) - 1:
        seg = pts[i : i + dash]
        if len(seg) > 1:
            d.line(seg, fill=fill, width=width, joint="curve")
        i += dash + gap


# Star offsets relative to title bbox (fx, fy, base_radius px @ 1x)
_TITLE_STARS = [
    (-0.12, -0.55, 2.2),
    (1.08, -0.42, 1.8),
    (-0.08, 1.15, 1.6),
    (1.12, 0.95, 2.0),
    (0.42, -0.72, 1.4),
    (0.78, 1.22, 1.5),
    (-0.22, 0.35, 1.2),
    (1.02, 0.18, 1.3),
]


def _draw_star(d, cx: float, cy: float, r: float, bright: float):
    """Small cyan sparkle (dot + cross)."""
    col = lerp(CYAN, WHITE, min(1.0, bright))
    ri = max(1, int(r * SS))
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=col)
    if bright > 0.65:
        arm = ri + SS
        d.line([(cx - arm, cy), (cx + arm, cy)], fill=col, width=max(1, SS))
        d.line([(cx, cy - arm), (cx, cy + arm)], fill=col, width=max(1, SS))


def _cyan_stars(d, box, frame: int):
    x0, y0, x1, y1 = box
    tw, th = max(1, x1 - x0), max(1, y1 - y0)
    for i, (fx, fy, br) in enumerate(_TITLE_STARS):
        pulse = 0.45 + 0.55 * math.sin(frame * 0.28 + i * 1.9)
        sx = x0 + fx * tw
        sy = y0 + fy * th
        _draw_star(d, sx, sy, br * (0.75 + 0.35 * pulse), pulse)


def _white_title(img: Image.Image, xy, text, font, frame: int = 0) -> Image.Image:
    """Crisp white title with twinkling cyan star dots."""
    d = ImageDraw.Draw(img)
    box = d.textbbox(xy, text, font=font)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text((xy[0] + dx * SS, xy[1] + dy * SS), text, font=font, fill=(0, 0, 0))
    d.text(xy, text, font=font, fill=WHITE)
    _cyan_stars(d, box, frame)
    return img


def _draw_table(d, box, fonts, alpha: float = 1.0):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=5 * SS, fill=TABLE_HDR, outline=lerp(DIM, MINT, 0.4 * alpha), width=max(1, SS))
    pad_x = x0 + 14 * SS
    y = y0 + 14 * SS
    d.text((pad_x, y), "T-SCALE", font=fonts["tbl_title"], fill=MINT)
    y += 26 * SS
    d.text((pad_x, y), "m-1-0x · CRYPTO", font=fonts["tbl_sub"], fill=TXT)
    y += 24 * SS
    d.line([(x0 + 10 * SS, y), (x1 - 10 * SS, y)], fill=GRID, width=SS)
    y += 14 * SS

    col_w = (x1 - x0 - 28 * SS) / 2
    d.text((pad_x, y), "Ciclo", font=fonts["tbl_hdr"], fill=WHITE)
    d.text((pad_x + col_w, y), "Durata", font=fonts["tbl_hdr"], fill=CYAN)
    y += 22 * SS

    row_h = 26 * SS
    for i, (ciclo, dur) in enumerate(TABLE_ROWS):
        bg = TABLE_ALT if i % 2 else TABLE_ROW
        d.rectangle([x0 + 8 * SS, y - 3 * SS, x1 - 8 * SS, y + row_h - 4 * SS], fill=bg)
        d.text((pad_x, y), ciclo, font=fonts["tbl_cell"], fill=WHITE if ciclo == "T" else TXT)
        d.text((pad_x + col_w, y), dur, font=fonts["tbl_cell"], fill=CYAN if ciclo == "T" else WHITE)
        y += row_h


def _chip(d, cx, cy, text, col, font):
    tw = int(d.textlength(text, font=font))
    d.rounded_rectangle(
        [cx - tw / 2 - 4 * SS, cy - 1 * SS, cx + tw / 2 + 4 * SS, cy + 14 * SS],
        radius=3 * SS,
        fill=(6, 9, 17),
        outline=col,
        width=max(1, SS),
    )
    d.text((cx - tw / 2, cy + 1 * SS), text, font=font, fill=col)


def _target(d, cx, cy, text, col, font):
    r = 6 * SS
    d.line([(cx - r, cy), (cx + r, cy)], fill=col, width=SS)
    d.line([(cx, cy - r), (cx, cy + r)], fill=col, width=SS)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=max(1, SS))
    _chip(d, cx, cy - 24 * SS if col == DOWN else cy + 12 * SS, text, col, font)


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


def _intro_frame(f: int, bg: Image.Image, fonts: dict) -> Image.Image:
    img = bg.copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * SS, H * SS], fill=(5, 8, 16))
    line1 = "MATASSA"
    line2 = "CYCLE FRAMEWORK"
    f1, f2 = fonts["intro_l1"], fonts["intro_l2"]
    w1 = int(d.textlength(line1, font=f1))
    w2 = int(d.textlength(line2, font=f2))
    cx = W * SS // 2
    cy = H * SS // 2 - 24 * SS
    img = _white_title(img, (cx - w1 // 2, cy - 44 * SS), line1, f1, f)
    img = _white_title(img, (cx - w2 // 2, cy + 8 * SS), line2, f2, f + 3)
    d = ImageDraw.Draw(img)
    sub = "T-scale reference · cyclical analysis"
    sw = int(d.textlength(sub, font=fonts["intro_sub"]))
    d.text((cx - sw // 2, cy + 62 * SS), sub, font=fonts["intro_sub"], fill=TXT)
    _cyan_stars(d, (cx - w1 // 2 - 30 * SS, cy - 60 * SS, cx + w1 // 2 + 30 * SS, cy + 80 * SS), f + 5)
    return img.resize((W, H), Image.LANCZOS)


def build_frame(f: int, bg: Image.Image, fonts: dict) -> Image.Image:
    if f < TITLE_INTRO:
        return _intro_frame(f, bg, fonts)

    cf = f - TITLE_INTRO
    img = bg.copy()
    d = ImageDraw.Draw(img)

    pad = PAD * SS
    top = (TOPBAR + 4) * SS
    bot = (H - BOTBAR - 4) * SS
    base_y = (top + bot) // 2
    y_scale = 48 * SS
    chart_right = int((W - TABLE_W - 8) * SPLIT) * SS
    split_x = chart_right
    table_x0 = (W - TABLE_W - 6) * SS
    spacing = (split_x - pad) / max(1, N - 1)
    body_w = spacing * 0.55

    def sx(i: float) -> float:
        return pad + i * spacing

    def sy(v: float) -> float:
        return base_y - v * y_scale

    if cf < N * CANDLE_FRAMES:
        revealed = cf // CANDLE_FRAMES + 1
        proj_t = 0.0
    else:
        revealed = N
        proj_t = min(1.0, (cf - N * CANDLE_FRAMES) / PROJ_FRAMES)
    proj_revealed = int(proj_t * PROJC)

    # grid
    for gx in range(0, int(split_x), 28 * SS):
        d.line([(gx, top - 4 * SS), (gx, bot + 4 * SS)], fill=GRID, width=1)
    for gy in range(top, bot, 28 * SS):
        d.line([(pad, gy), (split_x, gy)], fill=GRID, width=1)

    # projection zone
    d.rectangle([split_x, top - 4 * SS, table_x0 - 4 * SS, bot + 4 * SS], fill=(8, 12, 24))
    dashed(
        d,
        [(split_x, y) for y in range(top, bot, 5 * SS)],
        fill=DIM,
        width=SS,
        dash=1,
        gap=1,
    )

    last_i = revealed - 1 + proj_t * PROJC
    samples = [i * 0.2 for i in range(0, int(last_i * 5) + 2)]
    cyc_pts = [(sx(w), sy(cyc(w))) for w in samples]
    fld_pts = [(sx(w), sy(fld(w))) for w in samples]
    price_pts = [(sx(w), sy(price(w))) for w in samples]

    # glow cycle + FLD
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    if len(cyc_pts) > 1:
        gd.line(cyc_pts, fill=(*MINT, 200), width=3 * SS, joint="curve")
    if len(fld_pts) > 1:
        gd.line(fld_pts, fill=(*CYAN, 180), width=2 * SS, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(3 * SS))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    # history candles
    for i in range(min(revealed, N)):
        x = sx(i)
        o, c, hi, lo = ohlc(i)
        col = UP if c >= o else DOWN
        d.line([(x, sy(hi)), (x, sy(lo))], fill=col, width=max(1, SS))
        yo, yc = sy(o), sy(c)
        a, b = min(yo, yc), max(yo, yc)
        if b - a < 2 * SS:
            b = a + 2 * SS
        d.rectangle([x - body_w / 2, a, x + body_w / 2, b], fill=col)

    # cycle + FLD (history)
    hist_end = min(len(samples), sum(1 for w in samples if w <= revealed - 1))
    if hist_end > 1:
        d.line(cyc_pts[:hist_end], fill=MINT, width=max(2, SS), joint="curve")
        dashed(d, fld_pts[:hist_end], fill=CYAN, width=max(2, SS), dash=6, gap=3)

    # projection: solid white path (full line, clearly distinct)
    if proj_revealed > 0:
        p_start = max(0, hist_end - 1)
        if len(price_pts) > p_start + 1:
            d.line(
                price_pts[p_start:],
                fill=WHITE,
                width=max(3, SS),
                joint="curve",
            )

    def place_pivots(upto_i: int, projected: bool):
        for center, kind in _pivot_centers():
            if center > upto_i:
                continue
            if (center >= N) != projected:
                continue
            if kind == "max":
                win = range(max(0, center - 2), min(N + PROJC, center + 3))
                bi = max(win, key=lambda w: ohlc(w)[2])
                _, _, hi, _ = ohlc(bi)
                x, y = sx(bi), sy(hi)
                col = DOWN
                d.polygon(
                    [(x, y - 7 * SS), (x - 5 * SS, y - 15 * SS), (x + 5 * SS, y - 15 * SS)],
                    fill=col,
                )
                _chip(d, x, y - 31 * SS, "T-1i", col, fonts["pivot"])
            else:
                win = range(max(0, center - 2), min(N + PROJC, center + 3))
                bi = min(win, key=lambda w: ohlc(w)[3])
                _, _, _, lo = ohlc(bi)
                x, y = sx(bi), sy(lo)
                col = UP
                d.polygon(
                    [(x, y + 7 * SS), (x - 5 * SS, y + 15 * SS), (x + 5 * SS, y + 15 * SS)],
                    fill=col,
                )
                _chip(d, x, y + 19 * SS, "T+1", col, fonts["pivot"])

    place_pivots(revealed - 1, projected=False)

    if proj_revealed > 0:
        for center, kind in _pivot_centers():
            if center < N or center > N + proj_revealed - 1:
                continue
            x = sx(center)
            y = sy(cyc(center))
            if kind == "max":
                _target(d, x, y, "T-1 H", DOWN, fonts["pivot"])
            else:
                _target(d, x, y, "T+1 L", UP, fonts["pivot"])

    # reference table (right panel)
    tbl_alpha = min(1.0, revealed / 8)
    _draw_table(
        d,
        (table_x0, top - 2 * SS, W * SS - pad, bot + 2 * SS),
        fonts,
        tbl_alpha,
    )

    # top bar + title (always visible during chart)
    bar = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rectangle([0, 0, W * SS, TOPBAR * SS], fill=(4, 7, 14, 235))
    bd.line([(0, TOPBAR * SS), (W * SS, TOPBAR * SS)], fill=(*MINT, 100), width=SS)
    img = Image.alpha_composite(img.convert("RGBA"), bar).convert("RGB")
    img = _white_title(
        img,
        (PAD * SS, 12 * SS),
        "MATASSA CYCLE FRAMEWORK",
        fonts["title_bar"],
        f,
    )

    d = ImageDraw.Draw(img)
    legend = [("CICLO", MINT), ("FLD", CYAN), ("PIVOT", UP), ("PROIEZ.", WHITE)]
    lx = table_x0 - 14 * SS
    for label, col in reversed(legend):
        tw = int(d.textlength(label, font=fonts["legend"]))
        lx -= tw
        d.text((lx, 26 * SS), label, font=fonts["legend"], fill=col)
        lx -= 8 * SS
        d.ellipse([lx - 9 * SS, 28 * SS, lx - 2 * SS, 35 * SS], fill=col)
        lx -= 16 * SS

    bb = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bbd = ImageDraw.Draw(bb)
    bbd.rectangle([0, (H - BOTBAR) * SS, W * SS, H * SS], fill=(4, 7, 14, 230))
    img = Image.alpha_composite(img.convert("RGBA"), bb).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text(
        (PAD * SS, (H - 20) * SS),
        "reference-tables/m-1-0x.csv  ·  BTC 1H demo",
        font=fonts["foot"],
        fill=TXT,
    )
    rt = "@AnDr3HA · invite-only"
    d.text(
        (W * SS - PAD * SS - int(d.textlength(rt, font=fonts["foot"])), (H - 20) * SS),
        rt,
        font=fonts["foot"],
        fill=DIM,
    )

    return img.resize((W, H), Image.LANCZOS)


def main() -> None:
    fonts = {
        "intro_l1": fnt("ariblk.ttf", 46),
        "intro_l2": fnt("ariblk.ttf", 30),
        "intro_sub": fnt("consola.ttf", 14),
        "title_bar": fnt("ariblk.ttf", 28),
        "legend": fnt("consolab.ttf", 11),
        "pivot": fnt("consolab.ttf", 11),
        "foot": fnt("consola.ttf", 12),
        "tbl_title": fnt("arialbd.ttf", 17),
        "tbl_sub": fnt("consolab.ttf", 12),
        "tbl_hdr": fnt("consolab.ttf", 13),
        "tbl_cell": fnt("consolab.ttf", 13),
    }
    bg = bg_gradient()
    frames = [build_frame(f, bg, fonts) for f in range(FRAMES)]

    pal = frames[-1].convert("RGB").quantize(colors=160, method=Image.MEDIANCUT, dither=Image.NONE)
    quant = [fr.convert("RGB").quantize(palette=pal, dither=Image.NONE) for fr in frames]

    durations = [DURATION_MS] * FRAMES
    for i in range(TITLE_INTRO):
        durations[i] = 220
    durations[-1] = 1600

    OUT.parent.mkdir(parents=True, exist_ok=True)
    quant[0].save(
        OUT,
        save_all=True,
        append_images=quant[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    # Legacy path: some links may still point here
    legacy = ASSETS / "banner.gif"
    legacy.write_bytes(OUT.read_bytes())
    print(f"Wrote {OUT} ({len(frames)} frames, {OUT.stat().st_size / 1024:.0f} KB)")
    print(f"Synced {legacy}")


if __name__ == "__main__":
    main()
