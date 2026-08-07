# Verifying the LiteLLM ↔ router bridge

## 1. Proxy is listening
```
netstat -ano | grep :20129     # must show LISTENING; else the proxy is down
```

## 2. End-to-end request through the proxy
Send a non-streaming chat completion to the proxy with the `openai/<ns>/<model>` form.
Use curl or a Python urllib script (avoid shell-history leaks of the API key):

```python
import json, urllib.request
KEY = "<router-key>"   # from .bash_profile / .env
payload = json.dumps({
    "model": "openai/oc/deepseek-v4-flash-free",
    "messages": [{"role": "user", "content": "ping"}],
    "stream": False, "max_tokens": 5,
}).encode()
req = urllib.request.Request(
    "http://localhost:20129/v1/chat/completions",
    data=payload,
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("status", r.status, r.read().decode()[:200])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:300])
```

## 3. Read the proxy log
Expect one line per proxied request:
```
[bridge] rewrote model -> oc/deepseek-v4-flash-free
```

## Interpretation
- **429 Rate limit** or a real completion from the upstream = SUCCESS. The `openai/` prefix was
  stripped and `<ns>/<model>` reached the router. The "LLM Provider NOT provided" problem is solved.
- **litellm.BadRequestError: LLM Provider NOT provided** in the response = STILL BROKEN: the client is
  either hitting the router directly (Base URL wrong) or the proxy isn't stripping the prefix.

## Note on streaming (T4 in the original run)
Open a streaming request (`"stream": True`) and confirm you get the first SSE chunk without a 5xx from
the proxy. A 429 here is still a PASS (reached the router); only a LiteLLM prefix error is a failure.
