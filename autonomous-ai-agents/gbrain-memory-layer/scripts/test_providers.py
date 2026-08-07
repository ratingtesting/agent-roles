# -*- coding: utf-8 -*-
"""Cyrillic-safe probe: FlashRank reranker + 9router chat models.
Run: python test_providers.py  (MSYS curl mangles Cyrillic bodies — that's why this exists)"""
import json, time, urllib.request, subprocess

def winenv(name):
    return subprocess.run(["powershell.exe","-NoProfile","-Command",
        f'[Environment]::GetEnvironmentVariable("{name}","User")'],
        capture_output=True, text=True).stdout.strip()

def post(url, body, headers=None, timeout=180):
    req = urllib.request.Request(url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type":"application/json", **(headers or {})})
    t0 = time.time()
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8")
    except Exception as e:
        try: raw = e.read().decode("utf-8")
        except Exception: raw = str(e)
    return time.time()-t0, raw

def parse_chat(raw):
    """Handles plain JSON, SSE, and concatenated-JSON responses from 9router."""
    content = reason = ""; finish = err = None
    for line in raw.replace("data:", "\n").splitlines():
        line = line.strip()
        if not line or line == "[DONE]": continue
        try: obj = json.loads(line)
        except Exception: continue
        if obj.get("error"): err = obj["error"]
        for c in obj.get("choices", []):
            d = c.get("delta") or c.get("message") or {}
            content += d.get("content") or ""
            reason += d.get("reasoning") or d.get("reasoning_content") or ""
            finish = c.get("finish_reason") or finish
    return content, reason, finish, err

# --- FlashRank reranker (:8000, llama-server-wire-compatible) ---
dt, raw = post("http://127.0.0.1:8000/v1/rerank",
    {"query":"кот мяукает","documents":["собака лает","кошка издает мяу","солнечная погода"]})
print(f"FLASHRANK {dt:.1f}s -> {raw[:200]}")

# --- 9router chat models ---
K = winenv("API_9ROUTER_KEY")
prompt = "Ответь одним словом: работает"
for model in ["oc/nemotron-3-ultra-free"]:
    for i in range(3):
        dt, raw = post("http://localhost:20128/v1/chat/completions",
            {"model":model,"max_tokens":2000,"stream":False,
             "messages":[{"role":"user","content":prompt}]},
            {"Authorization":f"Bearer {K}"})
        c, rs, f, e = parse_chat(raw)
        print(f"{model} try{i+1}: {dt:.1f}s finish={f} content={c[:80]!r} err={e}")

# --- agentrouter direct (needs claude-cli UA) ---
AK = winenv("API_AGENTROUTER_KEY")
dt, raw = post("https://agentrouter.org/v1/messages",
    {"model":"claude-opus-4-8","max_tokens":20,"messages":[{"role":"user","content":prompt}]},
    {"x-api-key":AK,"anthropic-version":"2023-06-01",
     "User-Agent":"claude-cli/1.0.0 (external, cli)"})
try:
    d = json.loads(raw)
    print(f"AGENTROUTER {dt:.1f}s -> {(d.get('content') or [{}])[0].get('text') or d.get('error')}")
except Exception:
    print(f"AGENTROUTER {dt:.1f}s raw={raw[:200]}")
