# Sample workflow

A small memoryless recursion over made-up documents. Each step is triggered by the file the step before it left, works from files alone, and leaves a file for the next step. The checkers in `../checks/` compare this README against the code, so its steps, recursions and facts are written in a fixed form.

## Steps

Run them in this order. Each prints its line when it finishes.

1. fetch (`fetch.py`) → `FETCH ✓`
2. save (`save.py`) → `SAVE ✓`
3. read (`read.py`, then log each section with `../parts/read_log.py`) → `READ ✓`
4. outer (`outer.py`) → `OUTER ✓`
5. build (`build.py`) → `BUILD ✓`
6. deliver (`deliver.py`, then the +1 paste) → `DELIVER ✓`

Run the whole thing again and nothing is due: outer prints `BASE CASE ✓`.

## Recursions

- fetch: n = files in source/ not yet in the pull. One step: add one. Base: nothing new.
- save: n = files in the pull not yet saved. One step: copy one. Base: all in place.
- read: n = sections of the work index not yet logged. One step: read one, log it in your own words. Base: none left → `READ ✓`.
- outer: n = saved files not yet in the record. One step: mark one due. Base: none left → `BASE CASE ✓`.

## Stops

The only waits on a person: the +1 paste before delivery, and each read log line.

## Facts

- `BATCH_LIMIT = 5`
