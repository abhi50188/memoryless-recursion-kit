#!/usr/bin/env python3
# build: assembles the batch that's ready from due.json, up to BATCH_LIMIT items.
# What a real step would draft is out of scope; this writes a placeholder per item.
import json
import sys
from pathlib import Path

BATCH_LIMIT = 5

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"

due_file = WORK / "due.json"
if not due_file.exists():
    sys.exit("BUILD NO-GO: no due.json (run outer first)")
due = json.loads(due_file.read_text())[:BATCH_LIMIT]
batch = {"count": len(due), "items": [{"name": n, "draft": f"[placeholder draft for {n}]"} for n in due]}
(WORK / "batch.json").write_text(json.dumps(batch, indent=1))
print(f"built {len(due)}")
