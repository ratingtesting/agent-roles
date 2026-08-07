# Pitfalls — concrete before/after

Every long-horizon context loop hits these. Each is shown as the broken version
and the fix.

## 1. Unbounded summary nesting (THE big one)
**Broken** — a rolling summary string that prepends itself:
```python
self.summary = f"[{stamp}] prev summary: {self.summary}\ncompacted {n} lines -> {digest}"
```
This grows **linearly** with iterations. After 30 compactions the `summary`
field is 22 nested `"prev summary:"` lines long. The carried context is
unbounded → the whole strategy fails.

**Fixed** — make the summary a *capped data structure*, never an accumulating
string:
```python
self.digests.append(digest)
if len(self.digests) > SUMMARY_KEEP:      # e.g. 3
    self.digests = self.digests[-SUMMARY_KEEP:]
```
Carried size then plateaus (~1000 chars) and stays flat for any N.

## 2. Recursive reference nesting
**Broken** — each new line references the previous line *including its own
reference suffix*, so parens stack forever:
```python
last = ctx.window[-1].split(":")[-1].strip()
ref = f" (building on: {last})"
# -> iter=01 ... (building on: iter=00 ...)))))  infinite ')' growth
```
**Fixed** — read only the canonical stem of the previous item:
```python
prev = ctx.window[-1].split(" (building on")[0]
ref = f" (building on: {prev})"
```

## 3. Term-counter noise
**Broken** — counting tokens over the full line including the reference
scaffold double-counts and pollutes the frequency table with the word
`(building`:
```python
for w in ln.lower().split(): ...
# cumulative_terms contains '(building': 21, ...
```
**Fixed** — strip the scaffold before tokenizing:
```python
ln = ln.split(" (building on")[0]
for w in ln.lower().split(): ...
```

## 4. Resume double-counts / replays
**Broken** — `run(resume=True)` replays from iter 0, re-adding folded work, and
with a seeded RNG the stream diverges from the checkpoint.

**Fixed** — continue from `total_appended` AND re-prime the RNG by consuming the
same draws:
```python
start = ctx.total_appended
for _ in range(start):
    rng.choice(_topics)      # mirror make_line's draw order exactly
    rng.randint(0, 99)
```
Verify: after a full run, resume and confirm `total_appended` is unchanged and
carried size is identical.
