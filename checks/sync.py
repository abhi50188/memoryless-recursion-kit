#!/usr/bin/env python3
"""sync.py: the README agrees with itself and with facts read from the code.

The documentation never vouches for itself: every claim it makes is tested against the code.
What it checks:
  - Every script the README names in backticks (`name.py`) exists.
  - Every script in the folder is named in the README.
  - Every fact the README states in backticks as `NAME = value`:
      * says the same thing everywhere it appears in the README, and
      * matches a top-level assignment NAME = value in the code, read out of the code itself.
It stops on the first kind of disagreement it finds and names each one.

Usage: python3 sync.py <workflow folder>
"""
import ast
import re
import sys
from pathlib import Path


def code_facts(folder):
    facts = {}
    for py in sorted(Path(folder).glob("*.py")):
        for node in ast.parse(py.read_text()).body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id.isupper():
                        facts[t.id] = (repr(node.value.value), py.name)
    return facts


def run(folder):
    folder = Path(folder)
    text = (folder / "README.md").read_text()
    out, problems = [], []

    named = set(re.findall(r"`(?:\.\./parts/)?([\w]+\.py)`", text))
    present = {p.name for p in folder.glob("*.py")}
    parts = {p.name for p in (folder.parent / "parts").glob("*.py")}
    for s in sorted(named - present - parts):
        problems.append(f"README names `{s}`, which doesn't exist")
    for s in sorted(present - named):
        problems.append(f"{s} is in the folder but the README never names it")

    stated = {}
    for name, value in re.findall(r"`([A-Z_]+) = ([^`]+)`", text):
        stated.setdefault(name, set()).add(value.strip())
    facts = code_facts(folder)
    for name, values in sorted(stated.items()):
        if len(values) > 1:
            problems.append(f"README says {name} is {' and '.join(sorted(values))}")
            continue
        value = next(iter(values))
        if name not in facts:
            problems.append(f"README states {name} = {value}, but no script sets {name}")
        elif ast.literal_eval(value) != ast.literal_eval(facts[name][0]):
            problems.append(f"README says {name} = {value}; {facts[name][1]} says {facts[name][0]}")

    out.append(f"{len(named)} scripts named, {len(present)} present, {len(stated)} facts stated")
    return (not problems), out + problems


if __name__ == "__main__":
    ok, out = run(sys.argv[1])
    print("SYNC ✓" if ok else "SYNC ✗", "\n  ".join([""] + out))
    sys.exit(0 if ok else 1)
