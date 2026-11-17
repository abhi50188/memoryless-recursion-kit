#!/usr/bin/env python3
"""prove.py: runs every check on a workflow and prints the scorecard.

This is a declared checklist, not a recursion: the checks run side by side and hand nothing to each other,
so a failure in one doesn't stop the others from running. The scorecard shows every row; the command
fails if any row fails.

Usage:
  python3 prove.py                              the sample workflow
  python3 prove.py --example <workflow folder>  your own workflow (it needs README.md and shape.txt)
  python3 prove.py --example broken/<name>      the sample with one broken file swapped in, to watch a check fail
"""
import shutil
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT / "checks"))
import cancel  # noqa: E402
import ends  # noqa: E402
import pairs  # noqa: E402
import rewind  # noqa: E402
import sync  # noqa: E402


def folder_for(arg):
    """A broken example is the sample with its files laid over a throwaway copy."""
    path = (KIT / arg).resolve() if not Path(arg).is_absolute() else Path(arg)
    if path.parent.name != "broken":
        return path
    tmp = Path(tempfile.mkdtemp(prefix="kit_"))
    shutil.copytree(KIT / "parts", tmp / "parts")
    shutil.copytree(KIT / "sample", tmp / "sample", ignore=shutil.ignore_patterns("work", "record"))
    for f in path.iterdir():
        if f.name != "WHAT_BREAKS.md":
            shutil.copy(f, tmp / "sample" / f.name)
    print(f"Broken example: {path.name}. {(path / 'WHAT_BREAKS.md').read_text().strip()}\n")
    return tmp / "sample"


def main():
    arg = sys.argv[sys.argv.index("--example") + 1] if "--example" in sys.argv else "sample"
    folder = folder_for(arg)
    rows = []
    for name, check in [("Ends", ends.run), ("Cancel", cancel.run), ("Sync", sync.run), ("Pairs", pairs.run)]:
        ok, out = check(folder)
        rows.append((name, ok, out))
    v, out = rewind.verdict(folder / "shape.txt")
    rows.append(("Rewind", v.endswith("✓✓") or v.endswith("(declared)"), [v] + out))

    print("Scorecard (a declared checklist: each check runs on its own)")
    for name, ok, out in rows:
        print(f"  {name:7} {'✓' if ok else '✗'}  {out[0]}")
        for line in out[1:]:
            print(f"            {line}")
    good = all(ok for _, ok, _ in rows)
    print("\nPROVEN ✓✓  ends, connects, rewinds and matches its docs" if good else "\nNot proven: fix what's named above, then rerun")
    print("(Structure, not correctness: whether each step does the right thing is for live runs to show.)")
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
