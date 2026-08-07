# Probing models across multiple routers (9router / Nous Portal / freellmapi)

How to verify *which model ids actually work* when several routers are configured
and their catalogs overlap. Written after a session where the agent shotgun-tested
arbitrary model names and got corrected.

---

## 0. RULE: ask which models before probing

**Do not enumerate the whole catalog.** `config.yaml` for a multi-router profile can
list 400+ ids across `SuperCombo_*`, `kr/*`, `oc/*`, `openrouter/*`, `freellmapi/*`.
Probing them all burns minutes, hits upstream rate limits (`ResourceExhausted:
Worker local total request limit reached`), and produces noise the user did not ask for.

When the user says "check the models", ask **which set** before firing requests.
In this environment the answer was: only the OpenCode (`oc/*`) models on 9router plus
two models on the Nous Portal — a list of 7, not 400.

User's exact correction: *"9 роутер — это провайдер... ты проверяешь не все модели,
а только от ОПЕНКОДА... ПЕРЕСПРОСИТЬ надо было!"*

## 1. Provider taxonomy (do not conflate)

| Surface | What it is | Base URL | Auth |
|---|---|---|---|
| **9router** | local LLM router (a provider) | `http://localhost:20128/v1` | `API_9ROUTER_KEY` |
| `oc/*` | OpenCode models **served through** 9router | same as above | same |
| `kr/*`, `SuperCombo_*`, `qd/*` | other upstreams behind 9router | same | same |
| **Nous Portal** | separate first-party provider, OAuth | `https://inference-api.nousresearch.com/v1` | OAuth token in `auth.json` |
| `9router-proxy/` | Node shim for LiteLLM tools (OpenHands etc.) | `:20129` | — |

Pitfall that cost a full detour: the `9router-proxy/` directory is **not** needed to
talk to 9router. It only exists to strip the `openai/` prefix for LiteLLM clients.
Talk to `:20128` directly.

Second pitfall: a model can exist under one router and not another. `StepFun Step 3.7
Flash` is **not** an OpenCode model — probing `oc/stepfun-step-3.7-flash*` returns
`401 ModelError: Model ... not found`. It lives on the Nous Portal as
`stepfun/step-3.7-flash:free`. Same family also reachable via
`freellmapi/stepfun-step-3.7-flash` on 9router. Ask which route the user means.

## 2. Enumerating Nous Portal models (works)

`hermes model` shows only the provider menu, not model ids. Read the OAuth token
straight out of the profile's `auth.json`:

```python
import json, urllib.request
d = json.load(open("<HERMES_HOME>/profiles/<profile>/auth.json", encoding="utf8"))
n = d["providers"]["nous"]
req = urllib.request.Request(
    n["inference_base_url"] + "/models",
    headers={"Authorization": "Bearer " + n["access_token"]})
ids = [m["id"] for m in json.loads(urllib.request.urlopen(req, timeout=60).read())["data"]]
```

Returned 354 ids. Filter client-side (`if "step" in i.lower()`), do not probe blindly.

Notes:
- `access_token` expires ~hourly (`expires_at` in the same file); `agent_key` is a
  separate longer-lived credential. Try `access_token` first.
- A bare `403 / error code 1010` from the portal is a Cloudflare UA block — add
  `User-Agent: hermes-cli/1.0` and `Accept: application/json`.
- `:free` suffix matters. `stepfun/step-3.7-flash` (paid) returns
  `404 ... requires available credits`, while `stepfun/step-3.7-flash:free` works.

## 3. 9router quirks when probing

- **`GET /v1/models` hangs** (curl exit 28 / `TimeoutError`) even though
  `POST /v1/chat/completions` answers in ~2s. Do not conclude the router is down —
  probe with a real chat call. Check liveness with
  `netstat -ano | grep 20128` (LISTENING) instead.
- **Responses are not a single JSON object.** Depending on the upstream you get
  either concatenated JSON objects or an SSE `data: {...}` stream with a trailing
  `data: [DONE]`. Plain `json.loads` fails with
  `JSONDecodeError('Extra data: line 1 column 800')` — which looks like a model
  failure but is a *parsing* failure. Use a tolerant reader:

```python
dec = json.JSONDecoder()
def content(raw):
    raw = raw.strip(); out = ""
    if raw.startswith("data:"):
        for line in raw.splitlines():
            if line.startswith("data: ") and "[DONE]" not in line:
                try:
                    ch = json.loads(line[6:])["choices"][0]
                    out += (ch.get("delta") or ch.get("message") or {}).get("content") or ""
                except Exception: pass
        return out
    i = 0
    while i < len(raw):                       # concatenated objects
        try: o, j = dec.raw_decode(raw, i)
        except Exception: break
        ch = o.get("choices", [{}])[0]
        out += (ch.get("message") or ch.get("delta") or {}).get("content") or ""
        i = j
        while i < len(raw) and raw[i] in " \r\n": i += 1
    return out
```

- **Cyrillic:** send the body with `json.dumps(..., ensure_ascii=False).encode("utf8")`
  from Python. Testing Cyrillic through `curl -d` in git-bash mangles the encoding and
  the model answers "Input garbled" — that is curl's fault, not the model's.

## 4. Probe payload that discriminates

Ask for strict JSON *and* Cyrillic in one shot, then assert both:

```
Верни ТОЛЬКО валидный JSON без пояснений: {"ok":true,"lang":"ru","note":"Разблокировка командой"}
```

Score `json = re.search(r'\{[^{}]*"ok"[^{}]*\}', c)` and `ru = "Разблокировка" in c`,
and record latency. Report as a table: model | provider | latency | json | ru | status.

Failure modes seen and how to read them:

| Symptom | Meaning |
|---|---|
| `401 ModelError: Model X` | id not offered by that router — wrong prefix/route |
| `404 No active credentials for provider: openai` | prefix omitted entirely |
| `404 ... requires available credits` | paid variant; try the `:free` twin |
| `502 ResourceExhausted: Worker local total request limit` | upstream saturated — retry later, not a bad id |
| HTTP 200 but empty `content` | reasoning-only model; text landed in a `reasoning` field |

## 5. graphify provider hijack (related)

`~/.graphify/providers.json` holding only a `freellmapi` entry makes
`graphify extract` auto-detect that backend and ignore the `OPENAI_*` env vars —
the semantic layer then silently fails to build when that endpoint is down (401).
`~/.bash_profile` + the `graphify-nemo` helper set the intended router, so **only the
helper works**; the direct command gets hijacked. Fix is to add the intended router to
`providers.json` as the default — but treat that file as user-owned config and get
explicit approval before writing it.
