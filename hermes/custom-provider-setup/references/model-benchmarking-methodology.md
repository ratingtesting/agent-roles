# Benchmarking candidate models (choosing a default, not just checking liveness)

Probing "does this id answer?" is `references/model-probing-multi-router.md`.
This file is the next step: the user has named a shortlist and asks
**"which is best?"** Written after a session where three separate methodology
errors produced three different wrong answers before the real ranking emerged.

---

## 0. A single ping is not a benchmark

First-pass numbers from one trivial prompt (`"скажи ок"`):

| model | ping |
|---|---|
| `oc/deepseek-v4-flash-free` | 2.1s |
| `oc/nemotron-3-ultra-free` | 13.4s |

Same models on the real task, 5 runs:

| model | mean | delivery |
|---|---|---|
| `oc/deepseek-v4-flash-free` | 9.5s | 5/5 |
| `oc/nemotron-3-ultra-free` | 18.3s (min 0.8, max 93.1) | **2/5** |

The ping ranked nemotron as "slow but fine". It is actually **unreliable** —
3 of 5 runs failed, and the failures returned in **0.8s**, which drags the mean
*down*. A fast mean can mean fast failures. Always report delivery rate
(`N ok / N total`) next to latency, and report min/max, not just mean.

## 1. PITFALL: `max_tokens` truncation reads as "the model is broken"

The single most expensive error of the session, hit **twice**.

Reasoning models spend the budget on hidden reasoning tokens *before* emitting
`content`. With `max_tokens=1200`, StepFun and hy3 both returned
`finish_reason: "length"` and `content: None` — scored as `NO-JSON`, i.e. failed.
They had not failed; the budget ran out mid-reasoning.

Diagnostic — dump the raw message before believing a failure:

```python
ch  = resp["choices"][0]
msg = ch["message"]
print(ch.get("finish_reason"), list(msg.keys()))
print(repr(msg.get("content"))[:200])
print(repr(msg.get("reasoning") or msg.get("reasoning_content"))[:250])
print(resp.get("usage"))     # completion_tokens_details.reasoning_tokens
```

`hy3:free` showed `finish=length`, `content=None`, `reasoning_tokens=2000` of a
2000 budget. Unambiguous truncation.

**Rule: give at least `max_tokens=8000` when benchmarking, and treat
`finish_reason == "length"` as an invalid run to re-measure, never as a model
defect.** Keys `reasoning` / `reasoning_details` in the message are the tell that
a model is reasoning-class.

## 2. PITFALL: your parser failing is not the model failing

`JSONDecodeError('Unterminated string...')` and `нет '{'` were both scored as
model failures. One was chunk-reassembly in the tolerant reader, one was an
overly narrow regex. Before recording ❌, print the raw body. A parse error and a
bad answer look identical in a results table and only one is the model's fault.

Guard the reader itself with a few fixtures rather than trusting it:
non-stream JSON, SSE with `[DONE]`, `content: null` + reasoning, concatenated
objects, empty body. Five asserts, runs in a second, catches exactly the class of
bug that corrupted two rounds here.

## 3. Use a task-representative probe

`{"ok":true}` proves liveness and nothing else. For a graphify/extraction default,
the probe was a small class with a repository, a wallet, a typed return, and a
branch — then score the *structure*, not just parseability:

- **coverage** — how many of the N known entities appear in `nodes`
- **dangling edges** — `from`/`to` not present in `nodes` (silent graph corruption)
- **cleanliness** — no ``` fences or "Вот JSON:" preamble
- **determinism** — same score across runs at `temperature=0`

Coverage is what separated the finalists. Latency did not:

| model | JSON | mean | coverage per run |
|---|---|---|---|
| `oc/deepseek-v4-flash-free` | 5/5 | 9.5s | 5,5,5,5,4 |
| `tencent/hy3:free` | 4/5 | 49.5s | —,5,5,5,5 |
| `oc/laguna-s-2.1-free` | 3/3 | 11.3s | 3,2,3 |
| `stepfun/step-3.7-flash:free` | 3/3 | 28.4s | 2,2,5 |

`laguna` is 4× faster and consistently drops the two *infrastructure* deps
(`CampaignRepository`, `TonWallet`) — the most valuable nodes in an architecture
graph. `stepfun` scored 2, 2, then 5 on an identical prompt at `temperature=0`:
non-deterministic, so a batch run is a lottery. Per-run scores expose this;
an averaged column would have hidden it.

**For a knowledge graph, completeness beats speed** — a missed node is a
permanent hole, while a slow batch just finishes later.

## 4. Run it in the background

5 runs × 3 models × a reasoning model that can take 93s exceeds the 600s
foreground cap. Write the harness to a file and use
`terminal(background=true, notify_on_complete=true)`, printing a per-run progress
line with `flush=True` so `process(action="wait")` shows advancement.
Shell-level `nohup`/`&` is rejected by the terminal tool. Note that
`process(action="wait")` clamps `timeout` to 60s per call — expect to poll repeatedly.

## 5. Report shape

Table of model | provider | delivery N/N | mean/min/max | per-run quality | verdict,
then name one winner and say *why the faster loser lost*. State the sample size and
the fact that it is one file — do not present a 5-run micro-benchmark as settled.
Do not carry a latency figure from the smoke test into the final table; re-measure
everything under the real task.
