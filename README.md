# Memoryless Recursion Kit

Build AI-assisted workflows that don't depend on the assistant remembering, and check that they hold together.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24294504.svg)](https://doi.org/10.5281/zenodo.24294504)

This kit accompanies the white paper *Memoryless Recursions with a Provability Check: Files as the Only State in Human-in-the-Loop AI Workflows* (Sharma, 2026). The paper explains the method; this kit lets you run it.

It builds on the [TJ++ Logic Engine](https://github.com/abhi50188/tj-plus-plus-logic-engine), which checks the structure of a piece of text. This kit turns the same kind of structural checks onto the structure of a process.

---

## The idea in four lines

1. **Files are the only state.** Each step is triggered by the files the last step left, works from those files alone, and leaves files that trigger the next step.
2. **Rules are read on demand.** A step's rules are read just before that step, and the read's log is what lets the step start. A step that doesn't run never pays for its read.
3. **One approval, in code, before what can't be undone.** The script prints one sentence naming the action; you paste it back; code checks it word for word.
4. **The system checks itself.** Every loop ends, every documented step has a matching print, the docs agree with the code, and every program actually rewinds to its base case.

## The ideas, in plain words

**Memoryless.** No step remembers anything. Each one looks at the files, does its one job, and leaves a file behind. Pick it up tomorrow, or in a new session, and the files alone say what's next.

**Recursion.** A chain of levels where each level needs the level below it and punts its result up to the level above. The punt is the trigger: it's what makes the next level run. Pull out any level and the chain stops.

**List.** Steps that don't need each other. They sit side by side, and someone has to remember to run each one. A list is fine only when it's declared on purpose (a checklist); otherwise it's a gap.

**Base case.** The finish line, written down: the point where there's nothing left to do, and the program says so.

**Written outside in, proven inside out.** Code is written top down: start from what you want delivered, ask what that needs, then what that needs, down to where the work comes in. Shape files are written the same way, outermost level first. The proof runs the other way, because a recursion must rewind: from the innermost level out, each level punting up to the next. Two questions, two directions. Designing asks what each level needs. Proving asks whether each level triggers the next.

**The read level.** Read the instructions for a job right before doing that job, not all of them at the start of the day. A job that doesn't run today never costs a read.

**The handshake.** Before anything that can't be undone, the program prints one sentence saying exactly what it's about to do. You paste it back. That paste is the only "yes" it asks for.

**Ends.** Every loop has a way out, and every chain has a finish line. Nothing can run forever.

**Cancel.** The README read forwards against the code read backwards. Forwards is each step the README says happens, heading out. Backwards is what the code prints as each step releases. Like a shopping list next to the receipt, the two must cancel: every step on the list has a line on the receipt, and every line on the receipt is on the list. Anything left over, and the check stops.

**Sync.** The docs and the code tell the same story. If the docs say the limit is 5, the code says 5.

**Rewind.** The proof step. It also reads the code backwards, the way a recursion returns, from the innermost level out, but it checks something else: the punts. Each level does its job and punts its file up, and the punt triggers the level above. For every level the question is: does the level above need this, or could this level exist on its own? A level that could stand on its own is a list, not a recursion. If every level is required by the one above, with no gaps, no circles and nothing handed over by memory, it rewinds.

**Why both cancel and rewind.** Both read the code backwards, but they ask different questions. Cancel asks: do the code and the README agree, step for step? Rewind asks: is each level required by the level above? Steps can match the README perfectly and still be a list, and levels can each be required and still not match the README. Each catches what the other can't.

**Take-away.** Rewind shows each level *points to* the file it gets from below. Take-away proves the level above *can't run without it*: hide the file, run the level, and it must stop. That's the "required" part of rewind, tested for real.

**Pairs.** A check that compares something with itself always passes and proves nothing. Every check has to compare two different things.

**Proven.** Ends, cancel, sync, rewind and pairs all pass. That proves the shape: it ends, it connects, it rewinds, and it matches its docs. It doesn't prove every step does the right thing. Real runs still show that, and the take-away test is run whenever a script changes.

---

## Quick start

```
git clone https://github.com/abhi50188/memoryless-recursion-kit
cd memoryless-recursion-kit
python3 prove.py            # runs every check on the sample workflow
```

You should see a scorecard with every row passing. Then watch each check fail on a broken copy of the sample:

```
python3 prove.py --example broken/no_limit     # a loop with no way out → Ends stops
python3 prove.py --example broken/no_print     # a documented step nothing prints → Cancel stops
python3 prove.py --example broken/wrong_fact   # the README and the code disagree → Sync stops
python3 prove.py --example broken/self_pair    # a check against itself → Pairs stops
python3 prove.py --example broken/list         # a level that hands to nobody → Rewind says List
python3 prove.py --example broken/memory       # a hand-off made in chat → Rewind says MEMORY
python3 prove.py --example broken/not_in_code  # a hand-off the code doesn't have → Rewind says NOT IN CODE
```

Each broken copy changes one file and trips one check. For rewind, the result is a failure mode, named for what went wrong: List, MEMORY, NOT IN CODE, LOOP, DOESN'T LAND or BROKEN. Then the take-away test:

```
python3 checks/takeaway.py    # takes each handed-up file away in a throwaway copy; the level above must stop
```

Or walk the sample by hand, one step at a time, as its README describes (`sample/README.md`).

Python 3.9 or later. No other packages needed.

---

## What's in here

| Path | What it is |
|---|---|
| `sample/` | A small workflow over made-up documents, written as a memoryless recursion: fetch → save → read → outer → build → deliver |
| `sample/shape.txt` | The sample's shape, one line per level |
| `sample/README.md` | The sample's documentation, in the fixed form the checkers compare against the code |
| `sample/rules.md`, `sample/rules_index.txt` | The sample's rules and the index that says which rules each kind of work reads |
| `checks/ends.py` | Every loop is bounded, every recursion names its base case, every wait is a named stop |
| `checks/cancel.py` | Each step the README lists has a matching line a script prints, and the reverse |
| `checks/sync.py` | The README agrees with itself and with facts read from the code |
| `checks/rewind.py` | Reads a shape file and says whether it rewinds; `--design` checks a shape before any code exists |
| `checks/pairs.py` | No comparison in the code reads the same cell on both sides |
| `checks/takeaway.py` | The take-away test: each level stops when its file is taken away |
| `parts/read_log.py` | The read level: print the next rules section, log it in your own words, start the step when none are left |
| `parts/handshake.py` | The +1 handshake: print the sentence, check the paste word for word |
| `prove.py` | Runs every check and prints the scorecard (a declared checklist) |
| `broken/` | Seven broken copies of the sample, each changing one file, each with a note saying what breaks |

---

## What each check does

| Check | Reads | Compares against | Stops when |
|---|---|---|---|
| Ends | The code | Its own loops and waits | A loop has no limit, a recursion names no base case, or a wait isn't a named stop |
| Cancel | The steps the README lists | What the scripts print when a step finishes | A step has no print, or a print has no step |
| Sync | The README | Itself, and facts read from the code | Two statements disagree, a named script is missing, or a stated limit isn't the code's limit |
| Rewind | The shape file | The files each level's script actually reads | A level hands up nothing (List), hands up in chat (MEMORY), or claims a hand-off the code doesn't have (NOT IN CODE) |
| Pairs | Every comparison in the code | The cell each side reads | Both sides read the same cell |
| Take-away | Each hand-off in the shape | The level above, run without its file | The level above runs anyway |

The checks prove **structure, not correctness**: the system ends, connects, rewinds and matches its docs. Whether each step does the right thing is still for live runs to show.

---

## Use it on your own workflow

1. **State the recursion before you write code:** n (what's left, read from a file), one step, and the base case.
2. **Write the shape file** the way code is written, outside in: outermost level first, one line per level. (The proof will read it inside out.)

   Each line: the level, the script(s) that run it, and what it gets from which level below.

   ```
   deliver  | deliver.py | gets "batch.json" from build    | delivers
   build    | build.py   | gets "due.json" from outer
   outer    | outer.py   | gets "saved" from inner         | repeats over "pull.json"
   inner    | inner.py   | gets "pull.json" from fetch
   fetch    | fetch.py   | from outside: the source
   ```

3. **Check the design before building it:** `python3 checks/rewind.py shape.txt --design`. It answers "Rewinds," or names where it breaks.
4. **Write the README's steps,** and have each script print a fixed line when its step finishes.
5. **Run `python3 prove.py --example <your folder>`,** fix what it names, and rerun until it's clean.
6. **When a script changes,** run the take-away test: `python3 checks/takeaway.py <your folder>`. In a throwaway copy, it removes each file a level receives, runs the level above, and confirms it stops.

---

## Citation

Sharma, A. (2026). *Memoryless recursions with a provability check: Files as the only state in human-in-the-loop AI workflows.* Zenodo. https://doi.org/10.5281/zenodo.24294504

## License

The code is under the MIT License (see `LICENSE`), © 2026 Abhishek Sharma. The white paper is under CC BY 4.0.
