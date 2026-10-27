"""Scrape the public contribution calendar into data/contributions.json.

Uses only the standard library, so it runs in Actions and Termux without installs.
"""
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

USER = "BiparJoy"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"

CELL_RE = re.compile(r"<td\b[^>]*?\bdata-date=\"([\d-]+)\"[^>]*>", re.S)
ATTR_RE = re.compile(r'\b(id|data-level)="([^"]*)"')
TIP_RE = re.compile(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', re.S)
COUNT_RE = re.compile(r"^(\d[\d,]*) contributions?")


def fetch_html() -> str:
    req = urllib.request.Request(
        f"https://github.com/users/{USER}/contributions",
        headers={"User-Agent": "profile-readme-heatmap"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse(html: str) -> list[dict]:
    counts = {}
    for cell_id, text in TIP_RE.findall(html):
        m = COUNT_RE.match(text.strip())
        counts[cell_id] = int(m.group(1).replace(",", "")) if m else 0

    days = []
    for m in CELL_RE.finditer(html):
        attrs = dict(ATTR_RE.findall(m.group(0)))
        days.append({
            "date": m.group(1),
            "level": int(attrs.get("data-level", 0)),
            "count": counts.get(attrs.get("id"), 0),
        })
    days.sort(key=lambda d: d["date"])
    return days


def stats(days: list[dict]) -> dict:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)

    # Today may have no contributions yet; don't let that break the streak.
    current = 0
    tail = days[:-1] if days and not days[-1]["count"] else days
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1

    best = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]

    return {
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"]),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": months,
    }


def main() -> None:
    days = parse(fetch_html())
    if len(days) < 300:
        sys.exit(f"Only parsed {len(days)} days; GitHub's markup probably changed.")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "user": USER,
        "generated": date.today().isoformat(),
        "stats": stats(days),
        "days": days,
    }, indent=1))
    print(f"Wrote {len(days)} days to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
