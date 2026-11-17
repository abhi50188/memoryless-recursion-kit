#!/usr/bin/env python3
"""pairs.py: no comparison reads the same cell on both sides.

A check that compares a value with a copy of itself always passes and proves nothing.
What it reads: every call to within(...) or same(...) in the workflow's scripts.
What it requires: both sides are cell("<source>", "<column>") calls, and the two cells differ
(a different column, or the same column from a different source).
It stops on a side it can't map to a cell (so nothing passes unmapped) or on a cell compared with itself.
It confirms the cells differ, not what they mean.

Usage: python3 pairs.py <workflow folder>
"""
import ast
import sys
from pathlib import Path


def _cell(node):
    if (isinstance(node, ast.Call) and getattr(node.func, "id", None) == "cell" and len(node.args) == 2
            and all(isinstance(a, ast.Constant) for a in node.args)):
        return (node.args[0].value, node.args[1].value)
    return None


def run(folder):
    pairs, problems = [], []
    for py in sorted(Path(folder).glob("*.py")):
        for node in ast.walk(ast.parse(py.read_text())):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) in ("within", "same"):
                a, b = (_cell(x) for x in node.args[:2])
                if a is None or b is None:
                    problems.append(f"{py.name}:{node.lineno} a side of this comparison isn't a cell(source, column)")
                elif a == b:
                    problems.append(f"{py.name}:{node.lineno} compares {a[0]}.{a[1]} with itself")
                else:
                    pairs.append(f"{a[0]}.{a[1]} → {b[0]}.{b[1]}")
    return (not problems), [f"{len(pairs)} comparisons: " + (", ".join(pairs) or "none")] + problems


if __name__ == "__main__":
    ok, out = run(sys.argv[1])
    print("PAIRS ✓" if ok else "PAIRS ✗", "\n  ".join([""] + out))
    sys.exit(0 if ok else 1)
