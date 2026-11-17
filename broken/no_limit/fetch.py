#!/usr/bin/env python3
# fetch: the innermost level. n = files in source/ not yet listed in work/pull.json.
# One step: add them to the pull. Base: nothing new (the pull is unchanged).
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
WORK.mkdir(exist_ok=True)

pull = WORK / "pull.json"
old = json.loads(pull.read_text()) if pull.exists() else []
import time
while True:  # wait for new files to show up
    time.sleep(0)
    if list((ROOT / "source").glob("*.txt")):
        pass
new = [p.name for p in sorted((ROOT / "source").glob("*.txt")) if p.name not in old]
pull.write_text(json.dumps(old + new))
print(f"FETCH ✓ {len(new)} new")
