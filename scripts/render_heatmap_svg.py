"""Render data/contributions.json as an animated contribution heatmap SVG."""
import json
import os
from datetime import date
from pathlib import Path

from svgkit import MUTED, TEXT, window

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
WIDTH = 860
CELL, GAP = 12, 3
LEFT, TOP = 46, 84


def level(count: int, peak: int, gh_level: int) -> int:
    # Reserve the neon top colour for days near the year's peak.
    if count and peak and count >= 0.8 * peak and gh_level == 4:
        return 5
    return gh_level


def main() -> None:
    data = json.loads(SRC.read_text())
    days, st = data["days"], data["stats"]
    peak = st["best_day"]["count"]
    offset = (date.fromisoformat(days[0]["date"]).weekday() + 1) % 7  # Sunday-first rows

    cells, month_labels, last_month, last_x = [], [], None, -99
    for i, d in enumerate(days):
        col, row = divmod(i + offset, 7)
        x, y = LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
        lv = level(d["count"], peak, d["level"])
        anim = "" if STATIC else f' class="c" style="animation-delay:{(col + row) * 0.018:.3f}s"'
        tip = f'{d["count"]} contribution{"" if d["count"] == 1 else "s"} on {d["date"]}'
        cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[lv]}"{anim}><title>{tip}</title></rect>')

        month = d["date"][:7]
        if month != last_month and row <= 3 and col < 52:
            label = date.fromisoformat(d["date"]).strftime("%b")
            if x - last_x < 3 * (CELL + GAP) and month_labels:
                month_labels.pop()  # a partial first month would collide with the next label
            month_labels.append(f'<text x="{x}" y="{TOP - 8}" font-size="10" fill="{MUTED}">{label}</text>')
            last_month, last_x = month, x

    weekdays = "".join(
        f'<text x="{LEFT - 8}" y="{TOP + r * (CELL + GAP) + 10}" font-size="10" fill="{MUTED}" text-anchor="end">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    grid_bottom = TOP + 7 * (CELL + GAP)
    legend_x = WIDTH - 24 - len(PALETTE) * (CELL + GAP) - 34
    legend = (
        f'<text x="{legend_x - 6}" y="{grid_bottom + 18}" font-size="10" fill="{MUTED}" text-anchor="end">Less</text>'
        + "".join(
            f'<rect x="{legend_x + i * (CELL + GAP)}" y="{grid_bottom + 8}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
            for i, c in enumerate(PALETTE)
        )
        + f'<text x="{legend_x + len(PALETTE) * (CELL + GAP) + 4}" y="{grid_bottom + 18}" font-size="10" fill="{MUTED}">More</text>'
    )

    prompt = f'<text x="20" y="48" font-size="12" fill="{MUTED}"><tspan fill="#39d353">➜</tspan> <tspan fill="#58a6ff">~</tspan> {st["total"]} contributions in the last year</text>'

    best = st["best_day"]
    best_txt = f'{best["count"]} on {date.fromisoformat(best["date"]).strftime("%b %d")}' if best["count"] else "—"
    pairs = [
        ("total", st["total"]),
        ("active days", st["active_days"]),
        ("current streak", f'{st["current_streak"]}d'),
        ("longest streak", f'{st["longest_streak"]}d'),
        ("best day", best_txt),
    ]
    footer_y = grid_bottom + 48
    slot = (WIDTH - 40) / len(pairs)
    footer = "".join(
        f'<text x="{20 + i * slot + slot / 2}" y="{footer_y}" font-size="16" font-weight="700" fill="{TEXT}" text-anchor="middle"{"" if STATIC else f" class=\"f\" style=\"animation-delay:{1.4 + i * 0.12:.2f}s\""}>{v}</text>'
        f'<text x="{20 + i * slot + slot / 2}" y="{footer_y + 16}" font-size="10" fill="{MUTED}" text-anchor="middle"{"" if STATIC else f" class=\"f\" style=\"animation-delay:{1.4 + i * 0.12:.2f}s\""}>{k}</text>'
        for i, (k, v) in enumerate(pairs)
    )

    style = "" if STATIC else """
.c { opacity: 0; transform-box: fill-box; transform-origin: center; animation: pop .45s cubic-bezier(.2,.8,.3,1.2) forwards; }
.f { opacity: 0; animation: rise .5s ease-out forwards; }
@keyframes pop { from { opacity: 0; transform: translate(-6px,-6px) scale(.3); } to { opacity: 1; transform: none; } }
@keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
"""
    height = footer_y + 32
    body = prompt + "".join(month_labels) + weekdays + "".join(cells) + legend + footer
    OUT.write_text(window(WIDTH, height, f"{data['user']}@github: ~/contributions", body, style))
    print(f"Wrote {OUT.name} ({len(days)} days, {st['total']} contributions)")


if __name__ == "__main__":
    main()
