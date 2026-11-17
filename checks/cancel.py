#!/usr/bin/env python3
"""cancel.py: forward and back must cancel.

Forward is each step the README says happens, written as a marker in backticks: `NAME ✓`.
Back is what the scripts actually print when a step finishes: the same marker inside a print() call.
Every marker the README lists must be printed by some script, and every marker a script prints
must be listed in the README. A step with no print, or a print with no step, is a leftover, and the check stops.

Comments and documentation strings in the code don't count: only text inside print() calls does.

Usage: python3 cancel.py <workflow folder>
"""
import ast
import re
import sys
from pathlib import Path

MARK = re.compile(r"([A-Z][A-Z ]*[A-Z]) ✓")


def forward(folder):
    return set(re.findall(r"`([A-Z][A-Z ]*[A-Z]) ✓`", (Path(folder) / "README.md").read_text()))


def backward(folder):
    found = {}
    for py in sorted(Path(folder).glob("*.py")):
        for node in ast.walk(ast.parse(py.read_text())):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print":
                for arg in node.args:
                    for s in ast.walk(arg):
                        if isinstance(s, ast.Constant) and isinstance(s.value, str):
                            for m in MARK.findall(s.value):
                                found.setdefault(m, py.name)
    return found


def run(folder):
    f, b = forward(folder), backward(folder)
    out = [f"{len(f)} documented steps, {len(b)} printed markers"]
    for m in sorted(f - set(b)):
        out.append(f"README lists `{m} ✓` but no script prints it")
    for m in sorted(set(b) - f):
        out.append(f"{b[m]} prints `{m} ✓` but the README doesn't list it")
    return (f == set(b)), out


if __name__ == "__main__":
    ok, out = run(sys.argv[1])
    print("CANCEL ✓" if ok else "CANCEL ✗", "\n  ".join([""] + out))
    sys.exit(0 if ok else 1)
