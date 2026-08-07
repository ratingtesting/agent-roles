---
name: skill-publishing
description: >
  Prepare an agent-created skill (or any local prompt/markdown artifact) for public/community
  release. Load when the user says "I want to publish this skill", "share it with the community",
  "is this safe to release", "check the licenses", or asks whether reusing bundled sources causes
  legal problems. Covers three gates: (1) PII/stack-leakage scrub, (2) license audit with the
  mention-vs-redistribution rule, (3) engine/binding decoupling for genericity. Complements
  writing-skills / skill authoring (which cover CREATING skills) — this covers RELEASING them.
version: 1.0.0
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [skill-authoring, publishing, licensing, open-source, pii-scrub, community, compliance]
    related_skills: [writing-skills, hermes-agent-skill-authoring]
---

# Skill Publishing — release readiness for shared skills

Before a locally-built skill goes public, run three gates. Skipping any one is how you leak a
client's project, ship code you had no right to, or publish something too coupled to be reusable.

## Gate 1 — Scrub for PII and stack leakage (grep ALL files, not just the "binding" one)

A skill designed as "generic engine + project binding" still leaks if the split was never
enforced. **Grep every file in the skill dir**, not just the file you *intended* to hold the
specifics. Real finding: a "decoupled" engine still had the stack name, `pubspec.yaml`, framework
idioms, and personal paths scattered across 4 non-binding files.

Grep for (adapt tokens to the project):
- Stack/framework names, language idioms, package-manifest filenames, project codename
- Personal identifiers: the user's name, `C:\Users\<name>\...`, home paths
- Machine/infra: `localhost:<port>`, hardcoded absolute install paths, cron `job_id`s
- Business strategy / roadmap language that shouldn't be public

Fix = move genuinely stack-specific content into ONE clearly-labelled optional binding/example
file; make the engine files stack-neutral (generic "test / typecheck / build" instead of concrete
commands); delete personal/infra strings.

## Gate 2 — License audit, with the rule that saves you

**Mentioning a tool ≠ redistributing it.** A markdown skill that merely *names* a tool and gives
its run commands does NOT bundle that tool's source, so the tool's license does NOT bind the
skill's publication. The user installs the tool themselves, under the tool's own license. This is
the single most important licensing fact for prompt/markdown skills.

Therefore what actually governs your right to publish is the license of the *content you adapted*
(the source skills/text), not the licenses of tools you reference.

| Situation | Governs publication? |
|---|---|
| You copied/adapted another skill's TEXT | YES — check that skill's license |
| You only NAME a tool + show its CLI | NO — tool license irrelevant to your skill's release |
| You bundle a tool's SOURCE/binary in the skill | YES — tool license applies, add its LICENSE |

Known license facts (verified):
- **ClawHub-published skills = MIT-0.** Use/modify/redistribute, including commercially, no
  attribution required. Safest permissive license; you may relicense your derivative (e.g. MIT).
- Common referenced tools: Gitleaks (MIT), Semgrep (LGPL-2.1), NVIDIA SkillSpector (Apache-2.0) —
  all fine to *reference*.
- **Watch for source-available non-OSI licenses** (e.g. OSNL, BSL, SSPL). Example: De-Sloppify
  ships under OSNL — internal use is free for anyone, BUT bundling it into a product you *sell*
  while your company is *not* open-source triggers paid tiers ($1k–10k/mo by revenue). This never
  affects publishing a skill that merely references it; it bites only if the tool becomes a
  dependency of a commercial product. Flag this to the user for their productization plans.

How to verify a license fast: fetch the raw `LICENSE` file from the repo
(`raw.githubusercontent.com/<owner>/<repo>/main/LICENSE`) rather than trusting the GitHub sidebar
label — non-standard licenses (OSNL etc.) get mislabelled or hidden.

**If a referenced tool's license is problematic (or the user plans to sell a product that bundles
it), swap it for a permissive alternative.** Publishing the skill is still legal either way, but a
clean single-license story removes future traps. Method + a verified MIT/Apache tool stack
(jscpd/lizard/scc/dart_code_linter/Gitleaks/Semgrep/SkillSpector) and the specific paywall/language
traps to check → `references/permissive-tool-alternatives.md`.

## Gate 3 — Decouple engine from binding (reusability)

Community value = works outside your project. Confirm the generic engine (workflow, gates,
structure) carries none of the concrete stack, and that stack specifics live in a swappable,
clearly-optional binding/example file. This also sets up any future "sell a template" plan where
the engine is portable and the binding is replaceable.

## Gate 4 — Prove it actually works (behavioral A/B), don't just eyeball it

Before shipping, verify the skill changes behavior: run a **control** subagent (no skill) vs a
**treatment** subagent (with skill) on the SAME designed trap, verify outcomes with facts (re-read
files, re-run commands — not the subagents' self-reports), and map the treatment path onto the
skill's schema. Critical: the trap must be one where the *control arm actually fails*, or success
proves nothing (a too-easy trap where both arms pass measures safety, not effectiveness). Full
method, trap recipes, and the "control must fail" lesson → `references/behavioral-ab-validation.md`.

## Gate 5 — Verify the NAME is free BEFORE building a brand on it (do this FIRST at release time)

A great skill dies invisible if its name collides with existing projects in the same niche.
Renaming is cheap while the skill is still just markdown; it is catastrophic after you've built
reputation, stars, and inbound links on the name. So check availability as the FIRST release step.

Search each surface for the exact candidate name (and obvious variants like `foo-bar` / `foobar`):
- GitHub repos, PyPI, npm — a hit in YOUR niche is a hard blocker (looks like a clone, invisible in search)
- Web search for `"<name>" ai coding agent` etc. — zero software results = you own the whole SERP

Real finding this session: the working name collided with two GitHub projects + a PyPI package in
the exact same "AI coding loop" niche. Generic patterns were saturated — every `X-loop`, `X-guard`,
`slop-X`, `vibe-X`, `-smith`, `ratchet` candidate was already taken. **The winning move is a coined
word that returns zero software results** (the reason names like `desloppify` work — they own the
entire search page from day one). Verify the coined candidate is ALSO clean before committing;
don't hand yourself a second collision. Let the USER pick the final name — it's an irreversible\nbrand decision. Full rename procedure (rename dir → replace brand tokens WITHOUT touching\nindustry terms → validate load) → `references/skill-rename-procedure.md`.

## Positioning for an author with NO prior reputation

When the author has no track record in the domain, do NOT lean the launch on "I'm an expert"
(nothing backs it). Lean on the artifact: **"here's the thing, honestly battle-tested, judge for
yourself."** A published QA report showing found-and-fixed defects (Gate 4) is proof of quality
that needs no résumé — it's the strongest opening for an unknown author. Keep any
fundraising/product pitch OUT of an open-source skill repo: OSS-licensed content used as an
investor funnel repels the very community whose stars would build the author's credibility. The
repo builds reputation; the money conversation lives elsewhere (a separate landing page), linked
by at most one low-key "building something bigger → [contact]" line.

## Attribution ethic (even when not legally required)

MIT-0 needs no attribution, but keep a `references/provenance.md` crediting sources anyway. It is
cheap context, ethically right, and protects you reputationally in a community that values credit.

## Gate 7 — Platform-specific publishing (ClawHub, npm, PyPI)

Each platform has its own gotchas. For ClawHub (Hermes skill registry):
- **Always use `--name` flag** — without it, the directory name becomes the display name
- **Always publish from `git archive <tag>` staging** — clawhub ignores `.gitignore` and leaks internal files
- **Version not visible until scan** — the `OK` response doesn't mean it's listed yet

Full procedure → `references/clawhub-publishing.md`

## Gate 8 — Interpret third-party audit results

When a security auditor (SkillSpector, Semgrep, etc.) flags findings:
- **Code-level defects** (shell=True, env replacement, path injection) → fix these
- **Design-choice flags** (auto-bootstrap, cron, rollback) → these are intentional features, not bugs
- **False assurances** (claimed as enforced but isn't) → fix the claim or add the enforcement

Don't fix design choices to satisfy an auditor — that kills the product.
Full interpretation guide → `references/audit-interpretation.md`

## Gate 9 — Validate markdown structure (rendering integrity)

Unclosed code fences silently destroy the rest of a markdown file. Everything after the
broken fence renders as code — headings, tables, bullet points all vanish. This shipped
for 7 consecutive versions in a real skill before anyone noticed.

**Check before publishing:**

1. **Fence parity.** Count ``` markers in every `.md` file. Odd count = broken.
   ```bash
   awk '/^```/ {c++} END {print "fences: "c" (" (c%2==0 ? "EVEN" : "ODD") ")"}' SKILL.md
   ```
   Every opening ``` must have a closing one. Language-qualified fences (```bash, ```python)
   count as one marker, same as bare ```.

2. **No text leaked inside a code block.** After fixing fences, verify that prose sections
   (headings, tables, bold text) are OUTSIDE code blocks. A quick check: search for
   `##` headings and confirm none appear between unclosed fence pairs. The failure mode:
   the block closes, but content that should be outside was already inside from a prior edit.

3. **No orphaned backticks in inline code.** A misplaced backtick pair can open a code span
   that extends to the next backtick in the document, hiding subsequent content. The tell:
   a heading or sentence suddenly appears in `monospace` in the rendered view.

This is cheap to check (one awk command) and catches a class of bug that survives every
other review because the broken file looks fine in a plain-text editor — the damage only
shows in a renderer.

## Quick pre-release checklist

- [ ] Greped ALL skill files for stack/PII/infra leakage — clean
- [ ] Identified which sources' TEXT was adapted; confirmed their licenses permit release
- [ ] Confirmed referenced tools are only named (not bundled) — their licenses don't bind release
- [ ] Checked any source-available (non-OSI) tool license for downstream productization traps
- [ ] Engine is stack-neutral; specifics isolated in optional binding file
- [ ] provenance.md with credits present
- [ ] Behavioral A/B run on a trap where the control arm actually fails; treatment path maps to schema (Gate 4)
- [ ] Name verified free on GitHub/PyPI/npm/web in the target niche BEFORE branding on it (Gate 5)
- [ ] Markdown fence parity checked in all .md files — no orphaned code blocks (Gate 9)
- [ ] ClawHub-specific checks: `--name` flag used, staging from `git archive` (Gate 7)
- [ ] Audit findings classified: code defects fixed, design choices documented (Gate 8)

## Pitfalls

- **README.md "License" heading is what GitHub displays on the repo page.** Not just the LICENSE
  file. The text under `## License` in README.md (e.g. `[CC BY 4.0](LICENSE) — free for commercial
  use with attribution.`) is what shows in the sidebar and at the bottom of the rendered README.
  If you change LICENSE to MIT-0 but leave README.md saying CC BY 4.0, users see CC BY 4.0 on
  GitHub. Always update BOTH. Verify by opening the repo in a browser after push.
- **Embedded license text in assets (HTML/PNG/SVG).** Architecture diagrams, cover images, and
  interactive HTML pages may contain license strings in footers, watermarks, or metadata
  (e.g. `<div class="foot">keelwright by ratingtesting · CC BY 4.0</div>`). When changing
  license, grep ALL asset files for the old license string and update or remove it. Regenerate
  any PNGs from updated HTML. This is a subset of Gate 1 (grep everything) but catches people
  because they think assets are "just images" and skip them.
- **Trusting the "engine vs binding" split without grepping.** The intent to separate is not the
  same as separation. Verify with a full-dir grep every time.
- **Assuming a referenced tool's copyleft/commercial license infects your skill.** It doesn't, as
  long as you only reference it. Don't over-restrict yourself out of misplaced caution.
- **Reading the GitHub sidebar license label instead of the LICENSE file.** Non-standard licenses
  are frequently mislabelled; fetch the raw text.
- **Branding on a name you never searched.** Generic `X-loop` / `X-guard` / `un-slop` / `vibe-X`
  names in the AI-agent space are saturated — a web + GitHub + PyPI search almost always surfaces a
  collision. Search FIRST; a coined, zero-result word (like `desloppify`) wins the whole search
  page. Renaming after you've accrued stars/reputation is far costlier than renaming a markdown
  skill on day zero. Safe-rename procedure → `references/skill-rename-procedure.md`.
