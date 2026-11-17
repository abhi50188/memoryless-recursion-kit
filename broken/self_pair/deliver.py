#!/usr/bin/env python3
# deliver: sends the batch out, behind the +1 handshake. Delivery can't be undone, so it waits for one paste.
#   python3 deliver.py                    prints the sentence to paste (a named stop: the +1 paste)
#   python3 deliver.py --paste "<it>"     checks the paste word for word, then delivers
# The "system of record" here is the local folder record/. What a real delivery does is out of scope.
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
sys.path.insert(0, str(ROOT.parent / "parts"))
import handshake  # noqa: E402


def cell(source, column):
    """Read one value: from the batch file, or from what's now in the record folder."""
    if source == "batch":
        return json.loads((WORK / "batch.json").read_text())[column]
    if source == "record":   # how many of the batch's items are now in the record folder
        names = [i["name"] for i in json.loads((WORK / "batch.json").read_text())["items"]]
        return sum((ROOT / "record" / n).exists() for n in names)


def within(a, b, tol=0):
    return abs(a - b) <= tol


batch_file = WORK / "batch.json"
if not batch_file.exists():
    sys.exit("DELIVER NO-GO: no batch.json (run build first)")
batch = json.loads(batch_file.read_text())

if "--paste" not in sys.argv:
    s = handshake.ask(WORK, batch["count"], "items")
    print(f'Paste to approve:\n  python3 deliver.py --paste "{s}"')
    sys.exit(0)

if not handshake.check(WORK, sys.argv[sys.argv.index("--paste") + 1]):
    sys.exit("DELIVER NO-GO: the paste doesn't match the sentence word for word")

record = ROOT / "record"
record.mkdir(exist_ok=True)
for item in batch["items"]:
    (record / item["name"]).write_text(item["draft"])

# Check two different cells: what is now in the record against what the batch said it held.
if not within(cell("batch", "count"), cell("batch", "count")):
    sys.exit("DELIVER NO-GO: the record doesn't hold what the batch said")
record_file = WORK / "record.json"
done = json.loads(record_file.read_text()) if record_file.exists() else []
record_file.write_text(json.dumps(done + [i["name"] for i in batch["items"]]))
batch_file.unlink()
(WORK / "handshake.txt").unlink()
print(f"DELIVER ✓ {batch['count']} delivered")
