# 🎭 Agent Roles

> **A complete AI agency at your fingertips** — From frontend wizards to community builders, from whimsy injectors to reality checkers. Each agent is a specialized expert with personality, processes, and proven deliverables.

![License: MIT-0](https://img.shields.io/badge/License-MIT-0-blue.svg)
![Agents](https://img.shields.io/badge/agents-282-green.svg)

---

## 🚀 What Is This?

**The Agency** is a growing collection of meticulously crafted AI agent personalities. Each agent is:

- **🎯 Specialized**: Deep expertise in their domain (not generic prompt templates)
- **🧠 Personality-Driven**: Unique voice, communication style, and approach
- **📋 Deliverable-Focused**: Real code, processes, and measurable outcomes
- **✅ Production-Ready**: Battle-tested workflows and success metrics

**Think of it as**: Assembling your dream team, except they're AI specialists who never sleep, never complain, and always deliver.

---

## ⚡ Quick Start

### Option 1: Install Skills

Copy skills to your Hermes/agent skills directory or install via CLI.

**[⬇ Download the latest release](https://github.com/ratingtesting/agent-roles/releases/latest)**

### Option 2: Pre-configured Agent Swarms

Use ready-to-deploy multi-agent teams from the `examples/` directory for full-stack dev or marketing campaigns.

```bash
# Example: Deploy a full-stack web app team
cat examples/full-stack-web-app.yaml

# Copy skills required for the team into Hermes skills folder
cp frontend-developer/SKILL.md backend-architect/SKILL.md devops-automator/SKILL.md ~/.hermes/skills/
```

### Option 3: Use as Reference

Each agent file (`SKILL.md`) contains:
- Name, emoji, and color
- Core role and personality traits
- Required context before acting
- Task contract (ordered steps)
- Hard rules with red-flags
- Output example
- Dependencies

Browse the agents below and copy/adapt the ones you need!

---

## 🤖 Pre-built Agent Swarms & Teams

Deploy ready-made agent teams configured for specific workflows. Config files are available in `examples/`.

### 1. 🌐 Full-Stack Web App Development Team (`examples/full-stack-web-app.yaml`)
A complete multi-agent pipeline from product definition to production deployment:
- 🎨 **`ui-designer`**: UI/UX design tokens and layout
- 🖥️ **`frontend-developer`**: Responsive, accessible web frontend
- 🏗️ **`backend-architect`**: Scalable API and DB schema
- 🛡️ **`application-security-engineer`**: SDLC security gates
- ⚙️ **`devops-automator`**: CI/CD pipelines & infra
- 🧪 **`flutter-testing-qa-auditor`**: Test coverage & quality gates
- 🎛️ **`agents-orchestrator`**: Master coordinator for cross-agent execution

### 2. 📢 Content & Growth Marketing Swarm (`examples/content-marketing-swarm.yaml`)
An autonomous growth engine for content creation, SEO, and multi-channel distribution:
- ✍️ **`content-creator`**: Copywriting and article generation
- 🔍 **`seo-specialist`**: On-page SEO & search intent optimization
- 👾 **`reddit-community-builder`**: Organic community engagement
- 🎵 **`tiktok-strategist`**: Short-form video planning
- 📊 **`analytics-reporter`**: Conversion metrics and ROI reporting

### 3. 🛡️ Security Audit Swarm (`examples/security-audit-swarm.yaml`)
A hardened audit line from architecture to pentest and remediation:
- 🛡️ **`security-architect`**: Threat modeling & trust boundaries
- 🔐 **`application-security-engineer`**: SDLC gates, SAST/DAST
- ☁️ **`cloud-security-architect`**: Cloud posture & IAM
- ⛓️ **`blockchain-security-auditor`** + **`solidity-smart-contract-engineer`**: Smart-contract audit & fix
- 🗡️ **`penetration-tester`**: Exploit-driven validation
- 🎯 **`threat-detection-engineer`**: SIEM / MITRE detections for findings
- 🔑 **`secrets-credential-hygiene-engineer`**: Secrets scan & rotation
- 🎛️ **`agents-orchestrator`**: Merges reports into one backlog

### 4. 🗺️ GIS & Geo-Intelligence Swarm (`examples/gis-geo-intelligence-swarm.yaml`)
Field → dashboard: from raw geodata and drone capture to 3D and analytics:
- 📦 **`spatial-data-engineer`** + **`geoprocessing-specialist`**: Pipeline & automation
- 🗺️ **`gis-analyst`** + **`gis-qa-engineer`**: Layers, queries & QA
- 🏔️ **`3d-scene-developer`** + **`drone-reality-mapping-specialist`** + **`bim-gis-specialist`**: 3D, reality mesh & BIM-GIS
- 📊 **`spatial-data-scientist`** + **`cartography-designer`** + **`data-visualization-engineer`**: Stats, cartography & honest charts

### 5. 🇨🇳 China Market Entry Swarm (`examples/china-market-entry-swarm.yaml`)
Go-to-market across China's search, social, and commerce stack:
- 🌏 **`china-market-localization-strategist`**: Brand & compliance localization
- 🔍 **`baidu-seo-specialist`**: Baidu ranking & ICP
- 🎵 **`douyin-strategist`** / **`kuaishou-strategist`** / **`bilibili-content-strategist`**: Short-video & community
- 🌸 **`xiaohongshu-specialist`**: UGC & conversion on Xiaohongshu
- 💬 **`wechat-official-account`** + **`wechat-mini-program-developer`**: WeChat ops & Mini Programs
- 🛒 **`china-ecommerce-operator`** + **`cross-border-ecommerce`**: Taobao/PDD/JD & Tmall Global

### 🧩 Agentic Skill Authoring
The template/playbook for creating new commercial-grade agent skills in this repo. Use it whenever you add or adapt a role that will be shipped or resold.
- **What it gives:** `SKILL.md` frontmatter schema, body slots, license/discipline rules, clean-room rewriting, and verified Anthropic agent-design patterns.
- **When to use:** creating a new agent/skill, adapting an existing one for commercial use, writing role prompts for `delegate_task`/kanban, or forcing structure when volume/deadline makes agents cut corners.
- **Inputs:** role brief, target platform/tags, license requirements, source references.
- **Outputs:** ready-to-commit `SKILL.md`, optional `references/` assets, and a `related_skills` wiring checklist.
- **Pair with:** `injection-guard` + `agent-defense` for any web-facing skill.
[`agentic-skill-authoring/SKILL.md`](agentic-skill-authoring/SKILL.md)

---

## 🎨 The Agency Roster

### 💻 Engineering

Building the future, one commit at a time.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/3d-scene-developer.svg" width="24"> | 🏔️ | [3d-scene-developer](3d-scene-developer/SKILL.md) | 3D Scene Developer | Use when 3D visualization of GIS data is needed |
| <img src="avatars/agentic-identity-trust.svg" width="24"> | 🔐 | [agentic-identity-trust](agentic-identity-trust/SKILL.md) | Agentic Identity Trust | Use when an agent identity and trust scheme is needed |
| <img src="avatars/agentic-search-optimizer.svg" width="24"> | 🤖 | [agentic-search-optimizer](agentic-search-optimizer/SKILL.md) | Agentic Search Optimizer | Use when AI agents can't complete tasks on your site. |
| <img src="avatars/ai-data-remediation-engineer.svg" width="24"> | 🧬 | [ai-data-remediation-engineer](ai-data-remediation-engineer/SKILL.md) | Ai Data Remediation Engineer | Use when production data is broken at scale |
| <img src="avatars/ai-developer-experience-auditor.svg" width="24"> | 🤖 | [ai-developer-experience-auditor](ai-developer-experience-auditor/SKILL.md) | Ai Developer Experience Auditor | Use when auditing AI-agent compatibility / AGENTS.md / llms.txt / AI_DEVELOPMENT_RULES in a repository (machine-enforced file checks) |
| <img src="avatars/ai-engineer.svg" width="24"> | 🤖 | [ai-engineer](ai-engineer/SKILL.md) | Ai Engineer | Use when building ML models into production |
| <img src="avatars/ai-generated-code-security-auditor.svg" width="24"> | 🔎 | [ai-generated-code-security-auditor](ai-generated-code-security-auditor/SKILL.md) | Ai Generated Code Security Auditor | Use when auditing security of code from AI assistants |
| <img src="avatars/api-platform-engineer.svg" width="24"> | 🔌 | [api-platform-engineer](api-platform-engineer/SKILL.md) | Api Platform Engineer | Use when designing public/partner APIs |
| <img src="avatars/api-tester.svg" width="24"> | 🔌 | [api-tester](api-tester/SKILL.md) | Api Tester | Use when testing APIs and integrations |
| <img src="avatars/application-security-engineer.svg" width="24"> | 🔐 | [application-security-engineer](application-security-engineer/SKILL.md) | Application Security Engineer | Use when securing code and SDLC |
| <img src="avatars/automation-governance-architect.svg" width="24"> | ⚙️ | [automation-governance-architect](automation-governance-architect/SKILL.md) | Automation Governance Architect | Use when governing business automation decisions |
| <img src="avatars/autonomous-optimization-architect.svg" width="24"> | ⚡ | [autonomous-optimization-architect](autonomous-optimization-architect/SKILL.md) | Autonomous Optimization Architect | Use when cutting AI/API cost autonomously |
| <img src="avatars/backend-architect.svg" width="24"> | 🏗️ | [backend-architect](backend-architect/SKILL.md) | Backend Architect | Use when designing backend systems at scale |
| <img src="avatars/blender-add-on-engineer.svg" width="24"> | 🧩 | [blender-add-on-engineer](blender-add-on-engineer/SKILL.md) | Blender Add On Engineer | Use when building Blender add-ons and automation |
| <img src="avatars/blockchain-security-auditor.svg" width="24"> | 🛡️ | [blockchain-security-auditor](blockchain-security-auditor/SKILL.md) | Blockchain Security Auditor | Use when auditing smart contracts |
| <img src="avatars/cloud-security-architect.svg" width="24"> | ☁️ | [cloud-security-architect](cloud-security-architect/SKILL.md) | Cloud Security Architect | Use when cloud infrastructure security is needed |
| <img src="avatars/cms-developer.svg" width="24"> | 🧱 | [cms-developer](cms-developer/SKILL.md) | Cms Developer | Use when building Drupal/WordPress sites |
| <img src="avatars/codebase-onboarding-engineer.svg" width="24"> | 🧭 | [codebase-onboarding-engineer](codebase-onboarding-engineer/SKILL.md) | Codebase Onboarding Engineer | Use when onboarding devs to a codebase |
| <img src="avatars/data-engineer.svg" width="24"> | 🔧 | [data-engineer](data-engineer/SKILL.md) | Data Engineer | Use when building data pipelines |
| <img src="avatars/data-privacy-officer.svg" width="24"> | 🔐 | [data-privacy-officer](data-privacy-officer/SKILL.md) | Data Privacy Officer | Use when building data privacy compliance |
| <img src="avatars/data-visualization-engineer.svg" width="24"> | 📈 | [data-visualization-engineer](data-visualization-engineer/SKILL.md) | Data Visualization Engineer | Use when designing honest charts |
| <img src="avatars/database-optimizer.svg" width="24"> | 🗄️ | [database-optimizer](database-optimizer/SKILL.md) | Database Optimizer | Use when tuning DB queries/schema |
| <img src="avatars/database-reliability-engineer.svg" width="24"> | 🛟 | [database-reliability-engineer](database-reliability-engineer/SKILL.md) | Database Reliability Engineer | Use when keeping DBs available/safe |
| <img src="avatars/desktop-app-engineer.svg" width="24"> | 💻 | [desktop-app-engineer](desktop-app-engineer/SKILL.md) | Desktop App Engineer | Use when shipping Electron/Tauri desktop apps |
| <img src="avatars/developer-tooling-engineer.svg" width="24"> | 🛠️ | [developer-tooling-engineer](developer-tooling-engineer/SKILL.md) | Developer Tooling Engineer | Use when building CLIs/dev tools |
| <img src="avatars/devops-automator.svg" width="24"> | ⚙️ | [devops-automator](devops-automator/SKILL.md) | Devops Automator | Use when automating CI/CD/infra |
| <img src="avatars/devops-watchdog-engineer.svg" width="24"> | 🛡️ | [devops-watchdog-engineer](devops-watchdog-engineer/SKILL.md) | Devops Watchdog Engineer | Use when building self-healing watchdogs for local services. |
| <img src="avatars/drupal-performance.svg" width="24"> | ⚡ | [drupal-performance](drupal-performance/SKILL.md) | Drupal Performance | Use when accelerating a Drupal site to meet Core Web Vitals |
| <img src="avatars/drupal-shopping-cart.svg" width="24"> | 🛒 | [drupal-shopping-cart](drupal-shopping-cart/SKILL.md) | Drupal Shopping Cart | Use when building Drupal Commerce |
| <img src="avatars/email-intelligence-engineer.svg" width="24"> | 📧 | [email-intelligence-engineer](email-intelligence-engineer/SKILL.md) | Email Intelligence Engineer | Use when parsing email for agents |
| <img src="avatars/embedded-firmware-engineer.svg" width="24"> | 🔩 | [embedded-firmware-engineer](embedded-firmware-engineer/SKILL.md) | Embedded Firmware Engineer | Use when writing MCU/RTOS firmware |
| <img src="avatars/feishu-integration-developer.svg" width="24"> | 🔗 | [feishu-integration-developer](feishu-integration-developer/SKILL.md) | Feishu Integration Developer | Use when integrating Feishu/Lark |
| <img src="avatars/filament-optimization-specialist.svg" width="24"> | 🔧 | [filament-optimization-specialist](filament-optimization-specialist/SKILL.md) | Filament Optimization Specialist | Use when restructuring Filament admin |
| <img src="avatars/finops-engineer.svg" width="24"> | 💰 | [finops-engineer](finops-engineer/SKILL.md) | Finops Engineer | Use when cutting cloud spend |
| <img src="avatars/flutter-architecture-auditor.svg" width="24"> | 🏛️ | [flutter-architecture-auditor](flutter-architecture-auditor/SKILL.md) | Flutter Architecture Auditor | Use when audit Clean Architecture / feature-first / Repository law / boundaries in Flutter projects (machine-enforced grep/analyze) |
| <img src="avatars/flutter-database-storage-auditor.svg" width="24"> | 🗄️ | [flutter-database-storage-auditor](flutter-database-storage-auditor/SKILL.md) | Flutter Database Storage Auditor | Use when auditing Drift / local DB / caching / environments / secrets in Flutter (machine-enforced grep/analyze) |
| <img src="avatars/flutter-security-production-auditor.svg" width="24"> | 🔒 | [flutter-security-production-auditor](flutter-security-production-auditor/SKILL.md) | Flutter Security Production Auditor | Use when auditing security / production-readiness / services-contracts / crash-reporting in Flutter (machine-enforced grep) |
| <img src="avatars/flutter-testing-qa-auditor.svg" width="24"> | 🧪 | [flutter-testing-qa-auditor](flutter-testing-qa-auditor/SKILL.md) | Flutter Testing Qa Auditor | Use when testing / CI/CD / reference tests (Repository, Provider, Auth, Routing, Flags, Drift) audit in Flutter (machine-enforced flutter test) |
| <img src="avatars/frontend-developer.svg" width="24"> | 🖥️ | [frontend-developer](frontend-developer/SKILL.md) | Frontend Developer | Use when building web frontends |
| <img src="avatars/game-audio-engineer.svg" width="24"> | 🎵 | [game-audio-engineer](game-audio-engineer/SKILL.md) | Game Audio Engineer | Use when sound, music, and voice integration into a game is needed |
| <img src="avatars/geoai-ml-engineer.svg" width="24"> | 🤖 | [geoai-ml-engineer](geoai-ml-engineer/SKILL.md) | Geoai Ml Engineer | Use when ML models for images and geodata are needed |
| <img src="avatars/gis-qa-engineer.svg" width="24"> | ✅ | [gis-qa-engineer](gis-qa-engineer/SKILL.md) | Gis Qa Engineer | Use when quality check of geodata and maps is needed |
| <img src="avatars/git-workflow-master.svg" width="24"> | 🌿 | [git-workflow-master](git-workflow-master/SKILL.md) | Git Workflow Master | Use when setting team Git workflow |
| <img src="avatars/godot-gameplay-scripter.svg" width="24"> | 🎯 | [godot-gameplay-scripter](godot-gameplay-scripter/SKILL.md) | Godot Gameplay Scripter | Use when gameplay code and signals are needed in Godot 4 |
| <img src="avatars/godot-multiplayer-engineer.svg" width="24"> | 🌐 | [godot-multiplayer-engineer](godot-multiplayer-engineer/SKILL.md) | Godot Multiplayer Engineer | Use when multiplayer and synchronization are needed in Godot |
| <img src="avatars/godot-shader-developer.svg" width="24"> | 💎 | [godot-shader-developer](godot-shader-developer/SKILL.md) | Godot Shader Developer | Use when shaders and visual effects are needed in Godot |
| <img src="avatars/i18n-engineer.svg" width="24"> | 🌍 | [i18n-engineer](i18n-engineer/SKILL.md) | I18N Engineer | Use when making software multilingual |
| <img src="avatars/identity-access-engineer.svg" width="24"> | 🔐 | [identity-access-engineer](identity-access-engineer/SKILL.md) | Identity Access Engineer | Use when building auth/SSO/RBAC |
| <img src="avatars/identity-graph-operator.svg" width="24"> | 🕸️ | [identity-graph-operator](identity-graph-operator/SKILL.md) | Identity Graph Operator | Use when resolving multi-agent identities |
| <img src="avatars/image-prompt-engineer.svg" width="24"> | 📷 | [image-prompt-engineer](image-prompt-engineer/SKILL.md) | Image Prompt Engineer | Use when you need a prompt for photo generation: light, optics |
| <img src="avatars/infrastructure-maintainer.svg" width="24"> | 🏢 | [infrastructure-maintainer](infrastructure-maintainer/SKILL.md) | Infrastructure Maintainer | Use when infrastructure support is needed: updates, backups |
| <img src="avatars/investment-researcher.svg" width="24"> | 🔍 | [investment-researcher](investment-researcher/SKILL.md) | Investment Researcher | Use when investment analysis is needed: assessment, market analysis |
| <img src="avatars/iot-fleet-engineer.svg" width="24"> | 📡 | [iot-fleet-engineer](iot-fleet-engineer/SKILL.md) | Iot Fleet Engineer | Use when managing device fleets |
| <img src="avatars/jira-workflow-steward.svg" width="24"> | 📋 | [jira-workflow-steward](jira-workflow-steward/SKILL.md) | Jira Workflow Steward | Use when Jira settings are needed: workflow, statuses |
| <img src="avatars/llm-post-training-engineer.svg" width="24"> | 🧪 | [llm-post-training-engineer](llm-post-training-engineer/SKILL.md) | Llm Post Training Engineer | Use when post-training LLMs |
| <img src="avatars/lsp-index-engineer.svg" width="24"> | 🔎 | [lsp-index-engineer](lsp-index-engineer/SKILL.md) | Lsp Index Engineer | Use when building LSP code intelligence |
| <img src="avatars/macos-spatial-metal-engineer.svg" width="24"> | 🍎 | [macos-spatial-metal-engineer](macos-spatial-metal-engineer/SKILL.md) | Macos Spatial Metal Engineer | Use when you need Metal/Spatial code for macOS: GPU, Vision, AR |
| <img src="avatars/minimal-change-engineer.svg" width="24"> | 🪡 | [minimal-change-engineer](minimal-change-engineer/SKILL.md) | Minimal Change Engineer | Use when fixing with minimal diff |
| <img src="avatars/mobile-app-builder.svg" width="24"> | 📲 | [mobile-app-builder](mobile-app-builder/SKILL.md) | Mobile App Builder | Use when building mobile apps |
| <img src="avatars/mobile-release-engineer.svg" width="24"> | 🚀 | [mobile-release-engineer](mobile-release-engineer/SKILL.md) | Mobile Release Engineer | Use when shipping iOS/Android |
| <img src="avatars/multi-agent-systems-architect.svg" width="24"> | 🕸️ | [multi-agent-systems-architect](multi-agent-systems-architect/SKILL.md) | Multi Agent Systems Architect | Use when designing agent systems |
| <img src="avatars/network-engineer.svg" width="24"> | 🌐 | [network-engineer](network-engineer/SKILL.md) | Network Engineer | Use when configuring networks |
| <img src="avatars/organizational-psychologist.svg" width="24"> | 🧠 | [organizational-psychologist](organizational-psychologist/SKILL.md) | Organizational Psychologist | Use when diagnosing team dynamics |
| <img src="avatars/orgscript-engineer.svg" width="24"> | 📜 | [orgscript-engineer](orgscript-engineer/SKILL.md) | Orgscript Engineer | Use when modeling with OrgScript |
| <img src="avatars/payments-billing-engineer.svg" width="24"> | 💳 | [payments-billing-engineer](payments-billing-engineer/SKILL.md) | Payments Billing Engineer | Use when building payments/billing |
| <img src="avatars/penetration-tester.svg" width="24"> | 🗡️ | [penetration-tester](penetration-tester/SKILL.md) | Penetration Tester | Use when a pentest is needed: vulnerabilities, exploitation, report |
| <img src="avatars/privacy-engineer.svg" width="24"> | 🕵️ | [privacy-engineer](privacy-engineer/SKILL.md) | Privacy Engineer | Use when engineering privacy |
| <img src="avatars/prompt-engineer.svg" width="24"> | 🧬 | [prompt-engineer](prompt-engineer/SKILL.md) | Prompt Engineer | Use when crafting LLM prompts |
| <img src="avatars/qa-test-engineer.svg" width="24"> | 🧪 | [qa-test-engineer](qa-test-engineer/SKILL.md) | Qa Test Engineer | Use when running full quality gates: analyze, boundaries, tests, format, de-sloppify. |
| <img src="avatars/rag-pipeline-engineer.svg" width="24"> | 🔍 | [rag-pipeline-engineer](rag-pipeline-engineer/SKILL.md) | Rag Pipeline Engineer | Use when building RAG systems |
| <img src="avatars/rapid-prototyper.svg" width="24"> | ⚡ | [rapid-prototyper](rapid-prototyper/SKILL.md) | Rapid Prototyper | Use when prototyping fast MVPs |
| <img src="avatars/realtime-collaboration-engineer.svg" width="24"> | 🤝 | [realtime-collaboration-engineer](realtime-collaboration-engineer/SKILL.md) | Realtime Collaboration Engineer | Use when building realtime sync |
| <img src="avatars/reddit-community-builder.svg" width="24"> | 💬 | [reddit-community-builder](reddit-community-builder/SKILL.md) | Reddit Community Builder | Use when building authentic brand presence on Reddit. |
| <img src="avatars/roblox-avatar-creator.svg" width="24"> | 👤 | [roblox-avatar-creator](roblox-avatar-creator/SKILL.md) | Roblox Avatar Creator | Use when creating Roblox UGC avatars and accessories |
| <img src="avatars/roblox-experience-designer.svg" width="24"> | 🎪 | [roblox-experience-designer](roblox-experience-designer/SKILL.md) | Roblox Experience Designer | Use when designing Roblox engagement loops |
| <img src="avatars/roblox-systems-scripter.svg" width="24"> | 🔧 | [roblox-systems-scripter](roblox-systems-scripter/SKILL.md) | Roblox Systems Scripter | Use when writing server-side logic and Luau systems for Roblox |
| <img src="avatars/sales-engineer.svg" width="24"> | 🛠️ | [sales-engineer](sales-engineer/SKILL.md) | Sales Engineer | Use when a deal needs technical defense (POC, demo) |
| <img src="avatars/search-query-analyst.svg" width="24"> | 🔍 | [search-query-analyst](search-query-analyst/SKILL.md) | Search Query Analyst | Use when analyzing ad paid-search query reports |
| <img src="avatars/search-relevance-engineer.svg" width="24"> | 🔎 | [search-relevance-engineer](search-relevance-engineer/SKILL.md) | Search Relevance Engineer | Use when tuning search relevance |
| <img src="avatars/secrets-credential-hygiene-engineer.svg" width="24"> | 🔑 | [secrets-credential-hygiene-engineer](secrets-credential-hygiene-engineer/SKILL.md) | Secrets Credential Hygiene Engineer | Use when managing secrets and credentials in code |
| <img src="avatars/security-architect.svg" width="24"> | 🛡️ | [security-architect](security-architect/SKILL.md) | Security Architect | Use when designing a system's security model |
| <img src="avatars/senior-developer.svg" width="24"> | 💎 | [senior-developer](senior-developer/SKILL.md) | Senior Developer | Use when building premium Laravel |
| <img src="avatars/senior-secops-engineer.svg" width="24"> | 🛡️ | [senior-secops-engineer](senior-secops-engineer/SKILL.md) | Senior Secops Engineer | Use when code is checked for secrets and vulnerabilities |
| <img src="avatars/short-video-editing-coach.svg" width="24"> | 🎬 | [short-video-editing-coach](short-video-editing-coach/SKILL.md) | Short Video Editing Coach | Use when editing raw footage into short videos. |
| <img src="avatars/software-architect.svg" width="24"> | 🏛️ | [software-architect](software-architect/SKILL.md) | Software Architect | Use when designing system arch |
| <img src="avatars/solidity-smart-contract-engineer.svg" width="24"> | ⛓️ | [solidity-smart-contract-engineer](solidity-smart-contract-engineer/SKILL.md) | Solidity Smart Contract Engineer | Use when developing and auditing Solidity smart contracts |
| <img src="avatars/solution-engineer.svg" width="24"> | 🔧 | [solution-engineer](solution-engineer/SKILL.md) | Solution Engineer | Use when building GIS prototypes and demos (Esri) |
| <img src="avatars/spatial-data-engineer.svg" width="24"> | 📦 | [spatial-data-engineer](spatial-data-engineer/SKILL.md) | Spatial Data Engineer | Use when cleaning or transforming geospatial data. |
| <img src="avatars/spatial-data-scientist.svg" width="24"> | 📊 | [spatial-data-scientist](spatial-data-scientist/SKILL.md) | Spatial Data Scientist | Use when analyzing spatial statistics or clusters. |
| <img src="avatars/specialized-civil-engineer.svg" width="24"> | 🏗️ | [specialized-civil-engineer](specialized-civil-engineer/SKILL.md) | Specialized Civil Engineer | Use when calculating or checking a structure against building codes |
| <img src="avatars/specialized-developer-advocate.svg" width="24"> | 🗣️ | [specialized-developer-advocate](specialized-developer-advocate/SKILL.md) | Specialized Developer Advocate | Use when building developer communities, DX, and content. |
| <img src="avatars/specialized-salesforce-architect.svg" width="24"> | ☁️ | [specialized-salesforce-architect](specialized-salesforce-architect/SKILL.md) | Specialized Salesforce Architect | Use when designing Salesforce orgs within governor limits. |
| <img src="avatars/sre.svg" width="24"> | 🛡️ | [sre](sre/SKILL.md) | Sre | Use when defining SLOs and cutting production toil. |
| <img src="avatars/swarm-runner-engineer.svg" width="24"> | 🏃 | [swarm-runner-engineer](swarm-runner-engineer/SKILL.md) | Swarm Runner Engineer | Use when engineering the swarm runner: claim-locks, heartbeats, timeouts, agent launch. |
| <img src="avatars/test-automation-engineer.svg" width="24"> | 🎭 | [test-automation-engineer](test-automation-engineer/SKILL.md) | Test Automation Engineer | Use when E2E test automation is needed |
| <img src="avatars/test-results-analyzer.svg" width="24"> | 📋 | [test-results-analyzer](test-results-analyzer/SKILL.md) | Test Results Analyzer | Use when test results analysis is needed |
| <img src="avatars/threat-detection-engineer.svg" width="24"> | 🎯 | [threat-detection-engineer](threat-detection-engineer/SKILL.md) | Threat Detection Engineer | Use when SIEM detections and MITRE are needed |
| <img src="avatars/trend-researcher.svg" width="24"> | 🔭 | [trend-researcher](trend-researcher/SKILL.md) | Trend Researcher | Use when researching market trends |
| <img src="avatars/unity-architect.svg" width="24"> | 🏛️ | [unity-architect](unity-architect/SKILL.md) | Unity Architect | Use when Unity code is tangled; SO architecture is needed. |
| <img src="avatars/unity-editor-tool-developer.svg" width="24"> | 🛠️ | [unity-editor-tool-developer](unity-editor-tool-developer/SKILL.md) | Unity Editor Tool Developer | Use when routine in Unity Editor; tools are needed. |
| <img src="avatars/unity-multiplayer-engineer.svg" width="24"> | 🔗 | [unity-multiplayer-engineer](unity-multiplayer-engineer/SKILL.md) | Unity Multiplayer Engineer | Use when Unity multiplayer, network synchronization. |
| <img src="avatars/unity-shader-graph-artist.svg" width="24"> | ✨ | [unity-shader-graph-artist](unity-shader-graph-artist/SKILL.md) | Unity Shader Graph Artist | Use when Unity shaders/effects are needed; URP/HDRP. |
| <img src="avatars/unreal-multiplayer-architect.svg" width="24"> | 🌐 | [unreal-multiplayer-architect](unreal-multiplayer-architect/SKILL.md) | Unreal Multiplayer Architect | Use when UE5 multiplayer; replication, RPC validation. |
| <img src="avatars/unreal-systems-engineer.svg" width="24"> | ⚙️ | [unreal-systems-engineer](unreal-systems-engineer/SKILL.md) | Unreal Systems Engineer | Use when UE5 systems (GAS, C++/BP, Nanite/Lumen, performance). |
| <img src="avatars/unreal-technical-artist.svg" width="24"> | 🎨 | [unreal-technical-artist](unreal-technical-artist/SKILL.md) | Unreal Technical Artist | Use when UE5 visuals: materials, Niagara, PCG, LOD. |
| <img src="avatars/unreal-world-builder.svg" width="24"> | 🌍 | [unreal-world-builder](unreal-world-builder/SKILL.md) | Unreal World Builder | Use when UE5 open-world: World Partition, Landscape. |
| <img src="avatars/uswds-developer.svg" width="24"> | 🏛️ | [uswds-developer](uswds-developer/SKILL.md) | Uswds Developer | Use when frontend for US government sites on USWDS |
| <img src="avatars/ux-architect.svg" width="24"> | 📐 | [ux-architect](ux-architect/SKILL.md) | Ux Architect | Use when a CSS foundation, layout, or UX structure is needed. |
| <img src="avatars/ux-researcher.svg" width="24"> | 🔬 | [ux-researcher](ux-researcher/SKILL.md) | Ux Researcher | Use when UX research, personas, or tests are needed. |
| <img src="avatars/video-optimization-specialist.svg" width="24"> | 🎬 | [video-optimization-specialist](video-optimization-specialist/SKILL.md) | Video Optimization Specialist | Use when optimizing YouTube video retention. |
| <img src="avatars/video-streaming-engineer.svg" width="24"> | 🎬 | [video-streaming-engineer](video-streaming-engineer/SKILL.md) | Video Streaming Engineer | Use when tuning HLS/DASH delivery and player QoE. |
| <img src="avatars/visionos-spatial-engineer.svg" width="24"> | 🥽 | [visionos-spatial-engineer](visionos-spatial-engineer/SKILL.md) | Visionos Spatial Engineer | Use when building visionOS spatial apps |
| <img src="avatars/voice-ai-integration-engineer.svg" width="24"> | 🎙️ | [voice-ai-integration-engineer](voice-ai-integration-engineer/SKILL.md) | Voice Ai Integration Engineer | Use when speech pipeline: audio transcription |
| <img src="avatars/web-gis-developer.svg" width="24"> | 🌐 | [web-gis-developer](web-gis-developer/SKILL.md) | Web Gis Developer | Use when building interactive web maps |
| <img src="avatars/webassembly-engineer.svg" width="24"> | 🧩 | [webassembly-engineer](webassembly-engineer/SKILL.md) | Webassembly Engineer | Use when porting code to WebAssembly |
| <img src="avatars/wechat-mini-program-developer.svg" width="24"> | 💬 | [wechat-mini-program-developer](wechat-mini-program-developer/SKILL.md) | Wechat Mini Program Developer | Use when building WeChat Mini Programs with wx APIs. |
| <img src="avatars/wordpress-performance.svg" width="24"> | ⚡ | [wordpress-performance](wordpress-performance/SKILL.md) | Wordpress Performance | Use when accelerating WordPress site |
| <img src="avatars/wordpress-shopping-cart.svg" width="24"> | 🛍️ | [wordpress-shopping-cart](wordpress-shopping-cart/SKILL.md) | Wordpress Shopping Cart | Use when building WooCommerce carts, checkouts, payments. |
| <img src="avatars/workflow-architect.svg" width="24"> | 🗺️ | [workflow-architect](workflow-architect/SKILL.md) | Workflow Architect | Use when designing workflows, specifying paths |
| <img src="avatars/workflow-optimizer.svg" width="24"> | ⚡ | [workflow-optimizer](workflow-optimizer/SKILL.md) | Workflow Optimizer | Use when optimizing business workflows |
| <img src="avatars/xr-immersive-developer.svg" width="24"> | 🌐 | [xr-immersive-developer](xr-immersive-developer/SKILL.md) | Xr Immersive Developer | Use when building WebXR experiences |
| <img src="avatars/xr-interface-architect.svg" width="24"> | 🫧 | [xr-interface-architect](xr-interface-architect/SKILL.md) | Xr Interface Architect | Use when designing XR spatial interfaces |

### 🎨 Design

Making it beautiful, usable, and delightful.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/brand-guardian.svg" width="24"> | 🎨 | [brand-guardian](brand-guardian/SKILL.md) | Brand Guardian | Use when brand, identity, and tone of communication are needed |
| <img src="avatars/cartography-designer.svg" width="24"> | 🎨 | [cartography-designer](cartography-designer/SKILL.md) | Cartography Designer | Use when map design and styling are needed |
| <img src="avatars/corporate-training-designer.svg" width="24"> | 📚 | [corporate-training-designer](corporate-training-designer/SKILL.md) | Corporate Training Designer | Use when designing corporate training programs |
| <img src="avatars/economy-designer.svg" width="24"> | 💰 | [economy-designer](economy-designer/SKILL.md) | Economy Designer | Use when you need calculation and balance of a game's virtual economy |
| <img src="avatars/game-designer.svg" width="24"> | 🎮 | [game-designer](game-designer/SKILL.md) | Game Designer | Use when game design, mechanics, GDD and balance are needed |
| <img src="avatars/inclusive-visuals-specialist.svg" width="24"> | 🌈 | [inclusive-visuals-specialist](inclusive-visuals-specialist/SKILL.md) | Inclusive Visuals Specialist | Use when inclusive visuals are needed: accessibility, imagery |
| <img src="avatars/level-designer.svg" width="24"> | 🗺️ | [level-designer](level-designer/SKILL.md) | Level Designer | Use when level design is needed: gameplay, pacing, balance |
| <img src="avatars/narrative-designer.svg" width="24"> | 📖 | [narrative-designer](narrative-designer/SKILL.md) | Narrative Designer | Use when you need a narrative: plot, characters, choice |
| <img src="avatars/persona-walkthrough-specialist.svg" width="24"> | 🎭 | [persona-walkthrough-specialist](persona-walkthrough-specialist/SKILL.md) | Persona Walkthrough Specialist | Use when a CRO audit of a page via persona simulation is needed |
| <img src="avatars/recruitment-specialist.svg" width="24"> | 🎯 | [recruitment-specialist](recruitment-specialist/SKILL.md) | Recruitment Specialist | Use when running China recruitment ops |
| <img src="avatars/specialized-mcp-builder.svg" width="24"> | 🔌 | [specialized-mcp-builder](specialized-mcp-builder/SKILL.md) | Specialized Mcp Builder | Use when building MCP servers with agent-friendly tools. |
| <img src="avatars/technical-artist.svg" width="24"> | 🎨 | [technical-artist](technical-artist/SKILL.md) | Technical Artist | Use when an art pipeline and shaders are needed in the engine |
| <img src="avatars/ui-designer.svg" width="24"> | 🎨 | [ui-designer](ui-designer/SKILL.md) | Ui Designer | Use when designing a UI component system |
| <img src="avatars/ui-finish-gate-reviewer.svg" width="24"> | 🧱 | [ui-finish-gate-reviewer](ui-finish-gate-reviewer/SKILL.md) | Ui Finish Gate Reviewer | Use when UI is template-like before release; needs a pass/hold gate. |
| <img src="avatars/visual-storyteller.svg" width="24"> | 🎬 | [visual-storyteller](visual-storyteller/SKILL.md) | Visual Storyteller | Use when crafting visual narratives |
| <img src="avatars/whimsy-injector.svg" width="24"> | ✨ | [whimsy-injector](whimsy-injector/SKILL.md) | Whimsy Injector | Use when adding playful micro-interactions |

### 💰 Paid Media

Turning ad spend into measurable business outcomes.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/ad-creative-strategist.svg" width="24"> | ✍️ | [ad-creative-strategist](ad-creative-strategist/SKILL.md) | Ad Creative Strategist | Use when creatives and copy for paid advertising |
| <img src="avatars/aeo-foundations.svg" width="24"> | 🏗️ | [aeo-foundations](aeo-foundations/SKILL.md) | Aeo Foundations | Use when auditing AI discovery: crawlers, llms.txt, tokens. |
| <img src="avatars/ai-citation-strategist.svg" width="24"> | 🔮 | [ai-citation-strategist](ai-citation-strategist/SKILL.md) | Ai Citation Strategist | Use when auditing brand visibility in AI answer engines. |
| <img src="avatars/baidu-seo-specialist.svg" width="24"> | 🇨🇳 | [baidu-seo-specialist](baidu-seo-specialist/SKILL.md) | Baidu Seo Specialist | Use when ranking a site in Baidu's China search ecosystem. |
| <img src="avatars/bilibili-content-strategist.svg" width="24"> | 🎬 | [bilibili-content-strategist](bilibili-content-strategist/SKILL.md) | Bilibili Content Strategist | Use when growing a brand channel on Bilibili (B站). |
| <img src="avatars/carousel-growth-engine.svg" width="24"> | 🎠 | [carousel-growth-engine](carousel-growth-engine/SKILL.md) | Carousel Growth Engine | Use when auto-generating TikTok/IG carousels from a URL. |
| <img src="avatars/content-creator.svg" width="24"> | ✍️ | [content-creator](content-creator/SKILL.md) | Content Creator | Use when planning multi-platform content campaigns. |
| <img src="avatars/douyin-strategist.svg" width="24"> | 🎵 | [douyin-strategist](douyin-strategist/SKILL.md) | Douyin Strategist | Use when growing a brand on Douyin (China TikTok). |
| <img src="avatars/email-strategist.svg" width="24"> | 📧 | [email-strategist](email-strategist/SKILL.md) | Email Strategist | Use when segmentation and mailings, deliverability |
| <img src="avatars/global-podcast-strategist.svg" width="24"> | 🎙️ | [global-podcast-strategist](global-podcast-strategist/SKILL.md) | Global Podcast Strategist | Use when launching/growing a podcast brand. |
| <img src="avatars/instagram-curator.svg" width="24"> | 📸 | [instagram-curator](instagram-curator/SKILL.md) | Instagram Curator | Use when building brand presence on Instagram. |
| <img src="avatars/kuaishou-strategist.svg" width="24"> | 🎥 | [kuaishou-strategist](kuaishou-strategist/SKILL.md) | Kuaishou Strategist | Use when growing grassroots audiences on Kuaishou. |
| <img src="avatars/legal-billing-time-tracking.svg" width="24"> | ⏱️ | [legal-billing-time-tracking](legal-billing-time-tracking/SKILL.md) | Legal Billing Time Tracking | Use when tracking legal billing and time |
| <img src="avatars/linkedin-content-creator.svg" width="24"> | 💼 | [linkedin-content-creator](linkedin-content-creator/SKILL.md) | Linkedin Content Creator | Use when building thought leadership on LinkedIn. |
| <img src="avatars/multi-platform-publisher.svg" width="24"> | 📡 | [multi-platform-publisher](multi-platform-publisher/SKILL.md) | Multi Platform Publisher | Use when publishing one article to CN platforms. |
| <img src="avatars/offer-lead-gen-strategist.svg" width="24"> | 🧲 | [offer-lead-gen-strategist](offer-lead-gen-strategist/SKILL.md) | Offer Lead Gen Strategist | Use when you need an offer and lead generation strategy |
| <img src="avatars/paid-media-auditor.svg" width="24"> | 📋 | [paid-media-auditor](paid-media-auditor/SKILL.md) | Paid Media Auditor | Use when a paid traffic audit is needed: metrics, budget waste |
| <img src="avatars/paid-social-strategist.svg" width="24"> | 📱 | [paid-social-strategist](paid-social-strategist/SKILL.md) | Paid Social Strategist | Use when a paid social traffic strategy is needed: Meta, TikTok |
| <img src="avatars/podcast-strategist.svg" width="24"> | 🎧 | [podcast-strategist](podcast-strategist/SKILL.md) | Podcast Strategist | Use when launching a podcast in China's market. |
| <img src="avatars/ppc-campaign-strategist.svg" width="24"> | 💰 | [ppc-campaign-strategist](ppc-campaign-strategist/SKILL.md) | Ppc Campaign Strategist | Use when PPC paid campaign architecture is needed |
| <img src="avatars/pr-communications-manager.svg" width="24"> | 📣 | [pr-communications-manager](pr-communications-manager/SKILL.md) | Pr Communications Manager | Use when managing media relations or crises. |
| <img src="avatars/programmatic-display-buyer.svg" width="24"> | 📺 | [programmatic-display-buyer](programmatic-display-buyer/SKILL.md) | Programmatic Display Buyer | Use when display/programmatic media buying is needed |
| <img src="avatars/seo-specialist.svg" width="24"> | 🔍 | [seo-specialist](seo-specialist/SKILL.md) | Seo Specialist | Use when growing organic search visibility. |
| <img src="avatars/social-media-strategist.svg" width="24"> | 📣 | [social-media-strategist](social-media-strategist/SKILL.md) | Social Media Strategist | Use when planning cross-platform social campaigns. |
| <img src="avatars/tiktok-strategist.svg" width="24"> | 🎵 | [tiktok-strategist](tiktok-strategist/SKILL.md) | Tiktok Strategist | Use when building viral brand presence on TikTok. |
| <img src="avatars/tracking-measurement-specialist.svg" width="24"> | 📡 | [tracking-measurement-specialist](tracking-measurement-specialist/SKILL.md) | Tracking Measurement Specialist | Use when configuring ad conversion tracking |
| <img src="avatars/twitter-engager.svg" width="24"> | 🐦 | [twitter-engager](twitter-engager/SKILL.md) | Twitter Engager | Use when engaging in real-time on Twitter/X. |
| <img src="avatars/wechat-official-account.svg" width="24"> | 📱 | [wechat-official-account](wechat-official-account/SKILL.md) | Wechat Official Account | Use when managing a WeChat Official Account (公众号) |
| <img src="avatars/weibo-strategist.svg" width="24"> | 🔥 | [weibo-strategist](weibo-strategist/SKILL.md) | Weibo Strategist | Use when running brand operations on Weibo. |
| <img src="avatars/x-twitter-intelligence-analyst.svg" width="24"> | 🛰️ | [x-twitter-intelligence-analyst](x-twitter-intelligence-analyst/SKILL.md) | X Twitter Intelligence Analyst | Use when X/Twitter data analysis for decision making |
| <img src="avatars/xiaohongshu-specialist.svg" width="24"> | 🌸 | [xiaohongshu-specialist](xiaohongshu-specialist/SKILL.md) | Xiaohongshu Specialist | Use when marketing lifestyle brands on Xiaohongshu. |

### 💼 Sales

Turning pipeline into revenue through craft, not CRM busywork.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/deal-strategist.svg" width="24"> | ♟️ | [deal-strategist](deal-strategist/SKILL.md) | Deal Strategist | Use when qualifying and strategizing deals |
| <img src="avatars/discovery-coach.svg" width="24"> | 🔍 | [discovery-coach](discovery-coach/SKILL.md) | Discovery Coach | Use when you need an analysis of discovery-call techniques and questioning |
| <img src="avatars/government-digital-presales-consultant.svg" width="24"> | 🏛️ | [government-digital-presales-consultant](government-digital-presales-consultant/SKILL.md) | Government Digital Presales Consultant | Use when pursuing government IT bids |
| <img src="avatars/growth-hacker.svg" width="24"> | 🚀 | [growth-hacker](growth-hacker/SKILL.md) | Growth Hacker | Use when scaling user acquisition via experiments. |
| <img src="avatars/livestream-commerce-coach.svg" width="24"> | 🎙️ | [livestream-commerce-coach](livestream-commerce-coach/SKILL.md) | Livestream Commerce Coach | Use when training hosts for live commerce rooms. |
| <img src="avatars/loan-officer-assistant.svg" width="24"> | 🏦 | [loan-officer-assistant](loan-officer-assistant/SKILL.md) | Loan Officer Assistant | Use when assisting mortgage loan officers |
| <img src="avatars/outbound-strategist.svg" width="24"> | 🎯 | [outbound-strategist](outbound-strategist/SKILL.md) | Outbound Strategist | Use when outreach is needed: emails, sequences, targeting |
| <img src="avatars/pipeline-analyst.svg" width="24"> | 📊 | [pipeline-analyst](pipeline-analyst/SKILL.md) | Pipeline Analyst | Use when a funnel analysis, forecast, and CRM deal scoring is needed |
| <img src="avatars/proposal-strategist.svg" width="24"> | 🏹 | [proposal-strategist](proposal-strategist/SKILL.md) | Proposal Strategist | Use when proposal strategy and narrative (RFP) is needed |
| <img src="avatars/sales-coach.svg" width="24"> | 🏋️ | [sales-coach](sales-coach/SKILL.md) | Sales Coach | Use when coaching sales reps and reviewing funnels |
| 📊 | [sales-data-extraction-agent](sales-data-extraction-agent/SKILL.md) | Sales Data Extraction Agent | Use when extracting sales metrics |
| <img src="avatars/sales-outreach.svg" width="24"> | 🎯 | [sales-outreach](sales-outreach/SKILL.md) | Sales Outreach | Use when running B2B sales outreach |

### 🧠 Strategy

High-level thinking that shapes products, markets, and decisions.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/account-strategist.svg" width="24"> | 🗺️ | [account-strategist](account-strategist/SKILL.md) | Account Strategist | Use when growing existing accounts and NRR |
| <img src="avatars/behavioral-nudge-engine.svg" width="24"> | 🧠 | [behavioral-nudge-engine](behavioral-nudge-engine/SKILL.md) | Behavioral Nudge Engine | Use when adding behavioral nudges to a product |
| <img src="avatars/business-strategist.svg" width="24"> | ♟️ | [business-strategist](business-strategist/SKILL.md) | Business Strategist | Use when making competitive or market strategy |
| <img src="avatars/change-management-consultant.svg" width="24"> | 🔄 | [change-management-consultant](change-management-consultant/SKILL.md) | Change Management Consultant | Use when managing organizational change adoption |
| <img src="avatars/china-market-localization-strategist.svg" width="24"> | 🇨🇳 | [china-market-localization-strategist](china-market-localization-strategist/SKILL.md) | China Market Localization Strategist | Use when localizing a brand for China's platforms. |
| <img src="avatars/grant-writer.svg" width="24"> | 📝 | [grant-writer](grant-writer/SKILL.md) | Grant Writer | Use when writing grant proposals |
| <img src="avatars/healthcare-innovation-strategist.svg" width="24"> | 🧭 | [healthcare-innovation-strategist](healthcare-innovation-strategist/SKILL.md) | Healthcare Innovation Strategist | Use when a healthcare narrative is needed: pitch, regulatory, audit |
| <img src="avatars/narratologist.svg" width="24"> | 📜 | [narratologist](narratologist/SKILL.md) | Narratologist | Use when narrative analysis is needed: structure, genre, myth |
| <img src="avatars/specialized-chief-of-staff.svg" width="24"> | 🧭 | [specialized-chief-of-staff](specialized-chief-of-staff/SKILL.md) | Specialized Chief Of Staff | Use when supporting an executive |
| <img src="avatars/specialized-cultural-intelligence-strategist.svg" width="24"> | 🌍 | [specialized-cultural-intelligence-strategist](specialized-cultural-intelligence-strategist/SKILL.md) | Specialized Cultural Intelligence Strategist | Use when auditing an interface for cultural exclusion |
| ⚔️ | [strategy-duel-agent](strategy-duel-agent/SKILL.md) | Strategy Duel Agent | Use when running a strategic duel: conflict analysis |
| <img src="avatars/study-abroad-advisor.svg" width="24"> | 🎓 | [study-abroad-advisor](study-abroad-advisor/SKILL.md) | Study Abroad Advisor | Use when planning a study-abroad admissions strategy |
| <img src="avatars/supply-chain-strategist.svg" width="24"> | 🔗 | [supply-chain-strategist](supply-chain-strategist/SKILL.md) | Supply Chain Strategist | Use when sourcing suppliers and managing supply chains. |
| <img src="avatars/tax-strategist.svg" width="24"> | 🏛️ | [tax-strategist](tax-strategist/SKILL.md) | Tax Strategist | Use when tax optimization and compliance are needed |
| <img src="avatars/technical-consultant.svg" width="24"> | 🧠 | [technical-consultant](technical-consultant/SKILL.md) | Technical Consultant | Use when GIS strategy and solution selection are needed |
| <img src="avatars/zhihu-strategist.svg" width="24"> | 🧠 | [zhihu-strategist](zhihu-strategist/SKILL.md) | Zhihu Strategist | Use when building brand authority through Zhihu answers. |

### 📦 Product

From roadmap to delivery, shipping what matters.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/bookkeeper-controller.svg" width="24"> | 📒 | [bookkeeper-controller](bookkeeper-controller/SKILL.md) | Bookkeeper Controller | Use when bookkeeping and month-end close |
| <img src="avatars/chief-financial-officer.svg" width="24"> | 💼 | [chief-financial-officer](chief-financial-officer/SKILL.md) | Chief Financial Officer | Use when governing finance and capital decisions |
| <img src="avatars/document-generator.svg" width="24"> | 📄 | [document-generator](document-generator/SKILL.md) | Document Generator | Use when generating PDF/PPTX/DOCX/XLSX via code |
| <img src="avatars/executive-summary-generator.svg" width="24"> | 📝 | [executive-summary-generator](executive-summary-generator/SKILL.md) | Executive Summary Generator | Use when a brief executive summary is needed from a report |
| <img src="avatars/feedback-synthesizer.svg" width="24"> | 🔍 | [feedback-synthesizer](feedback-synthesizer/SKILL.md) | Feedback Synthesizer | Use when needed for user feedback analysis and prioritization |
| <img src="avatars/finance-tracker.svg" width="24"> | 💰 | [finance-tracker](finance-tracker/SKILL.md) | Finance Tracker | Use when budget control and company cash flow management is needed |
| <img src="avatars/financial-analyst.svg" width="24"> | 📊 | [financial-analyst](financial-analyst/SKILL.md) | Financial Analyst | Use when a financial model, forecast, and scenario assessment are needed |
| <img src="avatars/fp-a-analyst.svg" width="24"> | 📈 | [fp-a-analyst](fp-a-analyst/SKILL.md) | Fp A Analyst | Use when budget, forecast, and variance analysis are needed |
| <img src="avatars/meeting-notes-specialist.svg" width="24"> | 📋 | [meeting-notes-specialist](meeting-notes-specialist/SKILL.md) | Meeting Notes Specialist | Use when you need notes from the meeting: minutes, decisions, tasks |
| <img src="avatars/operations-manager.svg" width="24"> | ⚙️ | [operations-manager](operations-manager/SKILL.md) | Operations Manager | Use when optimizing business operations |
| <img src="avatars/product-manager.svg" width="24"> | 🧭 | [product-manager](product-manager/SKILL.md) | Product Manager | Use when a product manager is needed: PRD, roadmap, launch |
| <img src="avatars/project-shepherd.svg" width="24"> | 🐑 | [project-shepherd](project-shepherd/SKILL.md) | Project Shepherd | Use when cross-functional project coordination is needed |
| 📤 | [report-distribution-agent](report-distribution-agent/SKILL.md) | Report Distribution Agent | Use when distributing sales reports |
| <img src="avatars/sprint-prioritizer.svg" width="24"> | 🎯 | [sprint-prioritizer](sprint-prioritizer/SKILL.md) | Sprint Prioritizer | Use when prioritizing backlog or planning sprints. |
| <img src="avatars/studio-operations.svg" width="24"> | 🏭 | [studio-operations](studio-operations/SKILL.md) | Studio Operations | Use when studio operations need optimization |
| <img src="avatars/studio-producer.svg" width="24"> | 🎬 | [studio-producer](studio-producer/SKILL.md) | Studio Producer | Use when portfolio-level project production is needed |

### 🔬 Research

Insights, evidence, and analysis that drive decisions.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/anthropologist.svg" width="24"> | 🌍 | [anthropologist](anthropologist/SKILL.md) | Anthropologist | Use when designing cultures and societies |
| <img src="avatars/evidence-collector.svg" width="24"> | 📸 | [evidence-collector](evidence-collector/SKILL.md) | Evidence Collector | Use when a screenshot-based app review with factual evidence is needed |
| <img src="avatars/experiment-tracker.svg" width="24"> | 🧪 | [experiment-tracker](experiment-tracker/SKILL.md) | Experiment Tracker | Use when design, launch, and analysis of A/B experiments is needed |
| <img src="avatars/gis-analyst.svg" width="24"> | 🖥️ | [gis-analyst](gis-analyst/SKILL.md) | Gis Analyst | Use when maps, layers, and queries of geodata are needed |
| <img src="avatars/historian.svg" width="24"> | 📚 | [historian](historian/SKILL.md) | Historian | Use when history checking is needed: anachronisms, era details |
| <img src="avatars/specialized-pricing-analyst.svg" width="24"> | 💰 | [specialized-pricing-analyst](specialized-pricing-analyst/SKILL.md) | Specialized Pricing Analyst | Use when developing a pricing strategy |
| <img src="avatars/statistician.svg" width="24"> | 📊 | [statistician](statistician/SKILL.md) | Statistician | Use when pressure-testing claims or designing studies. |
| <img src="avatars/threat-intelligence-analyst.svg" width="24"> | 🔍 | [threat-intelligence-analyst](threat-intelligence-analyst/SKILL.md) | Threat Intelligence Analyst | Use when threat intelligence and APT profiling are needed |

### 🛡️ Security

Defending the stack — from secure-by-design architecture to breach response.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/compliance-auditor.svg" width="24"> | 📋 | [compliance-auditor](compliance-auditor/SKILL.md) | Compliance Auditor | Use when auditing SOC 2, ISO compliance |
| <img src="avatars/healthcare-marketing-compliance.svg" width="24"> | ⚕️ | [healthcare-marketing-compliance](healthcare-marketing-compliance/SKILL.md) | Healthcare Marketing Compliance | Use when checking medical advertising for compliance with the law |
| <img src="avatars/legal-compliance-checker.svg" width="24"> | ⚖️ | [legal-compliance-checker](legal-compliance-checker/SKILL.md) | Legal Compliance Checker | Use when compliance verification is needed: laws, risks, sanctions |
| <img src="avatars/specialized-fedramp-rmf-compliance.svg" width="24"> | 🛡️ | [specialized-fedramp-rmf-compliance](specialized-fedramp-rmf-compliance/SKILL.md) | Specialized Fedramp Rmf Compliance | Use when preparing for FedRAMP or NIST RMF |
| <img src="avatars/zk-steward.svg" width="24"> | 🗃️ | [zk-steward](zk-steward/SKILL.md) | Zk Steward | Use when knowledge base, Zettelkasten notes |

### 🗄️ Data & GIS

Data pipelines, geospatial intelligence, and visualization.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/bim-gis-specialist.svg" width="24"> | 🏗️ | [bim-gis-specialist](bim-gis-specialist/SKILL.md) | Bim Gis Specialist | Use when integrating BIM and GIS |
| 🗄️ | [data-consolidation-agent](data-consolidation-agent/SKILL.md) | Data Consolidation Agent | Use when consolidating sales data dashboards |
| <img src="avatars/drone-reality-mapping-specialist.svg" width="24"> | 🛸 | [drone-reality-mapping-specialist](drone-reality-mapping-specialist/SKILL.md) | Drone Reality Mapping Specialist | Use when drone imagery needs to be processed into geospatial data |
| <img src="avatars/gaussdb-expert.svg" width="24"> | 🗄️ | [gaussdb-expert](gaussdb-expert/SKILL.md) | Gaussdb Expert | Use when facing GaussDB OLTP performance issues |
| <img src="avatars/geographer.svg" width="24"> | 🗺️ | [geographer](geographer/SKILL.md) | Geographer | Use when geography of the world needs to be checked for plausibility |
| <img src="avatars/geoprocessing-specialist.svg" width="24"> | ⚙️ | [geoprocessing-specialist](geoprocessing-specialist/SKILL.md) | Geoprocessing Specialist | Use when ArcGIS geodata processing automation is needed |
| <img src="avatars/psychologist.svg" width="24"> | 🧠 | [psychologist](psychologist/SKILL.md) | Psychologist | Use when a psychological character analysis is needed |
| <img src="avatars/specialized-codebase-archaeologist.svg" width="24"> | 🏺 | [specialized-codebase-archaeologist](specialized-codebase-archaeologist/SKILL.md) | Specialized Codebase Archaeologist | Use when auditing code drift across AI tool sessions. |

### 🌍 Regional

Specialists for China, Korea, and global markets.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| <img src="avatars/china-ecommerce-operator.svg" width="24"> | 🛒 | [china-ecommerce-operator](china-ecommerce-operator/SKILL.md) | China Ecommerce Operator | Use when operating a Taobao/PDD/JD store |
| <img src="avatars/cross-border-ecommerce.svg" width="24"> | 🌏 | [cross-border-ecommerce](cross-border-ecommerce/SKILL.md) | Cross Border Ecommerce | Use when launching products on overseas marketplaces |
| <img src="avatars/korean-business-navigator.svg" width="24"> | 🇰🇷 | [korean-business-navigator](korean-business-navigator/SKILL.md) | Korean Business Navigator | Use when deals and negotiations with Korean businesses |
| <img src="avatars/specialized-french-consulting-market.svg" width="24"> | 🇫🇷 | [specialized-french-consulting-market](specialized-french-consulting-market/SKILL.md) | Specialized French Consulting Market | Use when navigating the French ESN freelance market. |

### 🏥 Specialized

Deep expertise for regulated, industry-specific, and niche domains.

| Avatar | Emoji | Agent | Specialty | When to Use |
|--------|-------|-------|-----------|-------------|
| 🩺 | [clinical-evidence-agent](clinical-evidence-agent/SKILL.md) | Clinical Evidence Agent | Use when clinical claims and sources are needed |
| <img src="avatars/customer-service.svg" width="24"> | 🎧 | [customer-service](customer-service/SKILL.md) | Customer Service | Use when handling customer service inquiries |
| <img src="avatars/customer-success-manager.svg" width="24"> | 🌟 | [customer-success-manager](customer-success-manager/SKILL.md) | Customer Success Manager | Use when managing customer success lifecycle |
| <img src="avatars/esg-sustainability-officer.svg" width="24"> | 🌱 | [esg-sustainability-officer](esg-sustainability-officer/SKILL.md) | Esg Sustainability Officer | Use when building ESG reporting programs |
| <img src="avatars/healthcare-aging-parent-care-companion.svg" width="24"> | 🧡 | [healthcare-aging-parent-care-companion](healthcare-aging-parent-care-companion/SKILL.md) | Healthcare Aging Parent Care Companion | Use when coordinating care for an aging relative |
| <img src="avatars/healthcare-customer-service.svg" width="24"> | 🏥 | [healthcare-customer-service](healthcare-customer-service/SKILL.md) | Healthcare Customer Service | Use when supporting patient service inquiries |
| <img src="avatars/hospitality-guest-services.svg" width="24"> | 🏨 | [hospitality-guest-services](hospitality-guest-services/SKILL.md) | Hospitality Guest Services | Use when delivering hospitality guest services |
| <img src="avatars/hr-onboarding.svg" width="24"> | 🤝 | [hr-onboarding](hr-onboarding/SKILL.md) | Hr Onboarding | Use when onboarding new employees |
| <img src="avatars/legal-client-intake.svg" width="24"> | 📋 | [legal-client-intake](legal-client-intake/SKILL.md) | Legal Client Intake | Use when qualifying legal client intakes |
| <img src="avatars/legal-document-review.svg" width="24"> | ⚖️ | [legal-document-review](legal-document-review/SKILL.md) | Legal Document Review | Use when reviewing legal documents |
| <img src="avatars/medical-billing-coding-specialist.svg" width="24"> | 🏥 | [medical-billing-coding-specialist](medical-billing-coding-specialist/SKILL.md) | Medical Billing Coding Specialist | Use when coding medical billing claims |
| <img src="avatars/retail-customer-returns.svg" width="24"> | 🛒 | [retail-customer-returns](retail-customer-returns/SKILL.md) | Retail Customer Returns | Use when processing retail returns |
| 🌍 | [sovereign-health-systems-agent](sovereign-health-systems-agent/SKILL.md) | Sovereign Health Systems Agent | Use when engaging health ministries or sovereign markets. |

---

## 📜 License

MIT-0 — Use freely, commercially or personally. No attribution required.

## 🙏 Acknowledgments

This collection brings together **282+ specialized agents** across every division, built for real-world workflows and production use.

## 💬 Community

- **GitHub Discussions**: Share your success stories
- **Issues**: Report bugs or request features

## 🚀 Get Started

1. **Browse** the agents above and find specialists for your needs
2. **Copy** the agents to your skills directory
3. **Activate** agents by referencing them in your conversations
4. **Customize** agent personalities and workflows for your needs

---

<div align="center">

**🎭 The Agency: Your AI Dream Team Awaits 🎭**

[⭐ Star this repo](https://github.com/ratingtesting/agent-roles) • [🐛 Report an issue](https://github.com/ratingtesting/agent-roles/issues)

Made with ❤️ by the community, for the community

</div>