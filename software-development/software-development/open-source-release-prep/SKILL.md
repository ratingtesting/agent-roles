---
name: open-source-release-prep
description: >
  Use when preparing a skill, repo, prompt pack, or any agent-built artifact for PUBLIC or
  community release — vetting licenses of referenced/bundled tools, deciding a license for your
  own work, scrubbing private data, and decoupling from a private stack. Triggers: "I want to
  publish this", "put this in the community", "will I have legal problems", "check the licenses",
  "make it universal / not tied to <stack>", "can I sell this later". Prevents shipping private
  data or tripping a copyleft/source-available license mine.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [licensing, open-source, publishing, privacy-scrub, decoupling, community, skills]
---

# Open-source release prep

Turning a private, agent-built artifact into something safe to publish. Independent checks —
run all of them; skipping one is where the problems come from.

## The gates (run all before publishing)

0. **Name-collision check** — before you commit to a public name, prove it's free (§Gate 0)
1. **License-vet everything you depend on or reference** → see `references/license-vetting.md`
2. **Decide YOUR license** (default MIT for permissive; CC BY when the goal is credit/fame)
3. **Scrub private data** (grep, don't eyeball) — private/env-specific content goes to `internal/` + `.gitignore`
4. **Decouple from the private stack** (generic core + per-stack bindings)
5. **Reference-integrity sweep** after any rename/merge (fix every pointer, incl. the swarm dispatch table)
6. **Publish the release, not just the tag** — a git tag alone is invisible to users. After
   `git tag vX.Y.Z && git push --tags`, ALWAYS run `gh release create vX.Y.Z --repo <owner>/<repo>
   --title "vX.Y.Z — <summary>" --notes "..."` and confirm it shows as **Latest**. A tag with no
   Release leaves the repo's Releases page empty and the user confused ("I pushed v1.4.0 but don't
   see it updated"). The Release is the human-visible publish event; the tag is only the anchor.
   Do both in the SAME push turn — never bump a version without creating the Release.

---

## Gate 0 — Name-collision check (do this BEFORE renaming, not after)

Renaming is cheap while the artifact is markdown and catastrophic once you've built reputation on
the name. So pick the public name FIRST, and prove it's unowned before committing:

1. **Search the exact name across the niche**, not just one registry. Hit GitHub, PyPI, npm, and a
   plain web search. A name is "taken" if any project in *your same space* already uses it — even a
   near-synonym positioning (e.g. `vibe-loop` vs `vibe-loop-engineering` both being "AI loop-coding
   harness"). Same-niche collision = you look like a clone and are invisible in search.
2. **Generic `X-loop` / `X-guard` / `slop-X` / `vibe-X` names are saturated** in the agent/AI-coding
   space (2026). Avoid them — they collide and don't rank.
3. **Winning move: coin a unique word that returns ZERO software results.** Then you own the entire
   search page from day one (this is why names like `desloppify` work). Verify the candidate returns
   only unrelated hits (surnames, fiction, people) — no GitHub/PyPI/npm/domain project.
4. **Only after the name is verified free** do the rename mechanics in Gate 5.

The name is a branding decision with irreversible downstream cost — surface the collision facts and
let the user choose; don't pick for them.

---

## Gate 1 — License vetting

**The key legal distinction (verify it applies to your case):** a Markdown skill / doc that only
*names a tool and gives its command line* is **NOT redistributing** that tool's code. Referencing
≠ bundling/linking/copying. So the tool's license (even LGPL, even GPL) imposes **no obligation**
on your publication. The user installs the tool themselves under that tool's license.

This flips only if you **bundle, embed, link, or copy source** — then the tool's license binds you.

**Always read the actual LICENSE file** (raw GitHub), never assume from a badge or memory.
Permissive & safe to depend on and redistribute: **MIT, MIT-0, Apache-2.0, BSD, ISC**.
Watch out for: **LGPL/GPL** (fine to *reference*, binds if *bundled/linked*), and
**source-available licenses with paid tiers** (OSNL, BSL, SSPL, Elastic, "free for internal use
only") — these look open but gate commercial redistribution. See `references/license-vetting.md`
for the concrete license bank and the tool-swap decision recorded from a real session.

**When a dependency has a problematic license:** prefer swapping it for a permissive-licensed
equivalent over adding legal caveats users must honor. A community-respected MIT/Apache tool that
covers the same job is worth more than a slightly-better-fit tool under a paywalled license —
consistency (one license story) beats a marginal capability gain, especially if you may sell later.

**"Absorb the source that inspired the candidate" pattern (used repeatedly, high value):** when a
candidate dependency/skill is either (a) under a bad license, (b) copyleft/NC you can't copy, or
(c) *immature* (0★, single-author, no track record) — don't take on the dependency. Instead:
1. Find the AUTHORITATIVE source it draws from (a book, a spec, a standard, an industry vocabulary,
   a published research finding). Candidates usually cite it themselves.
2. Terminology, facts, and ideas are **not copyrightable** — the *names* (e.g. Fowler's code-smell
   / refactoring-technique names, GoF pattern names, OWASP categories) are free to use.
3. Re-render the knowledge in **your own words** (never copy the source text) and inline it as a
   `references/<topic>.md`. Credit the source in provenance as a fact/inspiration, not a copy.
Result: zero dependency, clean license, and your artifact becomes *self-contained* — which also
fixes the "consumer may not have the bundled skill installed" problem. Prefer a mature respected
tool when one exists (GuardDog/OSV/SkillSpector); fall back to this pattern when it doesn't.

## Gate 2 — Your own license

Set `license:` in frontmatter AND ship a `LICENSE` file. **MIT** is the default for maximum reuse.
If your content was *adapted from* sources, confirm their license permits it: **MIT-0** permits
use/modify/redistribute/relicense with no attribution required (credit anyway, out of courtesy).

**Pick the license by the author's actual GOAL, and name the trade-off out loud:**
- **Want maximum adoption, don't care about visible credit → MIT.** Attribution is just the
  copyright line; your name travels quietly.
- **Want fame / "credit-or-pay" → CC BY 4.0.** Attribution is a *mandatory, visible* condition:
  no credit = license breach = they have no rights = must comply or negotiate (this IS the
  "credit or pay" lever, no special contract needed). Still permissive, so adoption stays high.
  CC BY suits docs/prompt/markdown artifacts (a SKILL.md is documentation, not compiled code).
- **Want to block others earning off it → CC BY-NC.** But NC *kills adoption and therefore fame*,
  and usually protects the wrong thing: the artifact is the marketing, the sellable product is a
  separate thing under its own license. Steer the user away from NC when their real goal is fame
  or when the money comes from a downstream product, not the artifact itself.

Honest ceiling to state to the user: a license only protects YOUR expression, structure, and
wording — **not the underlying ideas/patterns**. Adapted-from-MIT-0 concepts stay free at their
source; you get no monopoly on the concept, only on your rendering of it.

Enforcement realism: "no attribution = infringement" is legally solid but chasing every omission
in a markdown file rarely pays. CC BY's real value is the *norm* (people credit) + the lever, not
lawsuits — set expectations accordingly.

## Gate 3 — Private-data scrub (grep, never eyeball)

Before publishing, grep the whole artifact for personal/project data. Any hit that isn't a
deliberate public example → remove or move to your private project-instructions file.
```bash
# tune the alternation to your identifiers
grep -rEi "yourname|C:\\\\Users|/home/you|projectcodename|cron.?id|localhost:[0-9]|internal-host|strategy" .
```
Scrub targets: real names, absolute paths, hostnames/ports, cron/job IDs, product strategy,
internal URLs, secrets, org-specific jargon. Re-run the grep after edits (edits reintroduce data).
**A clean grep is the release gate — 0 hits, verified, not assumed.**

**Don't delete private/env-specific content — quarantine it in `internal/` + `.gitignore`.** Much
of what's "not publishable" is still valuable to the author: QA-run logs, session transcripts,
OS-specific workarounds (e.g. Windows/MSYS path quirks), the author's own test prompts. Rather than
lose it, move it to an `internal/` directory and add a repo-root `.gitignore` that excludes
`internal/`. Add an `internal/README.md` stating it is NOT part of the published artifact. This
keeps the author's kitchen intact while the public surface stays clean.

**Hard rule after quarantining: NO public file may point into `internal/`.** Moving a file breaks
every inbound link. For each link from a still-public file into a moved file, *genericize it* —
keep the universal lesson inline, drop the dead pointer (e.g. replace "full recipe →
`internal/windows-notes.md`" with a one-line generic version of the tip). Then grep to prove zero
`public → internal` links remain. A public file linking a gitignored file is a broken link the
moment someone clones the repo.

**Distinguish universal knowledge from author-specific detail when deciding what's public.** The
class-level technique stays public; the author's environment, private runs, and stack quirks go to
`internal/`. Test: "would a stranger on a different OS/stack need this?" No → `internal/`.

## Gate 4 — Decouple from the private stack

Make the core stack-agnostic; isolate stack-specifics so others can adapt without touching the
core. Pattern that works well for skills:
```
SKILL.md + references/*.md      = the engine (generic, portable)
references/bindings/<stack>.md  = per-stack commands (test/lint/build/tool invocations)
```
Ship ONE binding as a worked example (e.g. `flutter-example.md`) and tell users to copy it for
their stack. Keep only ONE artifact (a generic one), not two parallel copies — two copies = double
maintenance and they drift. The private consumer just uses the generic artifact + its own binding
+ its own private instructions file for the private data pulled out in Gate 3.

## Gate 5 — Reference-integrity sweep after any rename or merge

**New (2026-07):** `references/license-sweep-checklist.md` — file-by-file checklist for propagating a license change across the repo AND external publications. Load it whenever Gate 5 involves a license switch.

Publishing usually means renaming/merging the private skill into a new public name (e.g.
`lazy-unicorn-loop` → `vibe-loop`). When you do, the old name is referenced in more places than
the skill folder. Grep the WHOLE environment for the old name and fix every live pointer, or
consumers silently break:
- **Other skills' cross-reference tables** (`related_skills`, "how this connects" sections).
- **Project instruction files** (AGENTS.md / CLAUDE.md / .cursorrules) — dispatch tables, `/do`
  triggers, gate references, practice tables, setup guides.
- **Cron jobs** that load the skill by name.
- **The skill's own frontmatter/body/LICENSE** — after switching license (MIT→CC BY), sweep for
  the stale license word in SKILL.md body, provenance, and the setup guide, not just the LICENSE
  file. Internal contradiction (LICENSE says CC BY, body says MIT) defaults to whatever the file
  says and silently defeats the intended license.
- When deleting/merging a skill, use `absorbed_into=<new-name>` so downstream references get
  rewritten and forwarding is clean.

**Swarm gap (the one that bites and is easy to miss):** subagents do NOT inherit skills. If an
agent swarm consumes the skill via `delegate_task`, updating the main agent's instructions is not
enough — you must also update (a) the subagent **task→skill dispatch table** and (b) the
`delegate_task` **context template** so delegated workers are told to `skill_view(name='<new>')`
themselves. Otherwise the orchestrator uses the engine but every delegated worker runs without it.
Verify with a final grep: zero hits on the old skill name across the project.

## Bonus — coverage/risk research before claiming "safe" or "complete"

If publishing a security/quality artifact, do a fresh web pass on the current risk landscape and
build a **risk → mechanism → coverage** table (✅ full / ⚠️ partial / ❌ blind spot). Name the
blind spots honestly rather than implying total coverage; for each gap prefer an existing
respected tool with a clean license over a hand-rolled rule. This both improves the artifact and
becomes the "why use this" section of its README.

## Gate 7 — Serve the END USER first; benchmark scores are secondary

Stated explicitly by the author of a published skill: *"Мой скилл для упрощения жизни
вайбкодерам, луупкодерам — это самое главное, а тесты моделей — это вторичное."* When a change
would improve a benchmark/QA number but make the artifact more confusing or intrusive for a
non-programmer, the end user wins. When ranking work, fix what a real user hits on first contact
before polishing evaluation harnesses.

**Corollary — silent side effects are a bug, even when correct.** An artifact that writes files
into the user's project on load must SAY SO, once, in plain language, and state that removal is
allowed. Silence reads as intrusive and it also wastes the artifact's best moment to demonstrate
value. Shape that matters:

- One short line naming what was created, plus the benefit in the user's vocabulary
  ("memory across chats: what we already tried, which fixes stuck") — never internals
  ("L4 cross-session counters"), which mean nothing to the audience.
- State that deletion is permitted and what it costs. An effect the user cannot opt out of is not
  trusted.
- A notification, not a confirmation prompt — do not add a turn of friction.
- Fire only when something actually happened. Repeating it every session is noise.
- Explain-yourself headers in generated files too: replace `Do NOT delete — <internal system>
  reads this` with what the file does for the reader.

Removing a genuinely useful automatic behaviour is usually the wrong fix — the target audience
will never perform the setup by hand. Announce it instead.

**Grep for self-contradiction after this kind of change.** Docs telling the agent to act
"silently" survived in two files after the announce rule was added; an agent given both
instructions follows whichever it read last. Same class of bug as the stale-license sweep in
Gate 5.

## Gate 8 — Audit findings: separate real defects from framing complaints

Automated skill scanners (SkillSpector/ClawScan and similar) flag an autonomous artifact for
being autonomous. In a 30-finding report on a coding-agent skill, 27 were the scanner objecting
that an orchestrator writes files, spawns subagents, and runs shell commands — its purpose. Three
were real. Verify each finding against the file on disk before acting, and fix only genuine
defects; "fixing" the framing complaints would gut the artifact.

Findings that ARE worth fixing, because they are indefensible in a security-adjacent artifact:
- **Advice that evades a security detector.** Guidance to rename a logging parameter so a
  credential-leak rule stops matching, while still printing `secret[:8]`, is detector evasion plus
  a partial secret leak. Correct fix: don't log the value at all.
- **Code that executes untrusted input on unpack.** An importer running post-install shell
  commands from the archive it just extracted is remote code execution. A SHA256 manifest does not
  save you when the manifest ships inside the same archive — recompute the hashes and the gate
  passes. Integrity proves self-consistency, never provenance. Make execution opt-in behind an
  explicit flag, announce it, and say so in `--help`.
- **A verdict function that cannot fail.** Deriving pass/fail by searching output for `"FAILED"`
  instead of the process exit code reports crashed and no-tests-collected runs as green.

Anything a scanner reads as safety evasion — including wording that tells an agent to phrase a
request so a model won't refuse — is the most reputationally damaging category. Remove it even if
the intent was benign; you cannot argue with the label after publication.

**Prove such a fix with a hostile artifact, not with log assertions.** Build a real malicious
input carrying a working payload (a marker-file write) and confirm the marker does not appear.
Asserting on log text would have passed both before and after the fix.

## Pitfalls
- **Assuming a license from a badge/memory** — read the raw LICENSE file every time.
- **Treating "reference a tool" as redistribution** (over-caution) OR bundling code and ignoring
  its license (under-caution) — know which case you're in.
- **Eyeballing for private data** — always grep, and re-grep after edits.
- **Shipping two parallel copies** (public + private) — publish one generic artifact + bindings.
- **Source-available licenses that read as "open"** — OSNL/BSL/SSPL gate commercial redistribution;
  a paywall tier can ambush a future "sell it" plan even when internal use is free today.
- **Tag without a Release** — `git tag` + `git push --tags` is not a publish; users watch the
  Releases page. Always `gh release create` (mark Latest) in the same turn as the version bump.
