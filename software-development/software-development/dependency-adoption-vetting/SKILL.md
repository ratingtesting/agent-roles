---
name: dependency-adoption-vetting
description: Vet a recommended library before building on it.
version: 1.0.0
license: MIT-0
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [dependencies, supply-chain, slopsquatting, vetting, pypi, npm, adoption, due-diligence, r8]
    related_skills: [spike, verification-before-completion, ad-hoc-verification, windows-venv-isolation, open-source-release-prep]
---

# Dependency adoption vetting

Load this whenever a package name arrives as a *recommendation* rather than an existing
project dependency:

- "коллега посоветовал взять библиотеку X" / "a colleague said to use X"
- "ставится через `pip install X`" / "just `npm i X`"
- an agent, a blog post, or an LLM answer proposes a library you have not used before
- you are about to add ANY new entry to `requirements.txt` / `package.json` / `pyproject.toml`

## The core rule

**"The package exists" is the START of vetting, not the end of it.**

The well-known supply-chain gate (slopsquatting / R8) asks *does this package exist, or did an
LLM hallucinate a name an attacker pre-registered?* That gate is necessary and you must run it.
But passing it proves only that the name resolves — it says nothing about whether the library
will actually do the job. A real, MIT-licensed, well-known-author package can still be a trap.

So run **two** gates, in order, and never let gate 1 passing imply gate 2:

| Gate | Question | Fails how |
|---|---|---|
| **1. Genuine?** | Does it exist? Age? Adoption? Malware? Typosquat? | Hallucinated name, freshly-registered lookalike, malicious payload |
| **2. Viable?** | Does it *actually work* for our case, on our runtime, today? | Abandoned, wrong runtime, wrong dialect/scope, plain broken |

**Never report "the package is fine" off gate 1 alone.** Report the recommendation as
*confirmed* only after gate 2 produced real output on disk.

## The four "exists-but-is-a-trap" categories

Every one of these was hit for real in a single session (worked example →
`references/tinyquery-worked-example.md`). Check all four explicitly:

1. **Abandoned.** Last release / last commit years old. Nobody will fix what you find. This
   reframes the dependency as *code you now own*, not a live upstream.
2. **Wrong-runtime metadata.** Declared classifiers disagree with reality — e.g. a package
   marked `Programming Language :: Python :: 2.7` that in fact imports and runs fine on 3.11.
   The metadata can lie in *either* direction; only a run settles it. Note the direction: if it
   works despite the claim, you have no upstream guarantee for future runtimes.
3. **Wrong dialect / narrower scope than advertised.** The blurb matches your task but the
   implementation targets an older or different variant of it. This is the most dangerous
   category because it produces *confident wrong results*: a query/config/format that passes
   locally and fails in production, or vice versa. Always enumerate the boundary (below).
4. **Plain engine bugs.** Unhandled internal exceptions on ordinary combinations of features.
   Distinguish "our usage is wrong" from "the library throws `AttributeError` from its own
   internals" — the latter is a defect, and on an abandoned package it is permanent.

## Gate 1 — genuine? (registry + repo evidence)

Pull real evidence; do not assert from memory (verify before you assert, and prefer "unknown"
to a confident guess).

```bash
# PyPI — full metadata as JSON. Check HTTP code AND the body.
curl -s -o pkg.json -w "HTTP:%{http_code}\n" https://pypi.org/pypi/PACKAGE/json
# npm equivalent: curl -s https://registry.npmjs.org/PACKAGE

# Known CVEs (empty {} == none recorded)
curl -s -X POST https://api.osv.dev/v1/query -H "Content-Type: application/json" \
  -d '{"package":{"name":"PACKAGE","ecosystem":"PyPI"}}'
```

From the PyPI JSON, extract and record these fields — they are the gate-1 *and* gate-2 signal:

`name · version · summary · author · author_email · home_page · project_urls · license ·
requires_python · requires_dist · classifiers` plus, from `releases`, **every version with its
`upload_time`** (this is how you date the abandonment).

Then check the upstream repo state:

```bash
# Follow redirects (-L). A renamed/transferred repo returns 301 with a NULL-filled body,
# which reads as "no data" if you don't follow it.
curl -sL https://api.github.com/repos/OWNER/REPO -o gh.json
```
Record: `full_name` (reveals transfers), `archived`, `pushed_at`, `stargazers_count`,
`open_issues_count`, `license.spdx_id`.

**Malware/typosquat scan:**
```bash
uv tool install guarddog   # or: pip install guarddog
guarddog pypi scan PACKAGE
guarddog npm scan PACKAGE
```

**Red flags → BLOCK and re-confirm the name with the user:** does not exist (404); created in
the last ~30 days; near-zero downloads; a close typo of a popular package; any GuardDog finding.

## Gate 2 — viable? (probe it, don't read about it)

Reading docs and classifiers is not evidence. Install into an **isolated** venv and run it.

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -q --disable-pip-version-check PACKAGE   # POSIX: .venv/bin/python
.venv/Scripts/python.exe -m pip show PACKAGE
```

**Isolation is mandatory, not cosmetic** — without it you may be probing the *agent's* already
installed packages and the result means nothing. On a Hermes/Windows host the agent exports a
`PYTHONPATH` that makes both `pip` and `python` resolve the agent's site-packages first, so
`pip install` can print "Requirement already satisfied" and never install into `.venv` at all —
a silently false probe. Two forms, strongest first:

```bash
env -u PYTHONPATH .venv/Scripts/python -m pip install PACKAGE   # preferred: truly unsets it
PYTHONPATH= .venv/Scripts/python.exe -m pip install PACKAGE     # usually fine; empty, not unset
```

Prefer `env -u PYTHONPATH`. For tools launched through a generated `.exe` wrapper, even an empty
`PYTHONPATH=` can still be consulted first — run `python -m <tool>` from the tool's own venv
instead. Confirm isolation *before* trusting any probe result:

```bash
env -u PYTHONPATH .venv/Scripts/python -c "import sys; print(sys.prefix)"   # must print .../.venv
```

Full detail on this class of environment leak lives in the `windows-venv-isolation` skill —
consult it when probing on Windows.

### Step 2a — the import/construct/execute probe

Write a small probe **file** (not an inline `-c`, which trips the approval gate on some
runtimes) that walks the three stages separately and prints an unambiguous
`PROBE_OK` / `PROBE_FAIL:<stage>` marker:

1. `import` the package — record `__file__`.
2. Construct the main entry object.
3. Execute the most trivial real operation.

Failing at a *specific* stage is the diagnostic. A template lives at
`scripts/probe_dependency.py` — copy it and fill in the three stages.

**Pitfall this catches immediately:** a top-level `__init__.py` that is **empty**, so the
documented `import pkg; pkg.MainClass()` raises `AttributeError: module 'pkg' has no attribute
'MainClass'` and the real entry point is the submodule `from pkg import pkg`. Inspect
`site-packages/<pkg>/` and `grep -n "^class \|    def " <pkg>/<module>.py` to find the true API
instead of guessing from a README.

### Step 2b — the feature-boundary probe loop

This is the step that catches trap category 3, and it is the one most often skipped. Do not
stop at one happy-path call. Run a **battery** of the constructs your users will actually
write, and record pass/fail for each:

```bash
for q in "<construct A>" "<construct B>" "<construct C>"; do
  echo "--- $q"
  .venv/Scripts/python.exe tool.py "$q" 2>/dev/null | grep -E "failed|rows\)"
done
```

Include, deliberately, the modern/canonical forms you *expect* to work — those are the ones
whose failure changes the adoption decision. When something fails, **narrow it**: vary one
factor at a time until you can state the precise rule ("fails on `ORDER BY` *combined with* an
aggregate in the select list; each works alone"). A precise boundary is actionable; "sometimes
crashes" is not.

## Reporting the verdict

Write the findings to a durable note (`NOTES.md` or the spike README) for the team, with a
date and the runtime you tested on. Requirements:

- **Answer the recommender explicitly.** State whether the advice held up. Give the person
  credit where the package really is the right category of tool — then list the caveats.
- **Mark every claim as verified or not.** Anything you did not run is `INCONCLUSIVE`, never
  "clean". If a scanner was unavailable, say exactly that and what *was* checked instead:
  > GuardDog scan NOT run (not installed) → status INCONCLUSIVE, not "clean". Verified only:
  > package exists, 8 years old, known-org author, MIT, no OSV entries.
- **List the untested surface.** Name the features you did not probe so the next person knows
  the edge of the evidence.
- **Separate "our bug" from "their bug."** Show the internal traceback for engine defects.
- **Split the verdict by use case.** The honest answer is usually conditional: fine for A,
  unfit for B. Say which.
- **Leave the go/no-go and the alternatives to the human.** Choosing a dependency is a
  business/process decision. Present options with trade-offs; do not silently substitute a
  different library for the one you were asked to evaluate.

## Do not silently swap the recommendation

If gate 2 finds problems, the deliverable is still what was asked for — the working tool plus
an honest write-up of the risk. Build it, run it, show the output, and let the team decide.
Substituting your preferred library without being asked overrides a decision that is not
yours; listing credible alternatives for them to weigh does not.

## Pitfalls

- **Gate 1 green → assuming safe.** The whole point of this skill. Real ≠ viable.
- **Trusting classifiers/`requires_python` over a run.** Metadata is a claim; a run is evidence.
- **`curl` to a GitHub repo API without `-L`.** A renamed repo answers 301 and a body of
  nulls; without `-L` you conclude "no data" and miss `archived`/`pushed_at`/license entirely.
- **Only checking `info.version`.** You need the `releases` map with `upload_time` to see that
  the "current" version is years old.
- **One happy-path call declared as "it works."** Categories 3 and 4 hide one construct away.
- **Reporting an unavailable scanner as a pass.** A check that could not run has NOT passed.
- **Probing via inline `python -c`.** Trips the script-execution approval gate on some
  runtimes; write a probe file and run the file.
- **Leaving scratch files behind.** Clean up `pkg.json`, `gh.json`, throwaway probes and
  `__pycache__` before reporting; keep the probe script only if it documents a real pitfall.

## Support files

- `references/tinyquery-worked-example.md` — the full session transcript: all four trap
  categories hit on one package, with exact commands, outputs, and the boundary battery.
- `scripts/probe_dependency.py` — copy-and-fill three-stage import/construct/execute probe.
