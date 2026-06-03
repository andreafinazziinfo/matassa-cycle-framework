"""Generate assets/banner.gif for the README.

GitHub's image proxy strips SVG CSS/SMIL animation, so the animated banner is a
GIF. Rendered at 2x with supersampling + glow, then downscaled (LANCZOS) and
quantized to a shared adaptive palette to keep the file small.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Logical canvas; rendered at SS x then downscaled for crisp antialiasing.
W, H = 850, 280
SS = 2
FRAMES = 36
DURATION_MS = 70

OUT = Path(__file__).resolve().parents[1] / "assets" / "banner.gif"
FONTS = Path("C:/Windows/Fonts")

# Palette (matches GitHub profile brand)
BG_TOP = (7, 10, 19)
BG_BOT = (11, 17, 34)
GRID = (24, 33, 54)
MINT = (9, 241, 184)
BLUE = (14, 165, 233)
VIOLET = (139, 92, 246)
RED = (239, 68, 68)
AMBER = (234, 179, 8)
GREEN = (34, 197, 94)
TXT = (148, 163, 184)
TXT_DIM = (71, 85, 105)
WHITE = (236, 240, 248)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size * SS)


def s(v: int) -> int:
    return v * SS


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def bg_gradient() -> Image.Image:
    base = Image.new("RGB", (W * SS, H * SS), BG_TOP)
    px = base.load()
    for y in range(H * SS):
        t = y / (H * SS)
        # darker at edges, slightly lit center band
        c = lerp(BG_TOP, BG_BOT, math.sin(t * math.pi) * 0.9)
        for x in range(W * SS):
            px[x, y] = c
    return base


def wave_points(phase: float, base_y: int, amp: float, freq: float, x0: int, x1: int, step: int):
    pts = []
    for x in range(x0, x1, step):
        t = x / (W * SS) * freq * math.pi + phase
        y = base_y + amp * math.sin(t) + amp * 0.45 * math.sin(t * 2.3 + 0.6)
        pts.append((x, int(y)))
    return pts


def build_frame(f: int, bg: Image.Image, fonts: dict) -> Image.Image:
    img = bg.copy()
    phase = f / FRAMES * 2 * math.pi  # seamless loop

    # --- grid ---
    grid = ImageDraw.Draw(img)
    g = 30 * SS
    for x in range(0, W * SS, g):
        grid.line([(x, 0), (x, H * SS)], fill=GRID, width=1)
    for y in range(0, H * SS, g):
        grid.line([(0, y), (W * SS, y)], fill=GRID, width=1)

    # --- glow layer (wave + markers) ---
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    base_y = int(H * SS * 0.62)
    amp = 26 * SS
    main = wave_points(phase, base_y, amp, 4.0, -40 * SS, (W + 40) * SS, 4 * SS)
    back = wave_points(phase * 0.6 + 1.5, base_y + 14 * SS, amp * 0.7, 3.2, -40 * SS, (W + 40) * SS, 5 * SS)

    gd.line(back, fill=(*VIOLET, 150), width=2 * SS, joint="curve")
    gd.line(main, fill=(*MINT, 220), width=3 * SS, joint="curve")

    # cycle markers travelling along the wave (pivots)
    n = len(main)
    for k in range(5):
        idx = int((f / FRAMES + k / 5) % 1.0 * n)
        cx, cy = main[idx]
        col = MINT if k % 2 == 0 else BLUE
        r = 5 * SS
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*col, 255))

    glow = glow.filter(ImageFilter.GaussianBlur(5 * SS))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    d = ImageDraw.Draw(img)
    # sharp wave on top of glow
    d.line(main, fill=BLUE, width=1 * SS, joint="curve")
    for k in range(5):
        idx = int((f / FRAMES + k / 5) % 1.0 * n)
        cx, cy = main[idx]
        col = MINT if k % 2 == 0 else BLUE
        r = 3 * SS
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=WHITE, width=1)

    # ============ LEFT: terminal panel ============
    panel = (s(34), s(46), s(372), s(234))
    d.rounded_rectangle(panel, radius=s(8), fill=(4, 6, 13), outline=GRID, width=SS)
    d.ellipse([s(52) - s(4), s(64) - s(4), s(52) + s(4), s(64) + s(4)], fill=RED)
    d.ellipse([s(66) - s(4), s(64) - s(4), s(66) + s(4), s(64) + s(4)], fill=AMBER)
    d.ellipse([s(80) - s(4), s(64) - s(4), s(80) + s(4), s(64) + s(4)], fill=GREEN)
    d.text((s(98), s(58), ), "MATASSA://REFERENCE_TABLES", font=fonts["hdr"], fill=TXT_DIM)
    d.line([(s(46), s(78)), (s(360), s(78))], fill=GRID, width=SS)

    mono = fonts["mono"]
    lines = [
        [("matassa@cycle", VIOLET), (":", TXT), ("~/tables", BLUE), ("$ load m-1-0x.csv", TXT)],
        [("[", TXT), ("OK", MINT), ("] Profile M (1.0x) - 6 markets", TXT)],
        [("[", TXT), ("OK", MINT), ("] T-scale T .. T+10 mapped", TXT)],
        [("[", TXT), ("INF", VIOLET), ("] Crypto 100% | US 19.3%", TXT)],
        [("[", TXT), ("INF", VIOLET), ("] Pine private | TV invite", TXT)],
        [("[", TXT), ("SYS", BLUE), ("] Public: CSV + XLSX", TXT)],
    ]
    y = s(96)
    for segs in lines:
        x = s(52)
        for text, col in segs:
            d.text((x, y), text, font=mono, fill=col)
            x += int(d.textlength(text, font=mono))
        y += s(21)
    # prompt + blinking cursor
    x = s(52)
    for text, col in [("matassa@cycle", VIOLET), (":", TXT), ("~/tables", BLUE), ("$ status ", WHITE)]:
        d.text((x, y), text, font=mono, fill=col)
        x += int(d.textlength(text, font=mono))
    if f % 12 < 7:
        d.rectangle([x, y + s(2), x + s(7), y + s(13)], fill=MINT)

    # ============ RIGHT: title block ============
    rx = s(420)
    # status badge with pulsing dot
    bx, by = s(622), s(54)
    d.rounded_rectangle([bx, by - s(11), bx + s(150), by + s(11)], radius=s(11),
                        fill=(11, 23, 22), outline=MINT, width=1)
    pr = s(4) + (s(2) if f % 18 < 9 else 0)
    d.ellipse([bx + s(16) - pr, by - pr, bx + s(16) + pr, by + pr], fill=MINT)
    d.text((bx + s(28), by - s(7)), "REFERENCE LIVE", font=fonts["badge"], fill=MINT)

    # glowing title
    tglow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tg = ImageDraw.Draw(tglow)
    tg.text((rx, s(80)), "MATASSA CYCLE", font=fonts["title"], fill=(*MINT, 110))
    tg.text((rx, s(120)), "FRAMEWORK", font=fonts["title"], fill=(*MINT, 110))
    tglow = tglow.filter(ImageFilter.GaussianBlur(4 * SS))
    img = Image.alpha_composite(img.convert("RGBA"), tglow).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((rx, s(80)), "MATASSA CYCLE", font=fonts["title"], fill=WHITE)
    d.text((rx, s(120)), "FRAMEWORK", font=fonts["title"], fill=WHITE)
    d.text((rx, s(164)), "T-SCALE DURATIONS  /  CROSS-MARKET CALIBRATION", font=fonts["sub"], fill=MINT)

    # chips
    chips = [("MIN - M - MAX", MINT), ("T .. T+10", VIOLET), ("@AnDr3HA  TV", TXT)]
    cx = rx
    for label, col in chips:
        w = int(d.textlength(label, font=fonts["chip"])) + s(24)
        d.rounded_rectangle([cx, s(190), cx + w, s(216)], radius=s(5), fill=(7, 12, 20), outline=GRID, width=1)
        d.text((cx + s(12), s(196)), label, font=fonts["chip"], fill=col)
        cx += w + s(10)

    return img.resize((W, H), Image.LANCZOS)


def main() -> None:
    fonts = {
        "title": font("ariblk.ttf", 26),
        "sub": font("consolab.ttf", 10),
        "mono": font("consola.ttf", 10),
        "hdr": font("consolab.ttf", 8),
        "badge": font("consolab.ttf", 8),
        "chip": font("arialbd.ttf", 10),
    }
    bg = bg_gradient()
    frames = [build_frame(f, bg, fonts) for f in range(FRAMES)]

    # shared adaptive palette across all frames -> smaller, consistent GIF
    pal_src = frames[0].convert("RGB").quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE)
    quant = [fr.convert("RGB").quantize(palette=pal_src, dither=Image.NONE) for fr in frames]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    quant[0].save(OUT, save_all=True, append_images=quant[1:], duration=DURATION_MS,
                  loop=0, optimize=True, disposal=2)
    size_kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT} ({len(frames)} frames, {size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
