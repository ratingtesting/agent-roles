# Benchmarking models for graph/JSON extraction

Purpose: pick the extraction model for `graphify` (or any strict-JSON extraction job) on
evidence instead of a single latency ping.

## Why one ping lies
A trivial prompt ("say ok") returns in ~2s even from a heavy reasoning model, while the real
extraction job from the same model takes ~40s. Ranking on the ping picks the wrong model.
Worse, an unlucky single run can make a good model look broken.

## Rank by delivery rate, not peak quality
For a batch run across a repo, an intermittently failing model is useless even if its best
output is the richest. Order of criteria:
1. **Delivery rate** — successful strict-JSON parses out of N runs.
2. **Coverage** — how many known key entities appear in the graph.
3. **Dangling edges** — edges whose endpoints are not in `nodes`.
4. **Latency** — mean, min, max (report the spread; means hide 90s outliers).

## Harness rules learned the hard way
- `max_tokens >= 8000`. At 1200 a reasoning model spends the whole budget on the reasoning
  phase and returns `content: None` with `finish_reason: length`. That is a harness bug, not
  a model failure. Always print `finish_reason` and the message keys when content is empty.
- Handle three response shapes: single JSON object; SSE (`data: {...}` lines, terminated by
  `data: [DONE]`); several concatenated JSON objects on one line. Use a
  `json.JSONDecoder().raw_decode` loop plus an SSE branch, accumulating
  `choices[0].message.content` or `.delta.content`.
- Build the request body with `ensure_ascii=False` and `.encode("utf8")` for Cyrillic prompts.
- Strip a possible ```json fence before parsing, then locate the first `{`.
- `temperature=0` and identical prompt across models; run >=5 times to expose flakiness.
- Long benchmarks exceed the 600s foreground cap: write the harness to a `.py` file and run
  it with `terminal(background=True, notify_on_complete=True)`, printing a per-run progress
  line with `flush=True` so you can poll it.

## Scoring snippet
```python
ids = {x.get("id") for x in nodes if isinstance(x, dict)}
coverage = len([k for k in KEY_ENTITIES if any(k in str(i) for i in ids)])
dangling = sum(1 for e in edges
               if isinstance(e, dict) and (e.get("from") not in ids or e.get("to") not in ids))
```

## Result 2026-08 (9router `oc/*` + Nous portal), 5 runs each
| Model | JSON delivery | Mean latency | Coverage /5 |
|---|---|---|---|
| `oc/deepseek-v4-flash-free` | 5/5 | 9.5s | 5,5,5,5,4 |
| `tencent/hy3:free` (Nous) | 4/5 | 49.5s | ERR,5,5,5,5 |
| `oc/nemotron-3-ultra-free` | 2/5 | 18.3s | ERR,5,5,ERR,ERR |

Chosen: `oc/deepseek-v4-flash-free`. Nemotron kept as `graphify-nemo` fallback — richer graph
(19-21 nodes vs 11-14) on the runs it completed, but 3 of 5 died at ~0.8s.

## Endpoint notes
- Nous portal: base URL and OAuth token live in `<profile>/auth.json` under
  `providers.nous` (`inference_base_url`, `access_token`). `/v1/models` works there (354
  models). Free variants carry a `:free` suffix; paid ids return 404 with
  "requires available credits".
- 9router (localhost:20128): `/v1/chat/completions` works, but `/v1/models` can hang —
  a models-endpoint timeout is NOT evidence the backend is down.
- Model ids are provider-tier specific: a model may exist under `freellmapi/<name>` but not
  under `oc/<name>`. Do not assume a prefix; ask for the list.
