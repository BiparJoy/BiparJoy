"""Shared terminal-window chrome for the profile SVGs."""
from xml.sax.saxutils import escape

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"
BG = "#0d1117"
BORDER = "#30363d"
BAR = "#161b22"
MUTED = "#7d8590"
TEXT = "#c9d1d9"


def window(width: int, height: int, title: str, body: str, style: str = "") -> str:
    """Wrap body in a rounded terminal window with traffic-light dots."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
<style>
text {{ font-family: {FONT}; }}
{style}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 28 V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V28 Z" fill="{BAR}"/>
<line x1="0.5" y1="28" x2="{width - 0.5}" y2="28" stroke="{BORDER}"/>
<circle cx="16" cy="14.5" r="5" fill="#ff5f57"/>
<circle cx="32" cy="14.5" r="5" fill="#febc2e"/>
<circle cx="48" cy="14.5" r="5" fill="#28c840"/>
<text x="{width / 2}" y="18.5" text-anchor="middle" font-size="11" fill="{MUTED}">{escape(title)}</text>
{body}
</svg>
"""
