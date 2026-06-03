"""Generate assets/banner.gif for GitHub README (animations work; SVG CSS often stripped)."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 850, 200
FRAMES = 24
OUT = Path(__file__).resolve().parents[1] / "assets" / "banner.gif"


def main() -> None:
    frames: list[Image.Image] = []
    wave_y = 140

    for f in range(FRAMES):
        img = Image.new("RGB", (W, H), (11, 15, 25))
        draw = ImageDraw.Draw(img)

        for x in range(0, W, 30):
            draw.line([(x, 0), (x, H)], fill=(30, 41, 59))
        for y in range(0, H, 30):
            draw.line([(0, y), (W, y)], fill=(30, 41, 59))

        draw.rounded_rectangle([1, 1, W - 2, H - 2], radius=10, outline=(30, 41, 59), width=2)

        phase = f / FRAMES * 2 * math.pi
        pts: list[tuple[int, int]] = []
        for x in range(-50, W + 50, 6):
            t = x / W * 4 * math.pi + phase
            y = wave_y + int(25 * math.sin(t) + 12 * math.sin(t * 2.3))
            pts.append((x, y))
        if len(pts) > 1:
            draw.line(pts, fill=(9, 241, 184), width=2)
            draw.line(pts, fill=(14, 165, 233), width=1)

        draw.rounded_rectangle([32, 35, 372, 165], radius=8, fill=(4, 6, 13), outline=(30, 41, 59))
        draw.text((48, 48), "MATASSA://REFERENCE_TABLES", fill=(71, 85, 105))
        draw.text((48, 72), "[OK] T-scale tables M (1.0x)", fill=(9, 241, 184))
        draw.text((48, 92), "[INF] 6 markets calibrated", fill=(139, 92, 246))
        draw.text((48, 112), "[SYS] Pine private | TV invite", fill=(148, 163, 184))

        draw.text((400, 55), "MATASSA CYCLE", fill=(255, 255, 255))
        draw.text((400, 82), "FRAMEWORK", fill=(255, 255, 255))
        draw.text((400, 108), "T-SCALE REFERENCE LAYER", fill=(9, 241, 184))

        pulse = 4 + (2 if f % 12 < 6 else 0)
        cx, cy = 618, 48
        draw.ellipse([cx - pulse, cy - pulse, cx + pulse, cy + pulse], fill=(9, 241, 184))
        draw.text((630, 44), "REFERENCE LIVE", fill=(9, 241, 184))

        frames.append(img)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True)
    print(f"Wrote {OUT} ({len(frames)} frames)")


if __name__ == "__main__":
    main()
