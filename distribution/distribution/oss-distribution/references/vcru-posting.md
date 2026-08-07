# vc.ru / Osnova — reverse-engineered posting endpoint

Discovered by reading the SPA bundle `https://vc.ru/assets/index-DClEFwrC.js`. vc.ru is part of the Osnova network (DTF/TJournal/etc.); the pattern below is the same across the family.

## Key URLs
- `/new` and `/settings` are SPA routes that render the **feed**, NOT a compose form. Do not probe them for a form.
- The real compose editor is at `https://vc.ru/editor` — it returns a full editor page (~509 KB HTML), not a feed.
- The JS bundle reveals the transport class. Endpoint base: `https://api.vc.ru/{version}/editor`
  - Working versions: `v2.4`, `v2.10` (these return 401 when unauthenticated, proving the route exists).
  - `v3.4` is auth-only and returns 404 for `/editor`. `v1`/`v2`/`v3` (no dot) return 404.

## Create / save a draft
```
POST https://api.vc.ru/v2.4/editor
Content-Type: application/json
Cookie: <osnova-* cookies>

{ "entry": "<JSON-stringified entry object>" }
```
**Gotcha: double encoding.** The `entry` field is a JSON *string* nested inside the outer JSON object. Build it as:
```python
payload = json.dumps({"entry": json.dumps(entry, ensure_ascii=False)}, ensure_ascii=False).encode("utf-8")
```

## Publish
```
POST https://api.vc.ru/v2.4/editor/{id}/publish
```
Body can be empty. Sets `isPublished: true`.

## Entry object shape (from bundle `zd` default + `convertEntryDataToApiFormat`)
```json
{
  "id": 0,
  "user_id": 0,
  "type": 1,
  "subsite_id": 0,
  "title": "Заголовок",
  "entry": { "blocks": [ { "type": "text", "data": { "text": "<p>Абзац</p><p>Абзац</p>" } } ] },
  "external_access_link": "",
  "path": "",
  "is_editorial": false,
  "is_advertisement": false,
  "is_enabled_comments": true
}
```
Block text is HTML (wrap paragraphs in `<p>`). For a markdown source, convert each non-empty line/paragraph to `<p>...</p>`.

## Status-code interpretation
- `404` → wrong URL or version. Keep hunting versions (`v2.4`/`v2.10`), do NOT spam `/api/v1/posts/`, `/entries/`, `new-post`, etc.
- `401 "Кажется у вас нет доступа..."` → **correct route, auth rejected.** The exported cookies are stale or insufficient for `auth:"strict"`.
  - Fix attempt: re-export cookies from a *fresh* login (Cookie-Editor) and retry.
  - If 401 persists even with all cookies, the account may lack posting rights, or Osnova rejects exported sessions for the editor scope — fall back to manual posting or a different account.

## Cookie set (Cookie-Editor export from vc.ru)
`osnova-remember`, `auth-refresh-remember`, `osnova-aid`
Send ALL cookies (not just these three) — the session may carry more.

## Why this matters
The skill's old policy said "find the internal /api/... endpoint" — but the endpoint is NOT under `/api/` on the main host; it is `api.vc.ru/v2.4/editor`. Guessing `/api/v1/...` wastes quota. Use the above directly.
