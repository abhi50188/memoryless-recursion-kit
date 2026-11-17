#!/usr/bin/env python3
# save: brings each new file into its place, and only that. Skips anything already in place.
# n = files in pull.json not yet in work/saved/. One step: copy one. Base: all in place.
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"

pull = WORK / "pull.json"
if not pull.exists():
    sys.exit("SAVE NO-GO: no pull.json (run fetch first)")
saved = WORK / "saved"
saved.mkdir(exist_ok=True)
for name in json.loads(pull.read_text()):
    if not (saved / name).exists():
        shutil.copy(ROOT / "source" / name, saved / name)
print("SAVE ✓")
