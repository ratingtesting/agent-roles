#!/usr/bin/env bash
# graphify-setup.sh — idempotent setup for graphify on 9router + oc/nemotron-3-ultra-free
# Run: bash graphify-setup.sh
set -euo pipefail

echo "== [1/5] Install graphifyy =="
uv tool install graphifyy || echo "graphifyy already installed"

echo "== [2/5] Verify 9router + oc/nemotron-3-ultra-free =="
if [ -z "${API_9ROUTER_KEY:-}" ]; then
  echo "ERROR: API_9ROUTER_KEY not set. Export it before running." >&2
  exit 1
fi
curl -s http://localhost:20128/v1/chat/completions \
  -H "Authorization: Bearer $API_9ROUTER_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: OpenAI/Python 1.68.2" \
  -d '{"model":"oc/nemotron-3-ultra-free","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' \
  | head -c 200
echo ""

echo "== [3/5] Write ~/.bash_profile.d/graphify.sh (helper function) =="
mkdir -p ~/.bash_profile.d
cat << 'EOF' > ~/.bash_profile.d/graphify.sh
graphify-nemo() {
  export OPENAI_BASE_URL="http://localhost:20128/v1"
  export OPENAI_API_KEY="${API_9ROUTER_KEY}"
  export OPENAI_MODEL="oc/nemotron-3-ultra-free"
  "${HOME}/.local/bin/graphify" extract "$@" --backend openai --model "${OPENAI_MODEL}"
}
EOF

echo "== [4/5] Update ~/.bash_profile (global OPENAI_* + loader, deduped) =="
# Remove any old loader lines to avoid duplicates
grep -v 'bash_profile.d/\*.sh' ~/.bash_profile > ~/.bash_profile.tmp 2>/dev/null || true
# Prepend global OPENAI_* so direct graphify extract also uses 9router (not freellmapi auto-detect)
{
  echo '# graphify: default backend -> 9router + oc/nemotron-3-ultra-free'
  echo 'export OPENAI_BASE_URL="http://localhost:20128/v1"'
  echo 'export OPENAI_API_KEY="${API_9ROUTER_KEY}"'
  echo 'export OPENAI_MODEL="oc/nemotron-3-ultra-free"'
  echo '# load per-tool helper functions (graphify-nemo, etc.)'
  echo 'for f in ~/.bash_profile.d/*.sh; do [ -f "$f" ] && source "$f"; done'
} > ~/.bash_profile
rm -f ~/.bash_profile.tmp

echo "== [5/5] graphify hermes install (writes AGENTS.md rules) =="
graphify hermes install
# Append explicit rule so agents never call graphify extract directly (freellmapi hijack)
AGENTS=~/AGENTS.md
RULE='- ALWAYS use the `graphify-nemo` helper (9router + oc/nemotron-3-ultra-free) for any extraction/clustering that needs the LLM. Do NOT call `graphify extract` directly — freellmapi auto-detect will hijack it to llama-3.3-70b. For query/path/explain/update (no LLM) direct `graphify` is fine. OPENAI_* env vars in ~/.bash_profile already point to 9router.'
if ! grep -qF 'graphify-nemo' "$AGENTS" 2>/dev/null; then
  printf '\n%s\n' "$RULE" >> "$AGENTS"
fi

echo "== DONE =="
echo "Test: cd <project> && source ~/.bash_profile && graphify-nemo . --no-cluster"
echo "Clustering (when >=80 files): graphify-nemo . --cluster --max-concurrency 1 --api-timeout 600"
echo ""
echo "Note for monorepos (lazy-unicorn): build per-subfolder graphs:"
echo "  cd /c/Projects/lazy-unicorn/app && graphify-nemo . --no-cluster"
echo "  cd /c/Projects/lazy-unicorn/marketplace && graphify-nemo . --no-cluster"
echo "Do NOT run on monorepo root — it includes foreign clones (openhands, ai-company, etc.)"