# Supabase MCP Setup via Header Auth

## Problem

`hermes mcp add supabase --auth oauth` fails with "redirect_uri not allowed" because Supabase OAuth requires a pre-registered redirect URI (Hermes uses `http://127.0.0.1:XXXXX/callback` by default, which isn't whitelisted).

## Solution: Header Auth with Service Role Key

Supabase MCP (`https://mcp.supabase.com/mcp`) supports Bearer token auth via `Authorization` header.

### Via hermes config (preferred)

```bash
# Set header auth with environment variable substitution
hermes config set mcp_servers.supabase-app.url "https://mcp.supabase.com/mcp"
hermes config set mcp_servers.supabase-app.headers.Authorization "Bearer \${SUPABASE_APP_SERVICE_ROLE_KEY}"
hermes config set mcp_servers.supabase-app.timeout 30
```

This produces config.yaml entry:

```yaml
mcp_servers:
  supabase-app:
    url: "https://mcp.supabase.com/mcp"
    headers:
      Authorization: "Bearer ${SUPABASE_APP_SERVICE_ROLE_KEY}"
    timeout: 30
```

Key env vars must live in `~/.hermes/.env` — Hermes does `${VAR}` substitution at connect time.

### What not to do

- `hermes mcp add supabase --auth oauth` — will hang on OAuth callback that Supabase rejects
- `hermes mcp add supabase --auth header` — interactive mode times out in non-interactive sessions
- Patching config.yaml directly — patch tool refuses to write to config files (security)

## Multi-project Setup

Each Supabase project needs its own MCP server entry with its own key:

```bash
hermes config set mcp_servers.supabase-app.headers.Authorization "Bearer \${SUPABASE_APP_SERVICE_ROLE_KEY}"
hermes config set mcp_servers.supabase-marketplace.headers.Authorization "Bearer \${SUPABASE_MARKETPLACE_SERVICE_ROLE_KEY}"
```

## Verification

```bash
hermes mcp list
# Should show both servers with Status: enabled
```
