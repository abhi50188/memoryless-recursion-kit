#!/usr/bin/env python3
"""takeaway.py: the take-away test. Does each level really need the file it's said to receive?

The rewind gate shows that a level's script *names* its file. This shows it *can't run without it*.
For each hand-off in the shape, in a throwaway copy: run every level below it, take the handed-up file away,
run the level above, and confirm it stops (exits with an error). Nothing in your folder is touched.

If the workflow has a read level (a rules_index.txt), the levels below the one under test get every rules section
logged automatically with a labeled test note, since this is a test run, not a real read. The level under test never does.

Usage: python3 takeaway.py [<workflow folder>]      (default: the sample)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "checks"))
sys.path.insert(0, str(KIT / "parts"))
import read_log  # noqa: E402
import rewind  # noqa: E402

NOTE = "test note: automated take-away run, not a real read"


def fill_reads(folder):
    """Log every rules section for this test session, if the workflow has a read level (rules_index.txt)."""
    if not (Path(folder) / "rules_index.txt").exists():
        return
    kinds = {l.split("|")[0].strip() for l in (Path(folder) / "rules_index.txt").read_text().splitlines()
             if l.strip() and not l.startswith("#")}
    for kind in sorted(kinds):
        for f, h in read_log.left(str(folder), kind):   # bounded: the index's sections
            read_log.add(str(folder), kind, f"{f}: {h}", NOTE)


def run_level(folder, level, fill=False):
    """Run a level's first script. Levels below the one under test get their reads filled in, then run again."""
    args = [sys.executable, level["scripts"][0]]
    r = subprocess.run(args, cwd=folder, capture_output=True, text=True)
    if fill and r.returncode == 0 and (Path(folder) / "rules_index.txt").exists():
        fill_reads(folder)
        r = subprocess.run(args, cwd=folder, capture_output=True, text=True)
    return r


def main():
    src = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else KIT / "sample"
    v, _ = rewind.verdict(src / "shape.txt")
    if not v.endswith("✓✓"):
        sys.exit(f"TAKEAWAY NO-GO: the shape doesn't rewind ({v}); fix that first with rewind.py")
    levels, _ = rewind.parse(src / "shape.txt")
    order = [n for n, lv in levels.items() if lv["outside"]]
    while len(order) < len(levels):  # bound: the rewind gate already proved one chain through every level
        order.append(next(n for n, lv in levels.items() if lv["from"] == order[-1]))

    results, stopped = [], 0
    for i, name in enumerate(order[1:], start=1):
        tmp = Path(tempfile.mkdtemp(prefix="takeaway_"))
        shutil.copytree(KIT / "parts", tmp / "parts")
        work = tmp / src.name
        shutil.copytree(src, work, ignore=shutil.ignore_patterns("work", "record"))
        os.environ["KIT_SESSION"] = f"takeaway_{i}"
        for below in order[:i]:
            run_level(work, levels[below], fill=True)
        handed = levels[name]["file"]
        gone = [p for p in work.rglob(handed)] or [p for p in (work / "work").glob("*") if handed in p.name]
        for p in gone:
            shutil.rmtree(p) if p.is_dir() else p.unlink()
        r = run_level(work, levels[name])
        ok = r.returncode != 0
        stopped += ok
        results.append(f"{'stops ✓' if ok else 'ran anyway ✗'}  take away \"{handed}\" → {name}"
                       + ("" if gone else "  (file never appeared, so nothing to take away)"))
        shutil.rmtree(tmp)

    print(f"TAKEAWAY {'✓' if stopped == len(results) else '✗'}  {stopped} of {len(results)} hand-offs stop without their file")
    for line in results:
        print("  " + line)
    sys.exit(0 if stopped == len(results) else 1)


if __name__ == "__main__":
    main()
