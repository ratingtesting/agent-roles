# Swapping a problematically-licensed tool for a permissive one

When a skill references a tool whose license is source-available/non-OSI (OSNL, BSL, SSPL) or
proprietary-with-paywall, publishing the skill is still fine (mention ≠ redistribution, see Gate
2). But you often want to swap it anyway, because:

- The user plans to **bundle it into a product they sell** → source-available tiers or paywalls bite.
- You want **one clean licensing story** for the whole skill so nobody has to reason about tiers.
- The tool requires **activation / license keys / LOC caps** even on its "free" plan (friction +
  future paywall risk on the exact feature you need).

## Method: find a respected permissive alternative

1. **Name the job precisely.** Decompose the problematic tool into the primitive jobs it does
   (e.g. De-Sloppify = duplication detection + cyclomatic complexity + dead code + an aggregate
   score). You usually replace one all-in-one tool with 2-3 focused CLIs.
2. **Search for alternatives + "license"** and prefer OSI-permissive (MIT/Apache/BSD). Weigh
   community respect: stars, contributor count, presence in aggregators (e.g. MegaLinter),
   maintenance recency.
3. **Verify the license from the raw LICENSE file**, never the GitHub sidebar label
   (`raw.githubusercontent.com/<owner>/<repo>/main/LICENSE` or `master`).
4. **Check the specific feature you need is in the free/permissive scope**, not gated. Trap seen
   this session: DCM's *free plan* still needs `dcm activate --license-key`, has a LOC cap, and
   moves *cyclomatic complexity* (the exact metric wanted) into a paid tier — so it reproduced the
   very problem we were escaping.
5. **Check language coverage** for the target stack before committing. Trap: `lizard` supports 17
   languages but **not Dart**; `scc` and `jscpd` do cover Dart. Language gaps silently make a tool
   useless for a specific binding.
6. **Rebuild any lost aggregate metric yourself**, transparently. Losing a vendor's single
   "quality score 0-100" is fine: combine the primitives with explicit thresholds
   (`score = 100 − dup% × k1 − funcs_over_CCN × k2`). Self-set thresholds are more honest (can't be
   gamed by loosening a hidden vendor metric) and carry no license.

## Verified permissive code-quality tool stack (checked this session)

| Job | Tool | License | Notes |
|---|---|---|---|
| Duplication (copy/paste) | **jscpd** | MIT | 150-223 formats incl. Dart; token-based, fast |
| Cyclomatic complexity | **lizard** | MIT | 17 langs (cpp/java/c#/js/ts/py/ruby/php/swift/scala/go/rust/lua/plsql/…); **no Dart** |
| LOC + complexity estimate | **scc** | MIT | Go; very fast; broad coverage incl. Dart; COCOMO |
| Dart complexity/metrics | **dart_code_linter** | MIT | Bancolombia's maintained OSS fork of the old dart_code_metrics (the codebase DCM grew from); no key, no LOC cap |
| Secrets | **Gitleaks** | MIT | staged-diff + full-history |
| SAST | **Semgrep** | LGPL-2.1 | `--config=auto`; referenced-only, so LGPL doesn't bind the skill |
| 3rd-party skill audit | **NVIDIA SkillSpector** | Apache-2.0 | `--no-llm` static scan before install |
| Circular dependencies | **madge** (JS/TS) · **import-linter** (Py) | MIT · BSD-2 | `madge --circular ./src`; import-linter enforces `.importlinter` contracts |
| Layer/boundary violations | **eslint-plugin-boundaries** (JS/TS) · **import-linter** (Py) | MIT · BSD-2 | mechanically enforce a Clean-Arch dependency rule |
| Dead code (lava flow) | **knip** (JS/TS) · **vulture** (Py) | ISC · MIT | unused files/exports/functions; `vulture pkg/ --min-confidence 80` |

**Structural-integrity stack insight (verified this session):** duplication (jscpd) + complexity
(lizard/scc) only catch *volume* erosion. To close **"spaghetti code / big ball of mud" fully** you
also need three structural checks — **cycles** (madge/import-linter), **layer boundaries**
(eslint-plugin-boundaries/import-linter), and **dead code** (knip/vulture). All five categories are
MIT/BSD-2/ISC → one clean permissive story, safe for a sell-later roadmap. What still has *no cheap
machine detector*: **stylistic** consistency (naming drift, async/await vs promise mixing) — be
honest and mark that ⚠️ partial rather than claiming the gate prevents all drift.

## Tools deliberately rejected (for reference)

- **De-Sloppify** — OSNL (source-available). Free internally for anyone, but paid tiers if bundled
  into a product sold by a non-open-source company. Great tool; wrong license for a "sell it later"
  roadmap.
- **DCM (dcm.dev)** — proprietary; free plan needs license-key activation + has a LOC cap + gates
  cyclomatic complexity behind a paid tier. Reintroduced exactly the constraint we were removing.
