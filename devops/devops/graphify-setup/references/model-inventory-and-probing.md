# Model inventory & how to probe it (verified 2026-08-06)

Companion to `references/model-benchmark-for-extraction.md`. That file covers HOW to rank
models; this one covers WHICH models exist, WHERE they live, and the interaction rule that
matters more than either.

## Rule zero — ASK, do not enumerate

The user keeps the in-scope model list in their head and names models informally
("StepFun: Step 3.7 Flash", "HY3:free"). Those informal names do NOT map cleanly onto
provider ids, and the profile `config.yaml` contains hundreds of ids from unrelated
aggregators (`SuperCombo_*`, `kr/*`, `qd/*`, `openrouter/*`, `freellmapi/*`).

Enumerating them to "find what works" triggers a hard stop:
> «стоп!!! Ты делаешь фигню... ПЕРЕСПРОСИТЬ надо было!»
> «Ты не проверил все модели.»

Correct behaviour when a model name is ambiguous or the scope is unclear: ONE `clarify` call
listing what you found and asking which set is in scope. A guess costs ~100s per failed probe
and erodes trust; a question costs one turn.

Equally: when the user says "check all the models", they mean a specific list they hold.
Confirm the list before running anything.

## Two separate providers — do not conflate

| | 9router | Nous portal |
|---|---|---|
| Base URL | `http://127.0.0.1:20128/v1` | `https://inference-api.nousresearch.com/v1` |
| Auth | `API_9ROUTER_KEY` (env) | OAuth token, see below |
| Model prefix | `oc/` (OpenCode), `kr/`, `openrouter/`, `freellmapi/` | `stepfun/`, `tencent/`, ~354 total |
| `/v1/models` | TIMES OUT (use config.yaml or ask) | works, returns full list |

A model absent from one is not "broken" — it may simply live on the other. StepFun Step 3.7
Flash returns `401 ModelError` under every `oc/*` spelling because it is a Nous-portal model.

### Reading the Nous portal token

Never hand-type credentials; read them from the profile auth file:

```python
import json, os, urllib.request
p = os.path.expanduser("~/AppData/Local/hermes/profiles/<profile>/auth.json")
n = json.load(open(p, encoding="utf8"))["providers"]["nous"]
tok, base = n["access_token"], n["inference_base_url"]
req = urllib.request.Request(base + "/models",
        headers={"Authorization": "Bearer " + tok, "User-Agent": "hermes-cli/1.0"})
ids = [m["id"] for m in json.loads(urllib.request.urlopen(req, timeout=60).read())["data"]]
```

Pitfalls: the token expires roughly hourly (`expires_at`) — refresh by using Hermes normally.
Omitting `User-Agent` can yield `403 error code: 1010`. `hermes model` (singular, no
subcommand) prints the active provider; `hermes models` / `model list` are not valid commands.

## Verified results — strict-JSON + Cyrillic probe

| Model | Provider | Verdict |
|---|---|---|
| `oc/deepseek-v4-flash-free` | 9router | OK — chosen default |
| `stepfun/step-3.7-flash:free` | Nous portal | OK |
| `oc/laguna-s-2.1-free` | 9router | OK but consistently thinner coverage |
| `tencent/hy3:free` | Nous portal | OK, slow (~49s on real task) |
| `oc/nemotron-3-ultra-free` | 9router | rich output, unreliable delivery (2/5) |
| `oc/mimo-v2.5-free` | 9router | HTTP 200 but empty `content` |
| `oc/ling-3.0-flash-free` | 9router | `400` — removed upstream |
| `stepfun/step-3.7-flash`, `tencent/hy3`, `tencent/hy3-preview` | Nous portal | `404 requires available credits` — paid tiers |

`:free` suffix on the Nous portal marks the no-credit tier. The paid twin returns 404, not 402.

## Reusable probe harness

Handles all three response shapes (single JSON, SSE, concatenated JSON) and reasoning models.

```python
import json, re
dec = json.JSONDecoder()

def content(raw):
    raw = raw.strip()
    if raw.startswith("data:"):                       # SSE
        out = ""
        for line in raw.splitlines():
            if line.startswith("data: ") and "[DONE]" not in line:
                try:
                    ch = json.loads(line[6:])["choices"][0]
                    out += (ch.get("delta") or ch.get("message") or {}).get("content") or ""
                except Exception:
                    pass
        return out
    try:
        return json.loads(raw)["choices"][0]["message"].get("content") or ""
    except Exception:                                  # concatenated objects
        out, i = "", 0
        while i < len(raw):
            try:
                o, j = dec.raw_decode(raw, i)
            except Exception:
                break
            ch = o.get("choices", [{}])[0]
            out += (ch.get("message") or ch.get("delta") or {}).get("content") or ""
            i = j
            while i < len(raw) and raw[i] in " \r\n":
                i += 1
        return out
```

Non-negotiables when probing:
- `max_tokens >= 8000` for reasoning models, else the reasoning phase eats the budget and
  `content` returns empty with `finish_reason=length` — a good model scored as broken.
- Build the body with `ensure_ascii=False` and encode UTF-8; never probe Cyrillic via inline
  `curl -d` in git-bash (mangles encoding, produces fake "Input garbled" replies).
- `content == ""` is a FAILURE, not a pass — check for the reasoning field to confirm why.
- Long benchmarks exceed the 600s foreground cap: write the harness to a file and run it with
  `terminal(background=True, notify_on_complete=True)`. Shell-level `nohup`/`&` is rejected.
