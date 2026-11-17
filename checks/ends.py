#!/usr/bin/env python3
"""ends.py: does every loop end, does every recursion name its base case, and is every wait a named stop?

What it reads: every .py file in the workflow folder, and the README's "## Recursions" section.
What it requires:
  - A `while` loop either is bounded by its own condition and says so with a `# bound:` comment
    (on the line or the line above), or is `while True` with a `break` in its body.
    `for` loops over a finite list are bounded by the list and pass.
  - A function that calls itself carries a `# base:` comment in its body naming the base case.
  - A call to input() (a wait on a person) carries a `# stop:` comment naming the stop.
  - Every bullet under "## Recursions" in the README says "Base:".
It stops when any of these is missing, and names the file and line.

This is a structural check on what the code says, not a proof that every loop terminates.

Usage: python3 ends.py <workflow folder>
"""
import ast
import re
import sys
from pathlib import Path


def _has_break(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Break):
            return True
    return False


def run(folder):
    folder = Path(folder)
    problems, loops, recursions, waits = [], 0, 0, 0
    for py in sorted(folder.glob("*.py")):
        src = py.read_text()
        lines = src.splitlines()
        tree = ast.parse(src)

        def comment_near(lineno, tag):
            here = lines[lineno - 1]
            above = lines[lineno - 2] if lineno > 1 else ""
            return tag in here or tag in above

        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                loops += 1
                forever = isinstance(node.test, ast.Constant) and node.test.value is True
                if forever and not _has_break(node):
                    problems.append(f"{py.name}:{node.lineno} `while True` with no break: this loop never ends")
                elif not forever and not comment_near(node.lineno, "# bound:"):
                    problems.append(f"{py.name}:{node.lineno} while loop with no `# bound:` comment saying what limits it")
            elif isinstance(node, ast.FunctionDef):
                calls_self = any(isinstance(n, ast.Call) and getattr(n.func, "id", None) == node.name
                                 for n in ast.walk(node))
                if calls_self:
                    recursions += 1
                    body = "\n".join(lines[node.lineno - 1:node.end_lineno])
                    if "# base:" not in body:
                        problems.append(f"{py.name}:{node.lineno} function {node.name} calls itself with no `# base:` comment")
            elif isinstance(node, ast.Call) and getattr(node.func, "id", None) == "input":
                waits += 1
                if not comment_near(node.lineno, "# stop:"):
                    problems.append(f"{py.name}:{node.lineno} input() wait with no `# stop:` comment naming the stop")

    readme = folder / "README.md"
    if readme.exists():
        m = re.search(r"(?ms)^## Recursions\s*$(.*?)(?=^## |\Z)", readme.read_text())
        for b in re.findall(r"(?m)^- (.+)$", m.group(1) if m else ""):
            recursions += 1
            if "Base:" not in b:
                problems.append(f"README.md recursion with no base case: {b[:60]}")

    summary = f"{loops} while loops, {recursions} recursions, {waits} waits checked"
    return (not problems), ([summary] + problems)


if __name__ == "__main__":
    ok, out = run(sys.argv[1])
    print("ENDS ✓" if ok else "ENDS ✗", "\n  ".join([""] + out))
    sys.exit(0 if ok else 1)
