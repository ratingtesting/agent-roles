# Enhancements — What We Improved and How


## Method

All 22 critical roles were rewritten using the **`agent-authoring`** skill (Nous Research Hermes).
Each was restructured into the 6-slot contract and fact-checked via **`web_search` / `web_extract`** against authoritative 2026 sources.


## 6-Slot Structure (agent-authoring)

```
## Role        — expert anchor
## Context     — inputs to read before acting
## Task        — 4 output-slot contract
## Hard Rules  — red-flag rules (incl. cross_profile=True)
## Output Example — one concrete output fragment
## Dependencies — adjacent roles/teams
## Sources (verified 2026) — web-checked references
```


## What Was Weak in Upstream → What We Fixed

| Problem in upstream | Fix applied |
|---------------------|-------------|
| No slot structure (free-form roleplay prompt) | Enforced 6-slot agent-authoring contract |
| Broken UTF-8 on 4 roles (mobile-app-builder, app-store-optimizer, rapid-prototyper, wechat-mini-program-developer) | Re-encoded, full rewrite |
| Unverified metrics (K-factor >1.0 as norm, retention 40/20/10 as baseline) | Replaced with web-verified 2026 benchmarks |
| Missing Dependencies slot on all | Added explicit dependency map |
| No output contract | Added concrete Output Example per role |

## Fact-Checked Benchmarks (examples)

- **Core Web Vitals**: LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 (Google Search Central 2026)
- **Growth**: K-factor consumer 0.15–0.25, B2B SaaS ~0.20; LTV:CAC 4–8:1 (mobile B2B SaaS) — shno.co / semnexus.com
- **Retention**: Games good D1/D7/D30 = 35/15/5%, top quartile 40/20/10% — playio.co / AppsFlyer 2026
- **Mobile release**: crash-free 99.5%, ANR <0.47% (Play Vitals), phased rollout — StackAuthority 2026
- **i18n**: CLDR plural categories, pseudo-localization in CI, RTL logical CSS — ICU / MDN 2026

## Tooling

- `convert_all_agents.py` — batch-converts all agency-agents `.md` into 6-slot structure
- `agent-authoring` skill — the structural recipe
- `web_search` / `web_extract` — fact verification

## Critical Roles List (22)

`mobile-app-builder`, `app-store-optimizer`, `rapid-prototyper`, `wechat-mini-program-developer`, `seo-specialist`, `growth-hacker`, `reddit-community-builder`, `twitter-engager`, `content-creator`, `tiktok-strategist`, `social-media-strategist`, `email-strategist`, `founder-visionary`, `economy-designer`, `software-architect`, `code-reviewer`, `minimal-change-engineer`, `technical-writer`, `mobile-release-engineer`, `i18n-engineer`, `multi-platform-publisher`, `short-video-editing-coach`