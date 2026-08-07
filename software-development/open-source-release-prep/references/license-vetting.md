# License vetting — knowledge bank

## How to check
Read the raw LICENSE file directly, e.g. `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/LICENSE`
(branch is usually `main` or `master`). Never infer the license from a shields.io badge, a blog
post, or memory — projects relicense (dart_code_metrics → paid DCM is a real example).

## License buckets

| Bucket | Examples | Reference in a skill/doc? | Bundle/link the code? | Commercial resale of a product containing it? |
|---|---|---|---|---|
| Permissive | MIT, MIT-0, Apache-2.0, BSD-2/3, ISC | ✅ free | ✅ free (keep notice) | ✅ free |
| Weak copyleft | LGPL-2.1/3 | ✅ free (no obligation) | ⚠️ dynamic-link ok, keep it replaceable | ⚠️ ok if linked, not modified-static |
| Strong copyleft | GPL-2/3, AGPL | ✅ free (no obligation) | ❌ forces your work open | ❌ / must open source |
| Source-available (LOOKS open, ISN'T) | OSNL, BSL, SSPL, Elastic, "free for internal use only" | ✅ usually free | ⚠️ read terms | ❌ paid tier / forbidden |

**MIT-0** is the most permissive: use/modify/redistribute/relicense, **no attribution required**.
Community skill registries (e.g. ClawHub) commonly publish everything under MIT-0.

## The core insight (why publishing an instructions-only artifact is clean)
A skill/doc that only **names a tool and gives its command line** does not copy, embed, link, or
distribute that tool's source → it is **not redistribution**. Therefore even a GPL/LGPL tool
imposes **no license obligation** on your publication. The end user installs the tool themselves
under that tool's own license. Publish your doc under your own chosen license (MIT).

This breaks only if you actually **bundle/embed/link/copy** the tool's source into your artifact —
then that tool's license binds your artifact.

## Source-available trap (the one that ambushes "sell it later" plans)
Licenses like **OSNL** (Open Source Native License) grant free *internal* use to everyone but
require a **paid tier** to ship the tool inside a product/service if your company is not itself
open source. Free today for your own use ≠ free when you productize. If a "sell templates/products"
step is on your roadmap, screen dependencies for this now and prefer permissive equivalents.

## Recorded tool-swap decisions (loop/vibe-coding quality + supply-chain stack, 2026)
Concrete permissive replacements chosen when a source-available/proprietary tool was a licensing
risk for a publishable artifact:

| Job | Rejected (why) | Chosen (license) |
|---|---|---|
| Code-cleanup / dup + complexity | De-Sloppify (OSNL — paid tier on productization); DCM (proprietary, metrics behind license key + LOC cap) | **jscpd** (MIT, dup, 150+ langs) + **lizard** (MIT, cyclomatic, 17 langs) + **scc** (MIT, LOC+complexity, incl. Dart) |
| Dart-native complexity/metrics | DCM (proprietary/paywall) | **dart_code_linter** (MIT — the maintained OSS fork of the old dart_code_metrics) |
| Malicious / hallucinated package (slopsquatting) | — | **GuardDog** (Datadog, Apache-2.0) — recent-creation/typosquat/exfil/install-script heuristics |
| Dependency CVEs | — | **OSV.dev** API (no local tooling) / **OSV-Scanner** (Google, Apache-2.0, lockfiles) |
| Secrets scan | — | **Gitleaks** (MIT) |
| SAST | — | **Semgrep** (LGPL-2.1 — referenced by command only, so no obligation) |
| Third-party skill/MCP audit before install | anonymous registry "guard" skills | **NVIDIA SkillSpector** (Apache-2.0) |
| Structural erosion (cycles / layer breaks / dead code) — closes "spaghetti / big ball of mud" | — | **madge** (MIT, JS/TS cycles) + **import-linter** (BSD-2, Py cycles+layer contracts) + **eslint-plugin-boundaries** (MIT, Clean-Arch layer enforcement) + **knip** (ISC, JS/TS dead code) + **vulture** (MIT, Py dead code) |

Note: duplication+complexity (jscpd/lizard) catch *volume* erosion only; add the structural stack
above to catch *structural* erosion (cycles, boundary breaks, dead code). Style/naming consistency
has no cheap machine detector — don't claim it's covered.

Fast batch license-verification technique (used this session): instead of opening each raw LICENSE
by hand, query registry metadata in one shot — PyPI JSON (`.info.license` + classifiers) for
Python, `npm view <pkg> license version` for npm. Confirms license + latest version for many
packages quickly. Still spot-check the raw LICENSE for anything ambiguous or source-available.

Rule of thumb that produced these: when a dependency's license is problematic, **swap for a
respected permissive-licensed equivalent** rather than shipping caveats users must honor. Verify
"respected" via stars/contributors/releases and presence in reputable aggregations (e.g.
MegaLinter) — a strong signal, though not a guarantee the tool itself is vulnerability-free (that
risk sits with whoever installs it, under its license).
