#!/usr/bin/env python3
"""read_log.py: the read level. Rules are read just before the step that needs them.

The recursion:
  n         = the sections of a kind of work's index not yet logged for this session.
  one step  = print the next section; the reader logs one line, in their own words, saying what it requires.
  base case = none left -> "Applying index <kind>". The step's own script starts only once the log is complete.

The reader writes the log line, not a script: a log a script writes proves nothing about what was read.
The log is keyed by session and section, so a section shared by two kinds of work is read once per session.

Usage (from a workflow folder that has rules_index.txt):
  python3 read_log.py <folder> read <kind>
  python3 read_log.py <folder> add  <kind> "<heading>" "<what it requires, in your own words>"
  python3 read_log.py <folder> ok   <kind>        (exit 0 if the log is complete)
  python3 read_log.py <folder> reset              (clear this session's lines, e.g. after a compaction)

Index format, one line per kind of work:   kind | rules file | heading ; heading ; ...
"""
import json
import os
import re
import sys
from pathlib import Path


def session():
    return os.environ.get("KIT_SESSION", "default")


def entries(folder, kind):
    out = []
    for line in (Path(folder) / "rules_index.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        k, f, heads = [x.strip() for x in line.split("|")]
        if k == kind:
            out += [(f, h.strip()) for h in heads.split(";")]
    return out


def text(folder, f, heading):
    parts = re.split(r"(?m)^## (.+)$", (Path(folder) / f).read_text())
    for h, body in zip(parts[1::2], parts[2::2]):
        if h.strip().startswith(heading):
            return body.strip()
    return None


def log_path(folder):
    return Path(folder) / "work" / "read_log.jsonl"


def logged(folder):
    p = log_path(folder)
    if not p.exists():
        return set()
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return {r["section"] for r in rows if r["session"] == session()}


def left(folder, kind):
    have = logged(folder)
    return [(f, h) for f, h in entries(folder, kind) if f"{f}: {h}" not in have]


def ok(folder, kind):
    return bool(entries(folder, kind)) and not left(folder, kind)


def add(folder, kind, section, note):
    if section not in [f"{f}: {h}" for f, h in entries(folder, kind)]:
        sys.exit(f"READ NO-GO: {section} is not in index {kind}")
    if len(note.split()) < 6:
        sys.exit("READ NO-GO: write what the section requires, at least six words")
    p = log_path(folder)
    p.parent.mkdir(exist_ok=True)
    with open(p, "a") as o:
        o.write(json.dumps({"session": session(), "kind": kind, "section": section, "note": note}) + "\n")


def main(argv):
    folder, cmd = argv[0], argv[1]
    if cmd == "reset":
        p = log_path(folder)
        if p.exists():
            keep = [l for l in p.read_text().splitlines() if l.strip() and json.loads(l)["session"] != session()]
            p.write_text("".join(k + "\n" for k in keep))
        return print("Read log cleared for this session.")
    kind = argv[2]
    if not entries(folder, kind):
        sys.exit(f"READ NO-GO: no index {kind}")
    if cmd == "ok":
        sys.exit(0 if ok(folder, kind) else 1)
    if cmd == "add":
        add(folder, kind, argv[3], argv[4])
        return print(f"Logged: {argv[3]}")
    if cmd == "read":
        todo = left(folder, kind)
        if not todo:
            return print(f"Applying index {kind}")
        f, h = todo[0]
        t = text(folder, f, h)
        if t is None:
            sys.exit(f"READ NO-GO: heading '{h}' not found in {f}")
        print(f"Section {len(entries(folder, kind)) - len(todo) + 1} of {len(entries(folder, kind))}: {f}: {h}\n\n{t}\n")
        print(f'Then: python3 read_log.py {folder} add {kind} "{f}: {h}" "<what it requires, in your own words>"')


if __name__ == "__main__":
    main(sys.argv[1:])
