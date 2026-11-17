#!/usr/bin/env python3
# read: the read level for this workflow. Runs only once there are saved files to work on,
# then walks the rules for the "work" index one section at a time (parts/read_log.py).
# Base: every section logged -> READ ✓, which is what lets the outer level start.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "parts"))
import read_log  # noqa: E402

saved = ROOT / "work" / "saved"
if not saved.exists() or not any(saved.iterdir()):
    sys.exit("READ NO-GO: nothing in saved (run save first)")
if read_log.ok(str(ROOT), "work"):
    print("Applying index work")
    print("READ ✓")
else:
    read_log.main([str(ROOT), "read", "work"])
