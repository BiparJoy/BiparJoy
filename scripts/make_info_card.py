"""Render the neofetch-style info card SVG (edit LINES and re-run when details change)."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

from svgkit import BORDER, MUTED, TEXT, window

USER = "BiparJoy"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

WIDTH, HEIGHT = 490, 400
X, TOP, LINE = 22, 72, 25
KEY_W = 92

# (key, value, key colour)
LINES = [
    ("Now", "Prism: Rust download manager", "#39d353"),
    ("", "32 connections · crash-safe resume", "#39d353"),
    ("Desktop", "KDE Plasma 6 · Noctalia widgets", "#58a6ff"),
    ("Visuals", "NCS orb: 103,684 GPU-drawn dots", "#bc8cff"),
    ("Tools", "ColorNote backup decryptor (Tk)", "#f0883e"),
    ("Stack", "Rust · C++ · QML · Python · Luau", "#ff7b72"),
    ("Into", "Linux gaming · PS4/PS5 emulation", "#d2a8ff"),
    ("", "and native-port scene", "#d2a8ff"),
    ("Shell", "Termux on Android, Linux on desktop", "#79c0ff"),
    ("Since", "Apr 2026 on GitHub", "#e3b341"),
]
SWATCHES = ["#ff7b72", "#f0883e", "#e3b341", "#39d353", "#79c0ff", "#58a6ff", "#bc8cff", "#d2a8ff"]


def anim(i: int) -> str:
    return "" if STATIC else f' class="l" style="animation-delay:{0.2 + i * 0.11:.2f}s"'


def main() -> None:
    title = f'{USER}<tspan fill="{MUTED}">@</tspan>github'
    parts = [
        f'<text x="{X}" y="52" font-size="15" font-weight="700" fill="#39d353"{anim(0)}>{title}</text>',
        f'<line x1="{X}" y1="60" x2="{X + 150}" y2="60" stroke="{BORDER}" stroke-width="1.5"{anim(0)}/>',
    ]
    for i, (key, value, colour) in enumerate(LINES, start=1):
        y = TOP + i * LINE - 6
        parts.append(
            f'<g{anim(i)}><text x="{X}" y="{y}" font-size="13" font-weight="700" fill="{colour}">{escape(key)}</text>'
            f'<text x="{X + KEY_W}" y="{y}" font-size="13" fill="{TEXT}">{escape(value)}</text></g>'
        )

    sw_y = TOP + (len(LINES) + 1) * LINE - 6
    swatch = "".join(
        f'<rect x="{X + i * 30}" y="{sw_y}" width="26" height="14" rx="3" fill="{c}"/>' for i, c in enumerate(SWATCHES)
    )
    parts.append(f"<g{anim(len(LINES) + 1)}>{swatch}</g>")

    prompt_y = HEIGHT - 22
    parts.append(
        f'<text x="{X}" y="{prompt_y}" font-size="13" fill="{MUTED}"{anim(len(LINES) + 2)}>'
        f'<tspan fill="#39d353">➜</tspan> <tspan fill="#58a6ff">~</tspan> </text>'
        f'<rect x="{X + 34}" y="{prompt_y - 11}" width="8" height="14" fill="#39d353"'
        + ("" if STATIC else f' class="cur" style="animation-delay:{0.2 + (len(LINES) + 2) * 0.11:.2f}s, {0.2 + (len(LINES) + 2) * 0.11:.2f}s"')
        + "/>"
    )

    style = "" if STATIC else """
.l { opacity: 0; animation: in .45s ease-out forwards; }
.cur { opacity: 0; animation: in .1s forwards, blink 1.1s steps(1) infinite; }
@keyframes in { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: none; } }
@keyframes blink { 50% { opacity: 0; } }
"""
    OUT.write_text(window(WIDTH, HEIGHT, f"{USER}@github: ~/neofetch", "".join(parts), style))
    print(f"Wrote {OUT.name}")


if __name__ == "__main__":
    main()
