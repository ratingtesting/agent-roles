# Agents Registry

Source repositories and provenance for every agent role in this repo.


## Source repositories

| Repository | URL | License | Verified | Status |
|------------|-----|---------|----------|--------|
| agency-agents | https://github.com/msitarzewski/agency-agents | MIT | ✅ GitHub | ✅ Used (290 matched, 22 enhanced) |
| Ours (22 critical) | N/A — original authoring on top of agency-agents | MIT-compatible | N/A | ✅ Enhanced 6-slot versions |
| keelwright (author-owned) | https://github.com/ratingtesting/keelwright | MIT-0 | ✅ GitHub (origin/master) | ✅ Author's own skill, reinstalled 2026-08-09 |
| 6 author-owned roles | N/A — created by ratingtesting, not in agency-agents | MIT-0 | N/A | ✅ Project-specific, author-owned |

## License filter (per commercial-no-attribution policy)

- ✅ Loaded (no attribution required): **324** (22 enhanced critical + 295 agency-agents + 1 author-owned keelwright + 6 author-owned roles, all MIT/MIT-0)
- 🚫 Excluded (not from agency-agents / may need attribution): **58** Hermes-native skills (godmode, graphify, mlops, creative, etc. — keelwright + 6 author roles removed from this list)
- ⚠️ Unverified (empty license): 0

## Author-Owned Skill: keelwright

| Field | Value |
|-------|-------|
| Name | `keelwright` |
| Author | ratingtesting (https://github.com/ratingtesting) |
| Repository | https://github.com/ratingtesting/keelwright |
| License | **MIT-0** (verified on GitHub origin/master; stale local copy had CC-BY-4.0, reinstalled) |
| Version | 1.4.1 |
| Purpose | Engine for vibe-coders and loop-coders who ship AI-generated code. Covers 28 known failure modes: SQL injection, hardcoded secrets, hallucinated packages (slopsquatting), reward hacking (AI deletes tests to pass), doom loops (runaway token burn), false reports, missing auth, business logic bypasses, over-engineering. Machine-enforced guardrails (not prompt suggestions). Autonomy dial (Autopilot/Checkpoint/Copilot). Self-healing loop with circuit-breaker limits and Phoenix restart. Plain-language reports for non-developers. Proven by adversarial A/B testing: Keelwright Score (KDS) up to 83/100 on strong models (SWE-bench 78%). |
| Why included | Author's own commercial skill; MIT-0 permits commercial use without attribution. Reinstalled from `origin/master` on 2026-08-09 after stale local copy was found. |
| Platforms | windows, linux, macos |

## Author-Owned Roles (created by ratingtesting, NOT in agency-agents)

All verified absent from upstream `msitarzewski/agency-agents`. Moved to repo top-level with `author: ratingtesting` + `license: MIT-0` injected.

| # | Role | Source (Hermes) | License | Notes |
|---|------|-----------------|---------|-------|
| 1 | `chief-product-architect` | product/chief-product-architect (рой 2) | MIT-0 | Fuses many docs into one master spec |
| 2 | `killer-review-protocol` | product/killer-review-protocol (рой 2) | MIT-0 | Attacks a spec, proves it will fail |
| 3 | `risk-reviewer-legal` | product/risk-reviewer-legal (рой 2) | MIT-0 | Telegram/TON/payments/referral legal risk |
| 4 | `founder-decision-auditor` | product/founder-decision-auditor (рой 4) | MIT-0 | Audit Master decisions vs project docs, read-only |
| 5 | `mvp-experiment-designer` | mvp-experiment-designer (рой 4) | MIT-0 | MVP experiment design |
| 6 | `swarm-synthesis` | swarm-synthesis (рой 4) | MIT-0 | Multi-agent swarm synthesis |


## 22 Enhanced Critical Roles (modified by us)

These were weak in upstream (old format, broken UTF-8 on 4, no slot structure). Rewritten via `agent-authoring` skill with `web_search` fact-checking.

| # | Agent | Upstream source | License | Lines |
|---|-------|----------------|---------|-------|
| 1 | `mobile-app-builder` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-mobile-app-builder.md | MIT (upstream) / Ours (modified) | 72 |
| 2 | `app-store-optimizer` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-app-store-optimizer.md | MIT (upstream) / Ours (modified) | 72 |
| 3 | `rapid-prototyper` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-rapid-prototyper.md | MIT (upstream) / Ours (modified) | 76 |
| 4 | `wechat-mini-program-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-wechat-mini-program-developer.md | MIT (upstream) / Ours (modified) | 75 |
| 5 | `seo-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-seo-specialist.md | MIT (upstream) / Ours (modified) | 73 |
| 6 | `growth-hacker` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-growth-hacker.md | MIT (upstream) / Ours (modified) | 72 |
| 7 | `reddit-community-builder` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-reddit-community-builder.md | MIT (upstream) / Ours (modified) | 71 |
| 8 | `twitter-engager` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-twitter-engager.md | MIT (upstream) / Ours (modified) | 71 |
| 9 | `content-creator` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-content-creator.md | MIT (upstream) / Ours (modified) | 73 |
| 10 | `tiktok-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-tiktok-strategist.md | MIT (upstream) / Ours (modified) | 74 |
| 11 | `social-media-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-social-media-strategist.md | MIT (upstream) / Ours (modified) | 81 |
| 12 | `email-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-email-strategist.md | MIT (upstream) / Ours (modified) | 74 |
| 13 | `founder-visionary` | N/A | MIT (upstream) / Ours (modified) | 73 |
| 14 | `economy-designer` | https://github.com/msitarzewski/agency-agents/blob/main/economy-designer.md | MIT (upstream) / Ours (modified) | 73 |
| 15 | `software-architect` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-software-architect.md | MIT (upstream) / Ours (modified) | 73 |
| 16 | `code-reviewer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-code-reviewer.md | MIT (upstream) / Ours (modified) | 69 |
| 17 | `minimal-change-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-minimal-change-engineer.md | MIT (upstream) / Ours (modified) | 69 |
| 18 | `technical-writer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-technical-writer.md | MIT (upstream) / Ours (modified) | 73 |
| 19 | `mobile-release-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-mobile-release-engineer.md | MIT (upstream) / Ours (modified) | 74 |
| 20 | `i18n-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering-i18n-engineer.md | MIT (upstream) / Ours (modified) | 74 |
| 21 | `multi-platform-publisher` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-multi-platform-publisher.md | MIT (upstream) / Ours (modified) | 84 |
| 22 | `short-video-editing-coach` | https://github.com/msitarzewski/agency-agents/blob/main/marketing-short-video-editing-coach.md | MIT (upstream) / Ours (modified) | 74 |

## 295 Agency-Agents Roles (as-is, MIT)

Verbatim from upstream, converted to 6-slot structure by `convert_all_agents.py`. Not individually enhanced.

| # | Agent | Upstream source | License |
|---|-------|----------------|---------|
| 1 | `academic-anthropologist` | https://github.com/msitarzewski/agency-agents/blob/main/academic/academic-anthropologist.md | MIT (upstream) |
| 2 | `academic-geographer` | https://github.com/msitarzewski/agency-agents/blob/main/academic/academic-geographer.md | MIT (upstream) |
| 3 | `academic-historian` | https://github.com/msitarzewski/agency-agents/blob/main/academic/academic-historian.md | MIT (upstream) |
| 4 | `academic-narratologist` | https://github.com/msitarzewski/agency-agents/blob/main/academic/academic-narratologist.md | MIT (upstream) |
| 5 | `academic-psychologist` | https://github.com/msitarzewski/agency-agents/blob/main/academic/academic-psychologist.md | MIT (upstream) |
| 6 | `academic-statistician` | https://github.com/msitarzewski/agency-agents/blob/main/academic/academic-statistician.md | MIT (upstream) |
| 7 | `accounts-payable-agent` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/accounts-payable-agent.md | MIT (upstream) |
| 8 | `agent-activation-prompts` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/coordination/agent-activation-prompts.md | MIT (upstream) |
| 9 | `agentic-identity-trust` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/agentic-identity-trust.md | MIT (upstream) |
| 10 | `agents-orchestrator` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/agents-orchestrator.md | MIT (upstream) |
| 11 | `automation-governance-architect` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/automation-governance-architect.md | MIT (upstream) |
| 12 | `backend-architect` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-backend-architect.md | MIT (upstream) |
| 13 | `backend-architect-with-memory` | https://github.com/msitarzewski/agency-agents/blob/main/integrations/mcp-memory/backend-architect-with-memory.md | MIT (upstream) |
| 14 | `blender-addon-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/blender/blender-addon-engineer.md | MIT (upstream) |
| 15 | `business-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/business-strategist.md | MIT (upstream) |
| 16 | `change-management-consultant` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/change-management-consultant.md | MIT (upstream) |
| 17 | `chief-financial-officer` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/chief-financial-officer.md | MIT (upstream) |
| 18 | `china-ecommerce-operator` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-china-ecommerce-operator.md | MIT (upstream) |
| 19 | `corporate-training-designer` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/corporate-training-designer.md | MIT (upstream) |
| 20 | `customer-service` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/customer-service.md | MIT (upstream) |
| 21 | `customer-success-manager` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/customer-success-manager.md | MIT (upstream) |
| 22 | `data-consolidation-agent` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/data-consolidation-agent.md | MIT (upstream) |
| 23 | `data-privacy-officer` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/data-privacy-officer.md | MIT (upstream) |
| 24 | `database-optimizer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-database-optimizer.md | MIT (upstream) |
| 25 | `design-brand-guardian` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-brand-guardian.md | MIT (upstream) |
| 26 | `design-image-prompt-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-image-prompt-engineer.md | MIT (upstream) |
| 27 | `design-inclusive-visuals-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-inclusive-visuals-specialist.md | MIT (upstream) |
| 28 | `design-persona-walkthrough` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-persona-walkthrough.md | MIT (upstream) |
| 29 | `design-ui-designer` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-ui-designer.md | MIT (upstream) |
| 30 | `design-ui-finish-gate-reviewer` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-ui-finish-gate-reviewer.md | MIT (upstream) |
| 31 | `design-ux-architect` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-ux-architect.md | MIT (upstream) |
| 32 | `design-ux-researcher` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-ux-researcher.md | MIT (upstream) |
| 33 | `design-visual-storyteller` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-visual-storyteller.md | MIT (upstream) |
| 34 | `design-whimsy-injector` | https://github.com/msitarzewski/agency-agents/blob/main/design/design-whimsy-injector.md | MIT (upstream) |
| 35 | `engineering-ai-data-remediation-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-ai-data-remediation-engineer.md | MIT (upstream) |
| 36 | `engineering-ai-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-ai-engineer.md | MIT (upstream) |
| 37 | `engineering-api-platform-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-api-platform-engineer.md | MIT (upstream) |
| 38 | `engineering-autonomous-optimization-architect` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-autonomous-optimization-architect.md | MIT (upstream) |
| 39 | `engineering-backend-architect` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-backend-architect.md | MIT (upstream) |
| 40 | `engineering-cms-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-cms-developer.md | MIT (upstream) |
| 41 | `engineering-code-reviewer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-code-reviewer.md | MIT (upstream) |
| 42 | `engineering-codebase-onboarding-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-codebase-onboarding-engineer.md | MIT (upstream) |
| 43 | `engineering-data-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-data-engineer.md | MIT (upstream) |
| 44 | `engineering-data-visualization-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-data-visualization-engineer.md | MIT (upstream) |
| 45 | `engineering-database-optimizer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-database-optimizer.md | MIT (upstream) |
| 46 | `engineering-database-reliability-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-database-reliability-engineer.md | MIT (upstream) |
| 47 | `engineering-desktop-app-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-desktop-app-engineer.md | MIT (upstream) |
| 48 | `engineering-developer-tooling-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-developer-tooling-engineer.md | MIT (upstream) |
| 49 | `engineering-devops-automator` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-devops-automator.md | MIT (upstream) |
| 50 | `engineering-drupal-performance` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-drupal-performance.md | MIT (upstream) |
| 51 | `engineering-drupal-shopping-cart` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-drupal-shopping-cart.md | MIT (upstream) |
| 52 | `engineering-email-intelligence-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-email-intelligence-engineer.md | MIT (upstream) |
| 53 | `engineering-embedded-firmware-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-embedded-firmware-engineer.md | MIT (upstream) |
| 54 | `engineering-feishu-integration-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-feishu-integration-developer.md | MIT (upstream) |
| 55 | `engineering-filament-optimization-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-filament-optimization-specialist.md | MIT (upstream) |
| 56 | `engineering-finops-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-finops-engineer.md | MIT (upstream) |
| 57 | `engineering-frontend-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-frontend-developer.md | MIT (upstream) |
| 58 | `engineering-gaussdb-expert` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-gaussdb-expert.md | MIT (upstream) |
| 59 | `engineering-git-workflow-master` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-git-workflow-master.md | MIT (upstream) |
| 60 | `engineering-i18n-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-i18n-engineer.md | MIT (upstream) |
| 61 | `engineering-identity-access-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-identity-access-engineer.md | MIT (upstream) |
| 62 | `engineering-incident-response-commander` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-incident-response-commander.md | MIT (upstream) |
| 63 | `engineering-iot-fleet-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-iot-fleet-engineer.md | MIT (upstream) |
| 64 | `engineering-it-service-manager` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-it-service-manager.md | MIT (upstream) |
| 65 | `engineering-llm-post-training-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-llm-post-training-engineer.md | MIT (upstream) |
| 66 | `engineering-minimal-change-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-minimal-change-engineer.md | MIT (upstream) |
| 67 | `engineering-mobile-app-builder` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-mobile-app-builder.md | MIT (upstream) |
| 68 | `engineering-mobile-release-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-mobile-release-engineer.md | MIT (upstream) |
| 69 | `engineering-multi-agent-systems-architect` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-multi-agent-systems-architect.md | MIT (upstream) |
| 70 | `engineering-network-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-network-engineer.md | MIT (upstream) |
| 71 | `engineering-orgscript-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-orgscript-engineer.md | MIT (upstream) |
| 72 | `engineering-payments-billing-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-payments-billing-engineer.md | MIT (upstream) |
| 73 | `engineering-privacy-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-privacy-engineer.md | MIT (upstream) |
| 74 | `engineering-prompt-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-prompt-engineer.md | MIT (upstream) |
| 75 | `engineering-rag-pipeline-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-rag-pipeline-engineer.md | MIT (upstream) |
| 76 | `engineering-rapid-prototyper` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-rapid-prototyper.md | MIT (upstream) |
| 77 | `engineering-realtime-collaboration-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-realtime-collaboration-engineer.md | MIT (upstream) |
| 78 | `engineering-rust-refactoring-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-rust-refactoring-specialist.md | MIT (upstream) |
| 79 | `engineering-search-relevance-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-search-relevance-engineer.md | MIT (upstream) |
| 80 | `engineering-section-508-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-section-508-specialist.md | MIT (upstream) |
| 81 | `engineering-senior-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-senior-developer.md | MIT (upstream) |
| 82 | `engineering-software-architect` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-software-architect.md | MIT (upstream) |
| 83 | `engineering-solidity-smart-contract-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-solidity-smart-contract-engineer.md | MIT (upstream) |
| 84 | `engineering-sre` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-sre.md | MIT (upstream) |
| 85 | `engineering-technical-writer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-technical-writer.md | MIT (upstream) |
| 86 | `engineering-uswds-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-uswds-developer.md | MIT (upstream) |
| 87 | `engineering-video-streaming-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-video-streaming-engineer.md | MIT (upstream) |
| 88 | `engineering-voice-ai-integration-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-voice-ai-integration-engineer.md | MIT (upstream) |
| 89 | `engineering-webassembly-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-webassembly-engineer.md | MIT (upstream) |
| 90 | `engineering-wechat-mini-program-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-wechat-mini-program-developer.md | MIT (upstream) |
| 91 | `engineering-wordpress-performance` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-wordpress-performance.md | MIT (upstream) |
| 92 | `engineering-wordpress-shopping-cart` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-wordpress-shopping-cart.md | MIT (upstream) |
| 93 | `esg-sustainability-officer` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/esg-sustainability-officer.md | MIT (upstream) |
| 94 | `finance-bookkeeper-controller` | https://github.com/msitarzewski/agency-agents/blob/main/finance/finance-bookkeeper-controller.md | MIT (upstream) |
| 95 | `finance-financial-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/finance/finance-financial-analyst.md | MIT (upstream) |
| 96 | `finance-fpa-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/finance/finance-fpa-analyst.md | MIT (upstream) |
| 97 | `finance-investment-researcher` | https://github.com/msitarzewski/agency-agents/blob/main/finance/finance-investment-researcher.md | MIT (upstream) |
| 98 | `finance-tax-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/finance/finance-tax-strategist.md | MIT (upstream) |
| 99 | `frontend-developer` | https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-frontend-developer.md | MIT (upstream) |
| 100 | `game-audio-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/game-audio-engineer.md | MIT (upstream) |
| 101 | `game-designer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/game-designer.md | MIT (upstream) |
| 102 | `gis-3d-scene-developer` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-3d-scene-developer.md | MIT (upstream) |
| 103 | `gis-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-analyst.md | MIT (upstream) |
| 104 | `gis-bim-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-bim-specialist.md | MIT (upstream) |
| 105 | `gis-cartography-designer` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-cartography-designer.md | MIT (upstream) |
| 106 | `gis-drone-reality-mapping` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-drone-reality-mapping.md | MIT (upstream) |
| 107 | `gis-geoai-ml-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-geoai-ml-engineer.md | MIT (upstream) |
| 108 | `gis-geoprocessing-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-geoprocessing-specialist.md | MIT (upstream) |
| 109 | `gis-qa-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-qa-engineer.md | MIT (upstream) |
| 110 | `gis-solution-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-solution-engineer.md | MIT (upstream) |
| 111 | `gis-spatial-data-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-spatial-data-engineer.md | MIT (upstream) |
| 112 | `gis-spatial-data-scientist` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-spatial-data-scientist.md | MIT (upstream) |
| 113 | `gis-technical-consultant` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-technical-consultant.md | MIT (upstream) |
| 114 | `gis-web-gis-developer` | https://github.com/msitarzewski/agency-agents/blob/main/gis/gis-web-gis-developer.md | MIT (upstream) |
| 115 | `godot-gameplay-scripter` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/godot/godot-gameplay-scripter.md | MIT (upstream) |
| 116 | `godot-multiplayer-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/godot/godot-multiplayer-engineer.md | MIT (upstream) |
| 117 | `godot-shader-developer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/godot/godot-shader-developer.md | MIT (upstream) |
| 118 | `government-digital-presales-consultant` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/government-digital-presales-consultant.md | MIT (upstream) |
| 119 | `grant-writer` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/grant-writer.md | MIT (upstream) |
| 120 | `handoff-templates` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/coordination/handoff-templates.md | MIT (upstream) |
| 121 | `healthcare-aging-parent-care-companion` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/healthcare-aging-parent-care-companion.md | MIT (upstream) |
| 122 | `healthcare-clinical-evidence-agent` | https://github.com/msitarzewski/agency-agents/blob/main/healthcare/healthcare-clinical-evidence-agent.md | MIT (upstream) |
| 123 | `healthcare-customer-service` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/healthcare-customer-service.md | MIT (upstream) |
| 124 | `healthcare-innovation-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/healthcare/healthcare-innovation-strategist.md | MIT (upstream) |
| 125 | `healthcare-marketing-compliance` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/healthcare-marketing-compliance.md | MIT (upstream) |
| 126 | `healthcare-sovereign-health-systems-agent` | https://github.com/msitarzewski/agency-agents/blob/main/healthcare/healthcare-sovereign-health-systems-agent.md | MIT (upstream) |
| 127 | `hospitality-guest-services` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/hospitality-guest-services.md | MIT (upstream) |
| 128 | `hr-onboarding` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/hr-onboarding.md | MIT (upstream) |
| 129 | `identity-graph-operator` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/identity-graph-operator.md | MIT (upstream) |
| 130 | `language-translator` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/language-translator.md | MIT (upstream) |
| 131 | `legal-billing-time-tracking` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/legal-billing-time-tracking.md | MIT (upstream) |
| 132 | `legal-client-intake` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/legal-client-intake.md | MIT (upstream) |
| 133 | `legal-document-review` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/legal-document-review.md | MIT (upstream) |
| 134 | `level-designer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/level-designer.md | MIT (upstream) |
| 135 | `loan-officer-assistant` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/loan-officer-assistant.md | MIT (upstream) |
| 136 | `lsp-index-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/lsp-index-engineer.md | MIT (upstream) |
| 137 | `ma-integration-manager` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/ma-integration-manager.md | MIT (upstream) |
| 138 | `macos-spatial-metal-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/spatial-computing/macos-spatial-metal-engineer.md | MIT (upstream) |
| 139 | `marketing-aeo-foundations` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-aeo-foundations.md | MIT (upstream) |
| 140 | `marketing-agentic-search-optimizer` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-agentic-search-optimizer.md | MIT (upstream) |
| 141 | `marketing-ai-citation-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-ai-citation-strategist.md | MIT (upstream) |
| 142 | `marketing-app-store-optimizer` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-app-store-optimizer.md | MIT (upstream) |
| 143 | `marketing-baidu-seo-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-baidu-seo-specialist.md | MIT (upstream) |
| 144 | `marketing-bilibili-content-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-bilibili-content-strategist.md | MIT (upstream) |
| 145 | `marketing-book-co-author` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-book-co-author.md | MIT (upstream) |
| 146 | `marketing-carousel-growth-engine` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-carousel-growth-engine.md | MIT (upstream) |
| 147 | `marketing-china-ecommerce-operator` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-china-ecommerce-operator.md | MIT (upstream) |
| 148 | `marketing-china-market-localization-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-china-market-localization-strategist.md | MIT (upstream) |
| 149 | `marketing-content-creator` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-content-creator.md | MIT (upstream) |
| 150 | `marketing-cross-border-ecommerce` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-cross-border-ecommerce.md | MIT (upstream) |
| 151 | `marketing-douyin-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-douyin-strategist.md | MIT (upstream) |
| 152 | `marketing-email-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-email-strategist.md | MIT (upstream) |
| 153 | `marketing-global-podcast-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-global-podcast-strategist.md | MIT (upstream) |
| 154 | `marketing-growth-hacker` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-growth-hacker.md | MIT (upstream) |
| 155 | `marketing-instagram-curator` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-instagram-curator.md | MIT (upstream) |
| 156 | `marketing-kuaishou-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-kuaishou-strategist.md | MIT (upstream) |
| 157 | `marketing-linkedin-content-creator` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-linkedin-content-creator.md | MIT (upstream) |
| 158 | `marketing-livestream-commerce-coach` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-livestream-commerce-coach.md | MIT (upstream) |
| 159 | `marketing-multi-platform-publisher` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-multi-platform-publisher.md | MIT (upstream) |
| 160 | `marketing-podcast-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-podcast-strategist.md | MIT (upstream) |
| 161 | `marketing-pr-communications-manager` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-pr-communications-manager.md | MIT (upstream) |
| 162 | `marketing-private-domain-operator` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-private-domain-operator.md | MIT (upstream) |
| 163 | `marketing-reddit-community-builder` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-reddit-community-builder.md | MIT (upstream) |
| 164 | `marketing-seo-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-seo-specialist.md | MIT (upstream) |
| 165 | `marketing-short-video-editing-coach` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-short-video-editing-coach.md | MIT (upstream) |
| 166 | `marketing-social-media-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-social-media-strategist.md | MIT (upstream) |
| 167 | `marketing-tiktok-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-tiktok-strategist.md | MIT (upstream) |
| 168 | `marketing-twitter-engager` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-twitter-engager.md | MIT (upstream) |
| 169 | `marketing-video-optimization-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-video-optimization-specialist.md | MIT (upstream) |
| 170 | `marketing-wechat-official-account` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-wechat-official-account.md | MIT (upstream) |
| 171 | `marketing-weibo-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-weibo-strategist.md | MIT (upstream) |
| 172 | `marketing-x-twitter-intelligence-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-x-twitter-intelligence-analyst.md | MIT (upstream) |
| 173 | `marketing-xiaohongshu-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-xiaohongshu-specialist.md | MIT (upstream) |
| 174 | `marketing-zhihu-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-zhihu-strategist.md | MIT (upstream) |
| 175 | `medical-billing-coding-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/medical-billing-coding-specialist.md | MIT (upstream) |
| 176 | `narrative-designer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/narrative-designer.md | MIT (upstream) |
| 177 | `nexus-spatial-discovery` | https://github.com/msitarzewski/agency-agents/blob/main/examples/nexus-spatial-discovery.md | MIT (upstream) |
| 178 | `nexus-strategy` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/nexus-strategy.md | MIT (upstream) |
| 179 | `operations-manager` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/operations-manager.md | MIT (upstream) |
| 180 | `organizational-psychologist` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/organizational-psychologist.md | MIT (upstream) |
| 181 | `paid-media-auditor` | https://github.com/msitarzewski/agency-agents/blob/main/paid-media/paid-media-auditor.md | MIT (upstream) |
| 182 | `paid-media-creative-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/paid-media/paid-media-creative-strategist.md | MIT (upstream) |
| 183 | `paid-media-paid-social-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/paid-media/paid-media-paid-social-strategist.md | MIT (upstream) |
| 184 | `paid-media-ppc-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/paid-media/paid-media-ppc-strategist.md | MIT (upstream) |
| 185 | `paid-media-programmatic-buyer` | https://github.com/msitarzewski/agency-agents/blob/main/paid-media/paid-media-programmatic-buyer.md | MIT (upstream) |
| 186 | `paid-media-search-query-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/paid-media/paid-media-search-query-analyst.md | MIT (upstream) |
| 187 | `paid-media-tracking-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/paid-media/paid-media-tracking-specialist.md | MIT (upstream) |
| 188 | `personal-growth-mentor` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/personal-growth-mentor.md | MIT (upstream) |
| 189 | `phase-0-discovery` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/playbooks/phase-0-discovery.md | MIT (upstream) |
| 190 | `phase-1-strategy` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/playbooks/phase-1-strategy.md | MIT (upstream) |
| 191 | `phase-2-foundation` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/playbooks/phase-2-foundation.md | MIT (upstream) |
| 192 | `phase-3-build` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/playbooks/phase-3-build.md | MIT (upstream) |
| 193 | `phase-4-hardening` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/playbooks/phase-4-hardening.md | MIT (upstream) |
| 194 | `phase-5-launch` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/playbooks/phase-5-launch.md | MIT (upstream) |
| 195 | `phase-6-operate` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/playbooks/phase-6-operate.md | MIT (upstream) |
| 196 | `product-behavioral-nudge-engine` | https://github.com/msitarzewski/agency-agents/blob/main/product/product-behavioral-nudge-engine.md | MIT (upstream) |
| 197 | `product-feedback-synthesizer` | https://github.com/msitarzewski/agency-agents/blob/main/product/product-feedback-synthesizer.md | MIT (upstream) |
| 198 | `product-manager` | https://github.com/msitarzewski/agency-agents/blob/main/product/product-manager.md | MIT (upstream) |
| 199 | `product-sprint-prioritizer` | https://github.com/msitarzewski/agency-agents/blob/main/product/product-sprint-prioritizer.md | MIT (upstream) |
| 200 | `product-trend-researcher` | https://github.com/msitarzewski/agency-agents/blob/main/product/product-trend-researcher.md | MIT (upstream) |
| 201 | `project-management-experiment-tracker` | https://github.com/msitarzewski/agency-agents/blob/main/project-management/project-management-experiment-tracker.md | MIT (upstream) |
| 202 | `project-management-jira-workflow-steward` | https://github.com/msitarzewski/agency-agents/blob/main/project-management/project-management-jira-workflow-steward.md | MIT (upstream) |
| 203 | `project-management-meeting-notes-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/project-management/project-management-meeting-notes-specialist.md | MIT (upstream) |
| 204 | `project-management-project-shepherd` | https://github.com/msitarzewski/agency-agents/blob/main/project-management/project-management-project-shepherd.md | MIT (upstream) |
| 205 | `project-management-studio-operations` | https://github.com/msitarzewski/agency-agents/blob/main/project-management/project-management-studio-operations.md | MIT (upstream) |
| 206 | `project-management-studio-producer` | https://github.com/msitarzewski/agency-agents/blob/main/project-management/project-management-studio-producer.md | MIT (upstream) |
| 207 | `project-manager-senior` | https://github.com/msitarzewski/agency-agents/blob/main/project-management/project-manager-senior.md | MIT (upstream) |
| 208 | `real-estate-buyer-seller` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/real-estate-buyer-seller.md | MIT (upstream) |
| 209 | `reality-checker` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-reality-checker.md | MIT (upstream) |
| 210 | `recruitment-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/recruitment-specialist.md | MIT (upstream) |
| 211 | `report-distribution-agent` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/report-distribution-agent.md | MIT (upstream) |
| 212 | `resume-tailor` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/resume-tailor.md | MIT (upstream) |
| 213 | `retail-customer-returns` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/retail-customer-returns.md | MIT (upstream) |
| 214 | `roblox-avatar-creator` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/roblox-studio/roblox-avatar-creator.md | MIT (upstream) |
| 215 | `roblox-experience-designer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/roblox-studio/roblox-experience-designer.md | MIT (upstream) |
| 216 | `roblox-systems-scripter` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/roblox-studio/roblox-systems-scripter.md | MIT (upstream) |
| 217 | `sales-account-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-account-strategist.md | MIT (upstream) |
| 218 | `sales-coach` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-coach.md | MIT (upstream) |
| 219 | `sales-data-extraction-agent` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/sales-data-extraction-agent.md | MIT (upstream) |
| 220 | `sales-deal-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-deal-strategist.md | MIT (upstream) |
| 221 | `sales-discovery-coach` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-discovery-coach.md | MIT (upstream) |
| 222 | `sales-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-engineer.md | MIT (upstream) |
| 223 | `sales-offer-lead-gen-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-offer-lead-gen-strategist.md | MIT (upstream) |
| 224 | `sales-outbound-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-outbound-strategist.md | MIT (upstream) |
| 225 | `sales-outreach` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/sales-outreach.md | MIT (upstream) |
| 226 | `sales-pipeline-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-pipeline-analyst.md | MIT (upstream) |
| 227 | `sales-proposal-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/sales/sales-proposal-strategist.md | MIT (upstream) |
| 228 | `scenario-enterprise-feature` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/runbooks/scenario-enterprise-feature.md | MIT (upstream) |
| 229 | `scenario-incident-response` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/runbooks/scenario-incident-response.md | MIT (upstream) |
| 230 | `scenario-marketing-campaign` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/runbooks/scenario-marketing-campaign.md | MIT (upstream) |
| 231 | `scenario-startup-mvp` | https://github.com/msitarzewski/agency-agents/blob/main/strategy/runbooks/scenario-startup-mvp.md | MIT (upstream) |
| 232 | `security-ai-generated-code-auditor` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-ai-generated-code-auditor.md | MIT (upstream) |
| 233 | `security-appsec-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-appsec-engineer.md | MIT (upstream) |
| 234 | `security-architect` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-architect.md | MIT (upstream) |
| 235 | `security-blockchain-security-auditor` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-blockchain-security-auditor.md | MIT (upstream) |
| 236 | `security-cloud-security-architect` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-cloud-security-architect.md | MIT (upstream) |
| 237 | `security-compliance-auditor` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-compliance-auditor.md | MIT (upstream) |
| 238 | `security-incident-responder` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-incident-responder.md | MIT (upstream) |
| 239 | `security-penetration-tester` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-penetration-tester.md | MIT (upstream) |
| 240 | `security-secrets-credential-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-secrets-credential-engineer.md | MIT (upstream) |
| 241 | `security-senior-secops` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-senior-secops.md | MIT (upstream) |
| 242 | `security-threat-detection-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-threat-detection-engineer.md | MIT (upstream) |
| 243 | `security-threat-intelligence-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/security/security-threat-intelligence-analyst.md | MIT (upstream) |
| 244 | `specialized-chief-of-staff` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-chief-of-staff.md | MIT (upstream) |
| 245 | `specialized-civil-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-civil-engineer.md | MIT (upstream) |
| 246 | `specialized-codebase-archaeologist` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-codebase-archaeologist.md | MIT (upstream) |
| 247 | `specialized-cultural-intelligence-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-cultural-intelligence-strategist.md | MIT (upstream) |
| 248 | `specialized-developer-advocate` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-developer-advocate.md | MIT (upstream) |
| 249 | `specialized-document-generator` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-document-generator.md | MIT (upstream) |
| 250 | `specialized-fedramp-rmf-compliance` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-fedramp-rmf-compliance.md | MIT (upstream) |
| 251 | `specialized-french-consulting-market` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-french-consulting-market.md | MIT (upstream) |
| 252 | `specialized-korean-business-navigator` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-korean-business-navigator.md | MIT (upstream) |
| 253 | `specialized-mcp-builder` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-mcp-builder.md | MIT (upstream) |
| 254 | `specialized-model-qa` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-model-qa.md | MIT (upstream) |
| 255 | `specialized-pricing-analyst` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-pricing-analyst.md | MIT (upstream) |
| 256 | `specialized-salesforce-architect` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-salesforce-architect.md | MIT (upstream) |
| 257 | `specialized-strategy-duel-agent` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-strategy-duel-agent.md | MIT (upstream) |
| 258 | `specialized-workflow-architect` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-workflow-architect.md | MIT (upstream) |
| 259 | `strategy-duel-agent` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/specialized-strategy-duel-agent.md | MIT (upstream) |
| 260 | `study-abroad-advisor` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/study-abroad-advisor.md | MIT (upstream) |
| 261 | `supply-chain-strategist` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/supply-chain-strategist.md | MIT (upstream) |
| 262 | `support-analytics-reporter` | https://github.com/msitarzewski/agency-agents/blob/main/support/support-analytics-reporter.md | MIT (upstream) |
| 263 | `support-executive-summary-generator` | https://github.com/msitarzewski/agency-agents/blob/main/support/support-executive-summary-generator.md | MIT (upstream) |
| 264 | `support-finance-tracker` | https://github.com/msitarzewski/agency-agents/blob/main/support/support-finance-tracker.md | MIT (upstream) |
| 265 | `support-infrastructure-maintainer` | https://github.com/msitarzewski/agency-agents/blob/main/support/support-infrastructure-maintainer.md | MIT (upstream) |
| 266 | `support-legal-compliance-checker` | https://github.com/msitarzewski/agency-agents/blob/main/support/support-legal-compliance-checker.md | MIT (upstream) |
| 267 | `support-support-responder` | https://github.com/msitarzewski/agency-agents/blob/main/support/support-support-responder.md | MIT (upstream) |
| 268 | `technical-artist` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/technical-artist.md | MIT (upstream) |
| 269 | `terminal-integration-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/spatial-computing/terminal-integration-specialist.md | MIT (upstream) |
| 270 | `testing-accessibility-auditor` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-accessibility-auditor.md | MIT (upstream) |
| 271 | `testing-api-tester` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-api-tester.md | MIT (upstream) |
| 272 | `testing-evidence-collector` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-evidence-collector.md | MIT (upstream) |
| 273 | `testing-performance-benchmarker` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-performance-benchmarker.md | MIT (upstream) |
| 274 | `testing-reality-checker` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-reality-checker.md | MIT (upstream) |
| 275 | `testing-test-automation-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-test-automation-engineer.md | MIT (upstream) |
| 276 | `testing-test-results-analyzer` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-test-results-analyzer.md | MIT (upstream) |
| 277 | `testing-tool-evaluator` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-tool-evaluator.md | MIT (upstream) |
| 278 | `testing-workflow-optimizer` | https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-workflow-optimizer.md | MIT (upstream) |
| 279 | `unity-architect` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unity/unity-architect.md | MIT (upstream) |
| 280 | `unity-editor-tool-developer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unity/unity-editor-tool-developer.md | MIT (upstream) |
| 281 | `unity-multiplayer-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unity/unity-multiplayer-engineer.md | MIT (upstream) |
| 282 | `unity-shader-graph-artist` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unity/unity-shader-graph-artist.md | MIT (upstream) |
| 283 | `unreal-multiplayer-architect` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unreal-engine/unreal-multiplayer-architect.md | MIT (upstream) |
| 284 | `unreal-systems-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unreal-engine/unreal-systems-engineer.md | MIT (upstream) |
| 285 | `unreal-technical-artist` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unreal-engine/unreal-technical-artist.md | MIT (upstream) |
| 286 | `unreal-world-builder` | https://github.com/msitarzewski/agency-agents/blob/main/game-development/unreal-engine/unreal-world-builder.md | MIT (upstream) |
| 287 | `visionos-spatial-engineer` | https://github.com/msitarzewski/agency-agents/blob/main/spatial-computing/visionos-spatial-engineer.md | MIT (upstream) |
| 288 | `workflow-book-chapter` | https://github.com/msitarzewski/agency-agents/blob/main/examples/workflow-book-chapter.md | MIT (upstream) |
| 289 | `workflow-landing-page` | https://github.com/msitarzewski/agency-agents/blob/main/examples/workflow-landing-page.md | MIT (upstream) |
| 290 | `workflow-startup-mvp` | https://github.com/msitarzewski/agency-agents/blob/main/examples/workflow-startup-mvp.md | MIT (upstream) |
| 291 | `workflow-with-memory` | https://github.com/msitarzewski/agency-agents/blob/main/examples/workflow-with-memory.md | MIT (upstream) |
| 292 | `xr-cockpit-interaction-specialist` | https://github.com/msitarzewski/agency-agents/blob/main/spatial-computing/xr-cockpit-interaction-specialist.md | MIT (upstream) |
| 293 | `xr-immersive-developer` | https://github.com/msitarzewski/agency-agents/blob/main/spatial-computing/xr-immersive-developer.md | MIT (upstream) |
| 294 | `xr-interface-architect` | https://github.com/msitarzewski/agency-agents/blob/main/spatial-computing/xr-interface-architect.md | MIT (upstream) |
| 295 | `zk-steward` | https://github.com/msitarzewski/agency-agents/blob/main/specialized/zk-steward.md | MIT (upstream) |