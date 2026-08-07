---
name: agent-skill-catalog-publishing
description: Publishing AI agent skills to external catalogs.
---

# Agent Skill Catalog Publishing

Publishing a skill for discoverability is a distinct task from writing or versioning it. Each catalog has its own submission path and hard limits discovered the hard way. Read this before attempting any publish.

## Catalog matrix (status 2026-07)

| Catalog | Submission | Notes |
|---|---|---|
| **clawhub.ai** | CLI `clawhub skill publish` OR web "import from GitHub" | WORKS. Enforces MIT-0. NVIDIA SkillSpector moderation (pending state is normal). |
| **askill.sh** | Web form at /submit (paste GitHub URL) OR index triggered by `askill add gh:<owner>/<repo>` / `npx skills add <owner>/<repo>`. Indexes SKILL.md; 229k+ skills in catalog. | WORKS. Re-index by re-running the install/add command after a push. |
| **skills.sh** | NO public submit form. Auto-indexes when someone runs `npx skills add <owner>/<repo>` — the install CLI triggers a catalog index of the repo's SKILL.md. To force-index/re-index, run `npx skills add ratingtesting/keelwright` (add `--yes --global` to skip the interactive agent prompt). Confirmed working 2026-07-30: keelwright appeared as "Safe, Low Risk, 1 alert" immediately after the command. Passive GitHub auto-index is unreliable; the **npx command is the reliable path**. | Reliable for drive-stars IF you run the npx command. |
| **GitHub CLI** | `gh skill publish` (preview since 2026-04) | Publishes to skills.github.com ecosystem from the repo. |
| **AgentSkills.io** | **CLOSED** — CONTRIBUTING.md: "We don't maintain a directory of community skills. This may change in the future." | Do NOT attempt submission. Wastes cycles. |

## Verify in browser — CLI output is never proof of publication

Every catalog CLI prints a success line (`OK. Published`, `Installed 1 skill`,
`Found and indexed 1 skill`) that only means the *request* was accepted. The public
page renders from a cached/async index and lags — sometimes showing the old version for
minutes, or until a re-index event fires. Claiming "published" from CLI output alone is a
**false report**: it is exactly the self-report-without-verification failure mode the
keelwright skill exists to prevent in code, and the publisher must not commit it against
the catalog.

After EVERY catalog action, open the actual catalog page in a browser and confirm the
version number, description, and license match the push:

| Catalog | Page to open | What to check |
|---|---|---|
| clawhub.ai | `https://clawhub.ai/skills/<slug>` | `latestVersion`, `tags.latest`, changelog |
| askill.sh | `https://askill.sh/skills/gh/<owner>/<repo>` (or search) | version in SKILL.md excerpt, description, MIT-0 |
| skills.sh | `https://www.skills.sh/<owner>/<repo>` | version, "Safe/Low Risk" badge, description |
| GitHub | repo Releases tab | new Release carries `Latest` marker |

If the page is stale, do NOT conclude the publish failed and burn another version. The
index is async: re-run the install/add command (skills.sh, askill.sh) or trigger a scan
(clawhub), wait, then re-check in browser.

**Memory hazard:** never write a catalog-behavior claim to MEMORY.md from CLI output or
assumption. This session recorded "askill.sh auto-indexes" without browser verification;
that false entry then caused repeated wrong advice in a later session. Verify in browser,
then — and only then — record the fact.

## clawhub.ai workflow (proven)

```bash
npm i -g clawhub

# Token lives in Hermes .env as API_CLAWHUB_AI_KEY (value starts clh_)
# Write config directly — terminal tool can write it; do NOT pass token in argv
# (command parser blocks tokens in command line).
mkdir -p "$APPDATA/clawhub"
cat > "$APPDATA/clawhub/config.json" <<'EOF'
{"token":"clh_XXX","registry":"https://clawhub.ai"}
EOF
clawhub whoami   # prints your handle, e.g. ratingtesting

# CLI v0.23.1 surface: `publish <path>` (single skill, explicit) and `sync` (scans a tree).
# Always publish from a CLEAN STAGING COPY — see "Never publish the working directory" below.
STAGE="$TEMP/clawhub-publish-<slug>"
rm -rf "$STAGE" && mkdir -p "$STAGE"
git -C /path/to/skill-repo archive --format=tar <tag> | tar -x -C "$STAGE"

cd "$STAGE"
clawhub publish . --no-input --version <semver> --slug <slug> --name "<slug>" \
  --categories "automation,development,security" \
  --topics "<kw1>,<kw2>,<kw3>,<kw4>,<kw5>" \
  --source-repo <owner>/<repo> --source-commit "$(git -C /path/to/skill-repo rev-parse <tag>)" \
  --source-ref <tag> --changelog "<text>"
```

### `--name` is NOT optional — without it displayName comes from the FOLDER
This drew a direct user complaint ("зачем-то сменил название"). `--slug` sets the URL, but
`displayName` falls back to a title-cased version of the **staging directory name**:

| staging dir | resulting displayName |
|---|---|
| `clawhub-publish-keelwright` | `Clawhub Publish Keelwright` |
| `clawhub-publish-148` | `Clawhub Publish 148` |

Two wrong names shipped before anyone noticed, because the CLI prints `OK. Published` either
way and the catalog page is the only place the bad name shows. Always pass `--name` explicitly
**and** name the staging dir after the slug so both paths agree:

```bash
STAGE="$TEMP/<slug>"          # not "publish-<slug>", not "<slug>-<version>"
clawhub publish . --name "<slug>" ...
```

Metadata is **replace-only, never merged**: omitting `--categories` / `--topics` on a later
publish does not preserve the previous values, the fields come back `None`. Re-send the full
set on every publish. Confirm afterwards via `/api/v1/skills/<slug>` — check `displayName`,
`categories`, `topics` — because the catalog card renders from the newest **visible** version,
so a freshly-published-but-unscanned version leaves the old metadata on display and makes a
correct publish look like it failed.

`--no-input` is mandatory in an agent context: without it the CLI waits on a prompt after
printing its result and the tool call dies at timeout, leaving you unsure whether it published.
Note `-V, --cli-version` shows the version — plain `--version` is an unknown option at top level.

### Never publish the working directory
`clawhub` packages **every file in the folder** and does **not** read `.gitignore`. In this
session the live skill dir held 104 files while git tracked 74 — publishing it would have
shipped `internal/` (12 QA/session notes), article drafts, scraped account HTML, cover images
and `__pycache__` to a public registry. There is no `.clawhubignore`, and unlike GitHub there
is no `git revert` for a registry release.

Always stage via `git archive <tag>`, then assert the count matches `git ls-files | wc -l` and
grep the staging tree for private patterns before the publish call:

```bash
find "$STAGE" -type f | wc -l    # must equal: git ls-files | wc -l
find "$STAGE" -type f \( -path "*internal*" -o -name "*.pyc" -o -name "*-draft.md" \) | head
```

### Pitfalls (each cost a round-trip this session)
- **NEVER `clawhub delete <skill>` to "republish" — it destroys everything.** A whole-skill
  delete wipes download counts, star history, version timeline, and moderation state.
  `undelete` partially restores but the damage is real. This session: deleted keelwright
  (138 downloads, 9 versions), had to undelete, lost the v1.5.3 publish. To update a skill:
  just `clawhub publish` with a bumped version number — the old version stays, the new one
  overlays. To delete a SINGLE version: `clawhub delete <skill> --version <ver>` (requires
  publishing a replacement first if it is the current latest). When a user says "couldn't
  delete" in a version-update context, they mean the version was already consumed ("Version X
  already exists"), NOT that the whole skill needs deleting. Clarify before acting.
  **Hard rule: `clawhub delete` (whole skill) is a globally-destructive, irreversible action.
  Before running it, STOP and ask the user to confirm explicitly — never infer it from a
  failed-publish or "couldn't delete" remark. A vibe-coder owner will not expect a delete to
  nuke their download history.** Bumping the version is always the safe alternative.
- **Version must increment** on every re-publish. Same version → "Version X already exists. Increment." Bump patch even for metadata-only changes.
- **Max 3 categories.** Valid slugs observed working: `security`, `development`, `automation`, `utility`, `productivity`. `ai-ml` was REJECTED as unknown — verify a slug before using it.
- **License is enforced MIT-0** by ClawHub regardless of your SKILL.md `license:` field. To avoid conflict, set `license: MIT-0` in SKILL.md frontmatter AND use an MIT-0 LICENSE file. A CC-BY-4.0 skill shows as MIT-0 on the platform.
- **SkillSpector (by NVIDIA) moderation** runs on publish. A *pending* state ("findings are pending" / "pending.publication" / "Moderate CLEAN") is NORMAL — wait, don't click "Re-run preview" repeatedly, it resets the scan timer. A `suspicious` verdict is NOT the same thing and will never clear on its own — see "Cause of the invisible version" below.
- **"Import is out of date. Re-run preview"** appears when the GitHub repo changed after import. On web import from GitHub, just click Re-run preview. Via CLI, re-publish with bumped version.
- **Device login** (`clawhub login --device`) prints a code but needs browser GitHub OAuth the agent cannot complete. Prefer the token-in-config.json path.
- **Web import pulls from GitHub** — after you `git push` license/version changes, the site shows "out of date" until you re-run preview. The CLI publish and web import are two separate paths; if the user deleted the CLI-published skill and re-imports from GitHub, CLI publishes are moot.

### `OK. Published` is NOT proof of publication — verify against the registry
The CLI printed `OK. Published keelwright@1.4.7 (<id>)` and exited 0, yet the version never
became visible. Do not report success on the CLI's word; confirm with the read API:

```bash
curl -s "https://clawhub.ai/api/v1/skills/<slug>/versions"      # list — 200 JSON {"items":[...]}
curl -s -o /dev/null -w "%{http_code}\n" \
     "https://clawhub.ai/api/v1/skills/<slug>/versions/<semver>"  # 200 = live, 404 = not published
```

Working endpoints (probed): `/api/v1/skills/<slug>` and `/api/v1/skills/<slug>/versions`.
Wrong shapes that 404: `/api/skills/<owner>/<slug>`, `/api/v1/skills/<owner>/<slug>`,
`/api/registry/skills/...`. **Read endpoints need no auth** — plain `curl` works. Sending
`Authorization: Bearer <clh_ token>` returned `200` with a **zero-byte body**, which reads like
an outage but is just the wrong auth mode for these routes; drop the header.

The contradictory state to recognise: `/versions/<v>` returns **404 Version not found** while a
re-publish of the same version is refused with **"Version X already exists"**. The upload landed
and the version slot is consumed, but it is not listed. It cannot be overwritten — the only way
forward is a new version number, so diagnose before burning another one.

### Cause of the invisible version: it is waiting on a scan
A freshly published version is **not listed until a moderation scan completes**. Until then
you get the contradictory pair described above: `/versions/<v>` → 404, re-publish → "already
exists". This is the normal steady state right after `clawhub publish`, not an error.

```bash
clawhub scan --slug <slug> --version <semver> --json          # read the verdict
clawhub scan --slug <slug> --version <semver> --update --json # re-scan, write results back
```

`--update` re-runs the scan and stores the result. **This does make a stuck version appear** —
observed directly: `1.4.7` sat at 404 through several checks, the user triggered a re-scan, and
it became visible and took over `latest`. So when a version is invisible, run the scan (or ask
the user to) **before** concluding anything is wrong and before burning another version number.

Read `report.clawscan.status` for the verdict. A `suspicious` status is a real finding list
worth fixing on the merits, but note it did **not** prevent listing here — do not treat it as a
hard publication block, and do not assume a re-scan is futile.

Findings that trip `suspicious` on a legitimate guardrail skill — worth pre-empting anyway,
since each fix costs a version number:
- `subprocess.run(..., shell=True)` anywhere in shipped scripts (`[AST4] [OH1] [TM1]`). Putting it
  behind an opt-in flag is **not** enough; use an argument vector instead.
- Any wording that tells an agent to phrase requests so a model won't refuse (`[SSD-2]` — read as
  safety evasion, the most reputationally damaging finding).
- Creating/maintaining files outside the skill dir without consent (`[SDI-1] [SQP-2]`), and
  extracting archive content into a home-dir path like `~/kw-qa` (`[E4]`).

### `--changelog` / `--source-*` affect metadata, NOT the `latest` marker
Including `--changelog` and `--source-repo/--source-commit/--source-ref` is correct hygiene
(it populates the version's changelog text and provenance), but on an **existing** skill these
flags do NOT move the `latest` marker. `latest` follows **publish order** (see below): the most
recently *published* version is shown as latest, regardless of `--tags latest` or `--changelog`.
If you publish a higher semver after a lower one, the lower one — published last — wrongly
becomes latest. The only fix is a manual edit on clawhub.ai (Edit → Latest version → pick the
new version) or publishing another bumped version on top. Always pass `--changelog` anyway;
just don't expect it to set `latest`.

### Latest tag follows publish ORDER, not semver
Versions listed for one skill: `1.0.0` (15:03) → `1.3.0` (15:08) → `1.4.1` (15:09) → `0.1.0`
(15:26). Because `0.1.0` was pushed last it became latest, so `clawhub install <owner>/<slug>`
served `0.1.0`. Never publish a lower version after a higher one; if it happened, `clawhub hide`
the stray version. Install syntax is `--version <semver>` — the `<slug>@<version>` form errors
with "Skill not found or unavailable to this account".

### Rate limiting looks like a missing skill
Errors arrive as `Skill not found or unavailable to this account. (reset in 8s)` and
`Version not found (reset in 56s)`. The `(reset in Ns)` suffix marks it as throttling, not
absence — honour the stated delay and retry instead of concluding the skill or version is gone.

### `sync` will publish other people's skills
Run from a skills root, `clawhub sync` listed 20+ unrelated skills as `NEW (publish 1.0.0)`
alongside the intended one. It also proposes `--bump patch` off the registry's latest, which
would have published `1.4.2` over a local `1.4.7` and wrecked the numbering. Use
`publish <path>` with an explicit `--version` for a single skill; reserve `sync` for a tree you
own entirely, and always `--dry-run` first.

### The web publish form needs the user
`https://clawhub.ai/skills/publish?updateSlug=<slug>&ownerHandle=<handle>` returns 200 but the
form is client-rendered behind login. Exported browser cookies were auth-less (only
`clawhub-theme-mode` and `__vdpl`), so the fetched HTML showed no owner handle and no
category/tag/upload controls. Cookie export does not carry a ClawHub session — hand the form to
the user rather than trying to drive it.

### SkillSpector findings: separate real bugs from framing complaints
A 25–30 finding report on a coding-agent skill is mostly the scanner objecting that an
orchestrator orchestrates (writes files, spawns subagents, runs shell) — those are not bugs.
Verify each finding on disk and fix only what is genuinely wrong; roughly 1 in 10 qualifies.

The discriminating question is **not** "is this dangerous in the abstract" but "does the code
honour its stated contract". Every real defect across three audit rounds was a contract
violation: docs advising a rename to dodge a Semgrep credential rule while still logging
`secret[:8]`; a function taking an `impl_file` argument and ignoring it, with the verdict
scanned from output text instead of the exit code; an importer executing post-install shell
commands from a just-unpacked archive; `restore` silently keeping files added since the
snapshot; SKILL.md advertising a gate as "machine-checked" that its own reference file says
cannot be enforced.

To prove such a fix, build a genuinely hostile artifact with a working payload (a marker-file
write) and confirm the marker does **not** appear. Asserting on log text would have passed both
before and after. Note that SHA256 manifest checks do not help when the manifest ships inside
the same zip — recompute the hashes and the gate passes. Integrity proves self-consistency,
never provenance.

### Static-analysis false positives worth knowing
- **`importlib.util.spec.loader.exec_module(mod)` is NOT `exec()`.** SonarQube/Socket-style
  detectors flag it as "dynamic code execution" because the name contains `exec`, but it is the
  canonical stdlib way to load a `.py` module by path. A verification script that imports the
  module-under-test via `spec_from_file_location` + `exec_module` is safe — it only runs code
  already on disk in the repo. Do NOT "fix" this by switching to `importlib.import_module()`;
  that changes nothing and the detector may still fire. Leave the pattern; note it as a known
  false positive in the audit response.
- **`subprocess.run(argv, shell=False)` is the SAFE form**, not a finding. A detector that
  flags "subprocess" without checking `shell=False` is wrong — the dangerous pattern is
  `shell=True` or string-concatenated commands. Keep argument vectors; never downgrade to
  `shell=True` to satisfy a scanner.

Full triage method — the three buckets, the eight real defects with reasons, what to
deliberately leave alone and how to say so in release notes, and how to read the delta between
rounds — in `references/triaging-audit-findings.md`.

## License decision
If targeting clawhub: use MIT-0 in BOTH SKILL.md frontmatter (`license: MIT-0`) and the LICENSE file. Push the commit BEFORE importing so the platform picks up the right license.

## Every version needs a git tag AND a GitHub Release

A tag alone is invisible on the repo's front page. The user was confused when `v1.4.0` existed
as a tag with no Release entry and assumed the push had failed. The convention is therefore:
bump `version:` in SKILL.md → commit → push → `git tag` → push tag → `gh release create`.

`gh release create` has two traps worth pre-empting:

- **It rejects `-q`.** There is no quiet flag; passing one prints the whole help text and
  creates nothing, while the surrounding `&&` chain still looks like it succeeded.
- **Notes with apostrophes break single-quoted bash.** `--notes '...the skill's purpose...'`
  terminates the quote early and dies with `syntax error near unexpected token`. Write the
  notes to a temp file and pass `--notes-file` — reliable regardless of content.

Confirm with `gh release list | head -1` and check the new version carries the `Latest` marker.

### Write release notes that survive the next round
For a skill under repeated audit, the notes are the institutional memory. Include:
1. What was fixed and **why it was genuinely wrong** — the contract it violated, not the
   scanner's severity label.
2. A **"Not changed"** section naming the findings deliberately left alone and the reasoning.
   Without it the same findings get re-fought every round and a future maintainer may "fix"
   them out of the product.
3. The verification actually run, including the honest label (`ad-hoc, N/N PASS`, never
   "suite green" when no suite exists).
4. Any test that failed for the *wrong* reason and was corrected — record that the test was
   fixed rather than the claim weakened.

## Verify file state before agreeing it's broken
When the user says a file is "wrong"/"truncated", actually read it fully before confirming. This session the LICENSE file was complete (full CC BY 4.0 text) but was wrongly claimed truncated — caused a confusing round-trip. Read the whole file, don't infer from a grep snippet.

## References
See `references/catalog-commands.md` for the exact clawhub command set, the AgentSkills.io CONTRIBUTING excerpt, and the skills.sh issue #880 context.

## HF Space publishing (static apps)

Hugging Face Spaces with `sdk: static` serve files from a git repo. To update a file without cloning:

```python
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj="local/index.html",
    path_in_repo="index.html",
    repo_id="owner/space-name",
    repo_type="space",
    token=hf_token
)
```

**HF token quirk**: tokens in `.env` may contain a single ellipsis character `…` (U+2026)
that looks like three dots in terminal output. Python's `repr()` or `len()` disambiguates:
a 37-char token with `…` in the middle is valid; copying it as three literal periods `...`
gives a 39-char string that 401s. Always `repr()` the token before debugging auth failures.

After upload, verify via `curl https://huggingface.co/spaces/owner/space-name/raw/main/index.html | grep "license"`.

## askill.sh: re-index after changes

askill.sh indexes SKILL.md into its catalog (229k+ skills) from a GitHub repo. It refreshes
when someone runs `askill add gh:<owner>/<repo>` or installs via the npx/CLI path that resolves
to the same repo — i.e. the same mechanism as skills.sh. The web form at https://askill.sh/submit
(paste GitHub URL) also works but is not required for routine updates. Because the index is
driven by *install/resolve* events, a fresh `npx skills add <owner>/<repo>` (or `askill add`)
after a push is enough to surface new content — no separate "re-submit" step needed beyond
that. Check the **Raw tab** on the skill page to confirm the update landed (Preview may cache).

Run `scripts/stage_clean_publish_tree.py <repo_dir> <git_ref> <stage_dir>` before any publish:
it stages from `git archive`, asserts the file count matches `git ls-files`, greps for private
patterns, and exits non-zero so it can gate the publish command.

## The universal "did it actually publish" check (applies to ALL four catalogs)

The publisher's own worst failure mode this session: ran `npx skills add` / askill submit,
saw the CLI's "Installed 1 skill" / "Found and indexed 1 skill", and told the user the
catalog was updated — without opening the page. The pages were stale (showing the old
version) and the user caught it. This is the same self-report-without-verification flaw the
keelwright skill forbids in code; the publisher must not do it against the catalog.

RULE: after any publish/install/add/submit, open the catalog page in a browser and confirm
the version/description match the push. If stale, re-run the install/add command and wait —
do not burn another version number assuming failure. And never record a catalog-behavior
claim in MEMORY.md from CLI output alone; verify in browser first or it will poison later
sessions (this session wrote "askill.sh auto-indexes" unverified, then repeated the error).
