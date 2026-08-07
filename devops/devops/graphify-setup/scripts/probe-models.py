#!/usr/bin/env python
"""Benchmark candidate extraction models on the REAL job (code-graph -> strict JSON).

Ranks by DELIVERY RATE first, richness second. A batch run over a repo is ruined by
intermittent failures, not by a slightly thinner graph.

Usage:
    python probe-models.py                 # default 5 runs per model
    RUNS=3 python probe-models.py

Edit MODELS below. Entries are (model_id, base_url_kind) where kind is "9router"
or "nous"; credentials are resolved automatically.

WHY THIS EXISTS (hard-won, do not regress):
  * A single short ping ranks models WRONG. Reasoning models answer a trivial prompt
    in ~2s and the real task in ~40s.
  * max_tokens must be >= 8000. At 1200 the reasoning phase eats the budget,
    `content` returns empty/None with finish_reason=length, and a good model
    scores as broken.
  * Responses arrive in THREE shapes: one JSON object, SSE `data:` lines, or several
    concatenated JSON objects on one line. All three are handled here.
  * Probe Cyrillic through Python with ensure_ascii=False -- NEVER inline `curl -d`,
    which mangles UTF-8 in git-bash and fakes an "Input garbled" model failure.
  * DO NOT enumerate every model id found in config.yaml. Only a small named subset
    is ever in scope. If you lack an explicit list, ASK the user first.

Run it in the BACKGROUND (terminal background=true, notify_on_complete=true):
5 models x 5 runs easily exceeds the 600s foreground timeout.
"""
import json
import os
import re
import time
import urllib.request

RUNS = int(os.environ.get("RUNS", "5"))

MODELS = [
    ("oc/deepseek-v4-flash-free", "9router"),
    ("oc/nemotron-3-ultra-free", "9router"),
    ("tencent/hy3:free", "nous"),
]

CODE = '''class UnlockCampaign:
    def __init__(self, repo: CampaignRepository, wallet: TonWallet):
        self.repo = repo; self.wallet = wallet
    def join(self, user: User, code: str) -> UnlockResult:
        team = self.repo.find_team(code)
        if team.size >= team.threshold:
            self.wallet.transfer(user.address, team.reward)
            return UnlockResult.SUCCESS
        return UnlockResult.PENDING
'''

PROMPT = (
    "Извлеки граф кода. Верни СТРОГО JSON без markdown и пояснений, схема:\n"
    '{"nodes":[{"id":"","type":"class|method|param"}],'
    '"edges":[{"from":"","to":"","rel":"calls|uses|returns"}]}\n\nКод:\n' + CODE
)

KEY_ENTITIES = {
    "UnlockCampaign", "join", "CampaignRepository", "TonWallet", "UnlockResult",
}

_dec = json.JSONDecoder()


def endpoints():
    """Resolve base URLs + tokens. Nous OAuth token lives in the profile auth.json."""
    out = {}
    key = os.environ.get("API_9ROUTER_KEY")
    if key:
        out["9router"] = ("http://127.0.0.1:20128/v1", key)
    auth = os.path.expanduser(
        "~/AppData/Local/hermes/profiles/app/auth.json"
    )
    if os.path.exists(auth):
        with open(auth, encoding="utf8") as fh:
            nous = json.load(fh)["providers"]["nous"]
        out["nous"] = (nous["inference_base_url"], nous["access_token"])
    return out


def content(raw):
    """Accumulate assistant text across all three response shapes."""
    raw = raw.strip()
    if raw.startswith("data:"):
        buf = ""
        for line in raw.splitlines():
            if line.startswith("data: ") and "[DONE]" not in line:
                try:
                    ch = json.loads(line[6:])["choices"][0]
                    buf += (ch.get("delta") or ch.get("message") or {}).get("content") or ""
                except Exception:
                    pass
        return buf
    try:
        return json.loads(raw)["choices"][0]["message"].get("content") or ""
    except Exception:
        buf, i = "", 0
        while i < len(raw):
            try:
                obj, j = _dec.raw_decode(raw, i)
            except Exception:
                break
            ch = obj.get("choices", [{}])[0]
            buf += (ch.get("message") or ch.get("delta") or {}).get("content") or ""
            i = j
            while i < len(raw) and raw[i] in " \r\n":
                i += 1
        return buf


def main():
    eps = endpoints()
    for model, kind in MODELS:
        if kind not in eps:
            print(f"{model:30} SKIP (no credentials for {kind})")
            continue
        base, token = eps[kind]
        lats, ok, covs, dangling = [], 0, [], []
        for _ in range(RUNS):
            body = json.dumps(
                {
                    "model": model,
                    "messages": [{"role": "user", "content": PROMPT}],
                    "max_tokens": 8000,      # >=8000: see module docstring
                    "temperature": 0,
                },
                ensure_ascii=False,          # never mangle Cyrillic
            ).encode("utf8")
            req = urllib.request.Request(
                base + "/chat/completions",
                data=body,
                headers={
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/json",
                    "User-Agent": "hermes-cli/1.0",
                },
            )
            t0 = time.time()
            try:
                raw = urllib.request.urlopen(req, timeout=300).read().decode("utf8", "replace")
                lats.append(time.time() - t0)
                text = re.sub(r"^```(?:json)?|```$", "", (content(raw) or "").strip(), flags=re.M).strip()
                obj, _ = _dec.raw_decode(text, text.find("{"))
                nodes, edges = obj.get("nodes", []), obj.get("edges", [])
                ids = {n.get("id") for n in nodes if isinstance(n, dict)}
                covs.append(len([k for k in KEY_ENTITIES if any(k in str(i) for i in ids)]))
                dangling.append(
                    sum(1 for e in edges if isinstance(e, dict)
                        and (e.get("from") not in ids or e.get("to") not in ids))
                )
                ok += 1
            except Exception:
                lats.append(time.time() - t0)
                covs.append("ERR")
        avg = sum(lats) / len(lats) if lats else 0
        print(
            f"{model:30} JSON {ok}/{RUNS}  avg {avg:6.1f}s  "
            f"key {covs}  dangling {dangling}",
            flush=True,
        )


if __name__ == "__main__":
    main()
