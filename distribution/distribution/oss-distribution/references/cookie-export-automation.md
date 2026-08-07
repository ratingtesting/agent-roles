# Russian publishing: cookie-automation recipe

## Why this file exists
Hermes browser sessions are isolated from the user's desktop browser.
User cannot see/use the agent's browser windows.
Therefore automated publishing to habr.ru / vc.ru MUST use exported cookies.

## Supports
Session: 2026-07-27 — user reported "I don't see your browser."

## Exact workflow
1. User opens habr.com/ru and vc.ru in desktop Chrome/Edge and logs in.
2. User installs `Cookie-Editor` or `EditThisCookie`.
3. User opens extension → Export → copies JSON.
4. User saves JSON files into project trust store, e.g.:
   - `trust/cookies-habr.json`
   - `trust/cookies-vcru.json`
5. Subsequent requests use:
   - Cookie header from stored JSON
   - Any CSRF/auth tokens extracted from cookies or response headers

## Pitfalls
- `/login` paths on habr.ru/ru can redirect to 404 shells; rely on header links, not hard-coded URLs.
- vc.ru outer shells may include unrelated button refs; browser automation is fragile there.
- Browser automation is unsuitable when the user cannot view the agent session. Do not retry browser-only paths for publishable actions.

## Implementation
Use a small Python helper that loads these cookie JSONs into `requests.Session` and targets the article create/update endpoints directly instead of manual form automation.
