"""Fetch Google Scholar metrics for the profile and write assets/scholar.json.

Run daily on the owner's Mac by ~/scholar-updater/run.sh (launchd);
.github/workflows/scholar.yml can also run it by hand. Uses only the standard library.
If Scholar blocks the request or the page layout changes, the script exits
without touching any file, so the site keeps its last good numbers.
It also refreshes the citation figures in README.md.
"""
import datetime
import os
import html
import json
import pathlib
import re
import sys
import urllib.request

USER = "fFcWmdwAAAAJ"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en&cstart=0&pagesize=100"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "scholar.json"
README = ROOT / "README.md"


def fetch():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(page):
    stats = [int(x) for x in re.findall(r'class="gsc_rsb_std">(\d+)<', page)]
    rows = re.findall(r'class="gsc_a_at">(.*?)</a>.*?class="gsc_a_c">(.*?)</td>', page, flags=re.S)
    if len(stats) < 6 or not rows:
        raise ValueError("Scholar page did not contain the expected tables (blocked or layout changed)")
    papers = []
    for title, cell in rows:
        m = re.search(r">(\d+)</a>", cell)
        papers.append({"title": html.unescape(re.sub(r"<[^>]+>", "", title)).strip(),
                       "citations": int(m.group(1)) if m else 0})
    return {
        "updated": datetime.date.today().isoformat(),
        "source": f"https://scholar.google.com/citations?user={USER}&hl=en",
        "citations": stats[0],
        "h_index": stats[2],
        "i10_index": stats[4],
        "publications": len(papers),
        "papers": papers,
    }


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def update_readme(data):
    if not README.exists():
        return
    text = README.read_text(encoding="utf-8")
    day = datetime.date.fromisoformat(data["updated"])
    stamp = f"{day.day} {day.strftime('%B %Y')}"
    text = re.sub(
        r"Google Scholar, [0-9]{1,2} [A-Za-z]+ [0-9]{4} · \*\*\d+\*\* papers · \*\*\d+\*\* citations · "
        r"h-index \*\*\d+\*\* · i10-index \*\*\d+\*\*",
        f"Google Scholar, {stamp} · **{data['publications']}** papers · **{data['citations']}** citations · "
        f"h-index **{data['h_index']}** · i10-index **{data['i10_index']}**", text)
    text = re.sub(r"Scholar-\d+%20citations", f"Scholar-{data['citations']}%20citations", text)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not line.startswith("| 20"):
            continue
        cells = line.split("|")
        title = norm(re.sub(r"\]\(.*", "", cells[2]).lstrip(" ["))
        for p in data["papers"]:
            if norm(p["title"]).startswith(title[:40]) or title.startswith(norm(p["title"])[:40]):
                bold = cells[-2].strip().startswith("**")
                val = f"**{p['citations']}**" if bold else str(p["citations"])
                cells[-2] = f" {val} "
                lines[i] = "|".join(cells)
    README.write_text("\n".join(lines), encoding="utf-8")


def main():
    try:
        data = parse(fetch())
    except Exception as e:  # keep last good numbers
        print(f"Skipped: {e}")
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::warning::Scholar fetch skipped: {e}")
        return 0
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    same = {k: v for k, v in old.items() if k != "updated"} == {k: v for k, v in data.items() if k != "updated"}
    if same:
        print("No change in Scholar metrics")
        return 0
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    update_readme(data)
    print(f"Updated: {data['citations']} citations, h-index {data['h_index']}, i10 {data['i10_index']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
