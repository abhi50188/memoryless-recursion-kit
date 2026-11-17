"""handshake.py: the +1 handshake, the one approval inside a running recursion.

Before an action that can't be undone, the script prints one exact sentence naming the action and its count.
The human approves by pasting that sentence back; code checks it word for word. Paste, check and act are one step.
One paste approves the whole batch it names.
"""
from pathlib import Path


def ask(work, n, what):
    sentence = f"I approve delivering {n} {what} now."
    (Path(work) / "handshake.txt").write_text(sentence)
    return sentence


def check(work, paste):
    saved = Path(work) / "handshake.txt"
    return saved.exists() and paste.strip() == saved.read_text().strip()
