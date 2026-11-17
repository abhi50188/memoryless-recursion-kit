#!/usr/bin/env python3
# outer: works out what is due, from the files alone. Repeats over the units in pull.json.
# n = files in the pull that are saved and not yet in the record. One step: mark it due. Base: none -> BASE CASE ✓.
# It won't run until the read level's log (work/read_log.jsonl) is complete for this session.
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
sys.path.insert(0, str(ROOT.parent / "parts"))
import read_log  # noqa: E402

LOG = WORK / "read_log.jsonl"
if not LOG.exists() or not read_log.ok(str(ROOT), "work"):
    sys.exit("OUTER NO-GO: the rules for this work aren't read yet (run read first)")

pull = json.loads((WORK / "pull.json").read_text())
record_file = WORK / "record.json"
done = json.loads(record_file.read_text()) if record_file.exists() else []
due = [n for n in pull if (WORK / "saved" / n).exists() and n not in done]
(WORK / "due.json").write_text(json.dumps(due))
if due:
    print(f"OUTER ✓ {len(due)} due")
else:
    print("BASE CASE ✓ nothing due")
