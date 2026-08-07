# Publishing a skill/QA artifacts to HuggingFace Spaces + dev.to (Windows, token-from-.env)

Use when syncing a skill's public pages (HF Space README/card + index.html, dev.to article)
to match the GitHub source of truth. Works from the Hermes Windows/MSYS shell.

## Token source
Tokens live in `~/.config/hermes` → actually `%LOCALAPPDATA%/hermes/.env` (path:
`/c/Users/<user>/AppData/Local/hermes/.env`). Read with:
```bash
TOK=$(grep '^API_HUGGINGFACE_KEY=' "/c/Users/Unicorn/AppData/Local/hermes/.env" | head -1 | cut -d'=' -f2-)
```
- `API_HUGGINGFACE_KEY` — fine-grained HF token with `repo.write` on the Space.
- `API_DEV_TO_KEY` — dev.to API key.

Never paste the token value into chat or commits. Extract it into a shell var per command.

## HuggingFace Space (static SDK)
A static Space shows **index.html** full-screen in an iframe — the README card is NOT visible
on the page itself (it only shows under "Files" / "About", and in a Discussion post). So:
- To change what visitors SEE, edit `index.html` (add sections there), not just README.md.
- README.md (the card) still matters for the Spaces listing/SEO — update both.

Push via git with token in the URL (avoids git-credential prompts):
```bash
git clone "https://ratingtesting:${TOK}@huggingface.co/spaces/ratingtesting/keelwright" hf-space
# edit index.html / README.md
cd hf-space && git add -A && git commit -m "..." && \
git push "https://ratingtesting:${TOK}@huggingface.co/spaces/ratingtesting/keelwright" main
```
NOTE: HF Space default branch is `main`, NOT `master` — a `git push ... master` fails with
"src refspec master does not match any". Push to `main`.

### Browser is blocked for editing
The Space **Settings** page and discussion-edit XHR are behind CloudFront 403 in this
environment (Google SSO / WebAuthn unavailable). Do NOT rely on the browser to edit HF —
use git (Space files) or the REST API (discussions, see below). `whoami` works fine via
`huggingface_hub.HfApi().whoami()` once the token is in `~/.cache/huggingface/token`.

## dev.to article
Update (not create) an existing article with `PUT /api/articles/{id}`:
```bash
# Find the article id + confirm slug
curl -s -H "api-key: $DEVTO_KEY" "https://dev.to/api/articles/me"
# Returns [{id, slug, published}], e.g. id 4217414
curl -s -X PUT "https://dev.to/api/articles/4217414" \
  -H "api-key: $DEVTO_KEY" -H "Content-Type: application/json" \
  -d @payload.json   # {"article":{"title":..,"body_markdown":..,"published":true,"tags":[..]}}
```
Build `payload.json` in Python (json.dump) so markdown escaping is correct — don't hand-write JSON.

## HF Discussions — edit via Python SDK (huggingface_hub)
The discussion edit path that worked in this environment is the Python SDK, not REST/GraphQL.
Confirmed working commands:
```python
from huggingface_hub import HfApi
with open(r"C:\Users\Unicorn\AppData\Local\hermes\.env") as f:
    token = next(line.strip().split("=", 1)[1] for line in f if line.startswith("API_HUGGINGFACE_KEY="))
api = HfApi(token=token)
details = api.get_discussion_details(repo_id="ratingtesting/keelwright", discussion_num=1, repo_type="space")
first_comment = next(e for e in details.events if e.type == "comment")
api.edit_discussion_comment(repo_id="ratingtesting/keelwright", discussion_num=1, comment_id=first_comment.id, new_content="new markdown...", repo_type="space")
```
Gotchas:
- Browser edit is usually blocked by CloudFront 403; do not rely on UI here.
- REST PUT/PATCH returned 404; GraphQL updateDiscussionComment returned 404. Treat those as dead ends.
- If the Python SDK edit fails next session, fall back to: user edits manually in their browser, or leave Discussion as historical snapshot and update index.html + README card instead.

## Verification
After pushing, confirm with `curl` against the raw URL (not the rendered page, which caches):
- HF README: `curl -s https://huggingface.co/spaces/ratingtesting/keelwright/raw/main/README.md`
- dev.to: re-GET `https://dev.to/api/articles/{id}` and check `body_markdown` contains the new row.
