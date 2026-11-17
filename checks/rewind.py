#!/usr/bin/env python3
"""rewind.py: does this program rewind, or is it a list we're hoping will rewind?

What it reads: a shape file, one line per level (order doesn't matter; the gate never uses it):
    level | script(s) | gets "<file>" from <level below> [ | repeats over "<file>" ] [ | delivers ]
    level | script(s) | from outside: <what>
A line `# checklist` declares the levels side by side on purpose.

What it works out, on its own:
  - It finds the innermost level (the one that takes from outside) and walks up, level by level.
  - Each level must receive a file from exactly the level below it, and hand up to exactly one level above,
    until it lands on the level that delivers: the final base case.
  - Unless --design is given, each level's script must actually contain the name of the file it receives.

Verdicts: one pass, and six failure modes, each named for what went wrong:
  Rewinds ✓✓      one innermost level; each level hands up a file its script reads; it lands on the base case
  List          levels side by side, or a level that hands to nobody
  MEMORY        something is handed up in chat, not in a file
  NOT IN CODE   the shape claims a hand-off the receiving script doesn't have
  LOOP          a circle: levels that never connect to the outside
  DOESN'T LAND  the walk ends on a level that doesn't deliver
  BROKEN        a level takes from a level that doesn't exist, or names a script that doesn't exist
  Checklist ✓✓ (declared)   side by side on purpose, and declared

The gate proves the shape, not that a script can't run without its file. For that, run takeaway.py.

Usage: python3 rewind.py <shape file> [--design]
"""
import re
import sys
from pathlib import Path


def parse(path):
    levels, checklist = {}, False
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if line.lower().startswith("# checklist"):
            checklist = True
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        lv = {"name": parts[0], "scripts": [s.strip() for s in parts[1].split(",")],
              "file": None, "from": None, "outside": False, "chat": False, "delivers": False}
        for p in parts[2:]:
            m = re.match(r'gets "([^"]+)"( in chat)? from (\S+)', p)
            if m:
                lv["file"], lv["chat"], lv["from"] = m.group(1), bool(m.group(2)), m.group(3)
            elif p.startswith("from outside"):
                lv["outside"] = True
            elif p == "delivers":
                lv["delivers"] = True
        levels[lv["name"]] = lv
    return levels, checklist


def verdict(path, design=False):
    levels, checklist = parse(path)
    folder = Path(path).parent
    notes = []

    for lv in levels.values():
        if not lv["outside"] and lv["from"] not in levels:
            return "BROKEN", [f"{lv['name']} takes from '{lv['from']}', which isn't a level"]
        if not design:
            for s in lv["scripts"]:
                if not (folder / s).exists():
                    return "BROKEN", [f"{lv['name']} names {s}, which doesn't exist"]

    if checklist:
        if all(lv["outside"] for lv in levels.values()):
            return "Checklist ✓✓ (declared)", [f"{len(levels)} levels side by side, declared"]
        notes.append("declared a checklist, but some levels take from others")

    for lv in levels.values():
        if lv["chat"]:
            return "MEMORY", [f"{lv['name']} gets \"{lv['file']}\" in chat from {lv['from']}: hand it up in a file"]

    inner = [n for n, lv in levels.items() if lv["outside"]]
    if not inner:
        return "LOOP", ["no level takes from outside, so the levels only feed each other"]
    if len(inner) > 1:
        return "List", [f"{len(inner)} innermost levels side by side: {', '.join(inner)}"]

    above = {}
    for n, lv in levels.items():
        if lv["from"]:
            above.setdefault(lv["from"], []).append(n)

    walk, cur = [inner[0]], inner[0]
    while cur in above:  # bound: each level is visited once (checked just below), so at most len(levels) steps
        ups = above[cur]
        if len(ups) > 1:
            return "List", [f"{', '.join(ups)} all take from {cur}: side by side, not nested"]
        cur = ups[0]
        if cur in walk:
            return "LOOP", [f"the walk comes back to {cur}"]
        walk.append(cur)

    missed = [n for n in levels if n not in walk]
    if missed:
        return "LOOP", [f"never reached from the outside: {', '.join(missed)}"]
    if not levels[cur]["delivers"]:
        return "DOESN'T LAND", [f"the walk ends at {cur}, which doesn't deliver: it hands to nobody"]

    if not design:
        for n in walk[1:]:
            lv = levels[n]
            code = "".join((folder / s).read_text() for s in lv["scripts"])
            if lv["file"] not in code:
                return "NOT IN CODE", [f"{n} is said to get \"{lv['file']}\" from {lv['from']}, but {', '.join(lv['scripts'])} never names it"]

    rows = [f"{walk[0]} (from outside)"] + [f"{n} ← \"{levels[n]['file']}\" from {levels[n]['from']}" for n in walk[1:]]
    return "Rewinds ✓✓", notes + ["innermost first: " + " → ".join(walk)] + rows


if __name__ == "__main__":
    v, out = verdict(sys.argv[1], "--design" in sys.argv)
    print(v, "\n  ".join([""] + out))
    sys.exit(0 if v.endswith("✓✓") or v.endswith("(declared)") else 1)
