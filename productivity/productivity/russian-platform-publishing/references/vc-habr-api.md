# habr.ru / vc.ru API & auth reference

## habr.ru
- Account status comes from the profile/settings API. Read these BEFORE prescribing fixes:
  - `groups: ["readonly"]` -> account is read-only.
  - karma number (e.g. profile shows "1 Карма, read-only").
- ReadOnly is DEFAULT for new accounts (no invite). It is NOT caused by negative karma.
  Confirmed via real profile fetch: account `ratingtesting` showed karma +1 yet status read-only,
  registered "today". So "reset karma" advice is WRONG here.
- Sandbox (the path to a full account): https://habr.com/ru/sandbox/new/
  Passing moderation -> account becomes "полноправный" automatically.
- NO working submission API found. Tried and failed (404/301/401):
  - POST https://habr.com/api/v2/posts -> 401
  - GET  https://habr.com/ru/post/new -> 301
  - POST https://habr.com/ru/v1/publications/post/ -> 404
  - /ru/sandbox/new/ returns 200 HTML (SPA, no API in markup).
  => Submission is manual via the web form only.

## vc.ru
- Editor endpoint (from JS bundle index-*.js of vc.ru):
  - `POST https://api.vc.ru/v2.4/editor`  (v2.10 also valid)
  - body: `{"entry": JSON.stringify(entryObj)}`
  - publish: `POST https://api.vc.ru/v2.4/editor/{id}/publish`
  - auth uses `auth:"strict"`.
- entryObj minimal shape:
  {
    "id": 0, "user_id": 0, "type": 1, "subsite_id": 0,
    "title": "...",
    "entry": { "blocks": [ { "type": "text", "data": { "text": "<p>html</p>" } } ] },
    "external_access_link": "", "path": "",
    "is_editorial": false, "is_advertisement": false, "is_enabled_comments": true
  }
- AUTH FAILURE (verified twice with fresh full cookie export):
  Sent all 11 cookies (osnova-remember, auth-refresh-remember, osnova-aid,
  _ym_uid, _ym_d, _ym_isad, account:is-ads-disabled:v2, auth:is-session-saved:v2,
  fingerprint, pwa_disabled_90, stickydude).
  Response: 401 {"message":"Кажется у вас нет доступа к этому разделу, попробуйте раздел получше","error":{"code":401}}
  => vc.ru needs an `access_token` from the browser's localStorage, not cookies.
  Cookie export alone CANNOT publish to vc.ru.

## What worked elsewhere (prefer real tokens)
- HF Space: huggingface_hub SDK with API_HUGGINGFACE_KEY.
- dev.to: PUT /api/articles/{id} with API_DEV_TO_KEY.
- GitHub: gh CLI (token from `~/bin/gh auth status --show-token` or hosts.yml).
Lesson: for automated publishing prefer a real API token over cookie export.

## Publish URLs to hand the user
- habr: https://habr.com/ru/sandbox/new/   (title in its own field, body pasted in form)
- vc:   https://vc.ru/editor
