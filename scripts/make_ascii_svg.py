"""Turn the GitHub avatar into an animated ASCII-art SVG (run locally when the avatar changes).

Needs Pillow. Each row is typed in left to right behind a block cursor, staggered
top to bottom, then frozen.
"""
import io
import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

from svgkit import window

USER = "BiparJoy"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "avatar-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"  # dark (sparse) -> bright (dense); light text on a dark terminal
COLS, ROWS = 80, 42
WIDTH, HEIGHT = 370, 400
PAD_X, TEXT_TOP = 15, 46
FILL = "#d0d7de"
CURSOR = "#39d353"


def load_avatar() -> Image.Image:
    src = os.environ.get("AVATAR")
    if src:
        return Image.open(src)
    req = urllib.request.Request(f"https://avatars.githubusercontent.com/{USER}?s=460",
                                 headers={"User-Agent": "profile-readme-ascii"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return Image.open(io.BytesIO(resp.read()))


def to_rows(img: Image.Image) -> list[str]:
    img = ImageOps.grayscale(img)
    # Blur roughly one character cell so fur texture doesn't turn into noise.
    img = img.filter(ImageFilter.GaussianBlur(img.width / COLS))
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    # Push the dark rock background toward blank so the subject stands out.
    curve = [0 if v < 60 else int(255 * (v - 60) / 195) for v in range(256)]
    img = img.point(curve)
    px = img.load()
    last = len(RAMP) - 1
    return ["".join(RAMP[px[x, y] * last // 255] for x in range(COLS)).rstrip() for y in range(ROWS)]


def main() -> None:
    rows = to_rows(load_avatar())
    text_w = WIDTH - 2 * PAD_X
    line_h = (HEIGHT - TEXT_TOP - 14) / ROWS
    char_w = text_w / COLS
    # Monospace glyphs are ~0.6em wide; size so rows fit even where textLength is ignored.
    font_size = min(line_h * 1.02, char_w / 0.61)

    parts = []
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        y = TEXT_TOP + i * line_h
        length = len(row) * char_w
        text = row.replace("&", "&amp;").replace("<", "&lt;")
        attrs = f'x="{PAD_X}" y="{y + line_h * 0.8:.2f}" font-size="{font_size:.2f}" fill="{FILL}" xml:space="preserve" textLength="{length:.2f}" lengthAdjust="spacingAndGlyphs"'
        if STATIC:
            parts.append(f"<text {attrs}>{text}</text>")
            continue
        begin, dur = 0.25 + i * 0.07, 0.32 + 0.18 * len(row) / COLS
        parts.append(
            f'<clipPath id="r{i}"><rect x="{PAD_X}" y="{y:.2f}" width="0" height="{line_h + 1:.2f}">'
            f'<animate attributeName="width" from="0" to="{length + 2:.2f}" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
            f'<text {attrs} clip-path="url(#r{i})">{text}</text>'
            f'<rect x="{PAD_X}" y="{y + 1:.2f}" width="{char_w:.2f}" height="{line_h - 1:.2f}" fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + length:.2f}" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + dur:.2f}s"/></rect>'
        )

    OUT.write_text(window(WIDTH, HEIGHT, f"{USER}@github: ~/avatar.txt", "".join(parts)))
    print(f"Wrote {OUT.name}")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
