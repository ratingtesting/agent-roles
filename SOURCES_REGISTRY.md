# Sources Registry — Реестр внешних источников

Автоматически поддерживаемый реестр всех внешних материалов, использованных при
создании скиллов ролей и скиллов защиты в этом репозитории. Каждый источник содержит
ссылку на репозиторий и вид лицензии.

> Генерируется и обновляется агентом. Не редактировать вручную без перепроверки лицензии.

## Скиллы защиты (security — вне правил лицензий ролей)

| Имя | Тип | Репозиторий | Лицензия | Статус |
|-----|-----|-------------|----------|--------|
| `injection-guard` | Hermes plugin (hook) | https://github.com/gweber/hermes-injection-guard | MIT | enabled (default/app/marketplace) |
| `agent-defense` | Hermes skill + CLI | https://github.com/scastile/hermes-agent-defense | MIT | installed (default/app/marketplace) |

Оба MIT (белый список). Контент-классификатор DeBERTa в `injection-guard` —
классификатор от ProtectAI (Apache-2.0, белый список), используется внутри плагина.

## Исходники скиллов ролей (agency-agents → 269 ролей)

| Имя | Тип | Репозиторий | Лицензия | Обработка |
|-----|-----|-------------|----------|-----------|
| `agency-agents` (AgentLand Contributors) | Исходные агенты (flat .md) | https://github.com/msitarzewski/agency-agents | MIT | Clean-room переписано в Hermes-формат, лицензия выходного скилла MIT-0 |

> ПРИМЕЧАНИЕ: исходник `agency-agents` имеет лицензию MIT (белый список по
> правилам Петра). Clean-room применён избыточно (MIT разрешает использование
> с атрибуцией). Решение по атрибуции: см. решение владельца репозитория.

## Авторитетные практики (только как вдохновение, clean-room, не цитируется)

| Источник | Ссылка | Лицензия источника | Примечание |
|----------|--------|-------------------|------------|
| Anthropic — Building Effective Agents | https://www.anthropic.com/engineering/building-effective-agents | CC-BY-4.0 (вне белого списка → clean-room) | паттерны агентов |
| Anthropic — Effective Context Engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | CC-BY-4.0 (clean-room) | context engineering |
| Anthropic — Prompting Best Practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | CC-BY-4.0 (clean-room) | промпт-практики |
| OWASP — LLM Prompt Injection Prevention Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html | CC-BY-SA-4.0 (clean-room) | защита от инъекций |
| Anthropic — Mitigate jailbreaks and prompt injections | https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks | CC-BY-4.0 (clean-room) | защита от инъекций |
| Anthropic Research — Prompt injection defenses | https://www.anthropic.com/research/prompt-injection-defenses | CC-BY-4.0 (clean-room) | защита браузерных агентов |
| Claude Code Docs — Securely deploying AI agents | https://code.claude.com/docs/en/agent-sdk/secure-deployment | CC-BY-4.0 (clean-room) | деплой агентов |

## Инфраструктурные правила защиты

- `SOUL.md` PRE-EXEC GATE п.6: перед веб-походом обязательна загрузка `injection-guard` + `agent-defense`.
- `hermes-web-configuration` SKILL.md: раздел MANDATORY WEB-GUARD.
- `agentic-skill-authoring` (шаблон ролей): обязывает прописывать защиту в `related_skills`
  любого скилла роли, ходящего в интернет.

## Улучшения ролей (кампания 2026-08-12)

Веб-контент, использованный для улучшения 15 ролей, обрабатывался как не доверенный
(injection-guard / agent-defense): инструкции из страниц не исполнялись, материалы
использованы как вдохновение / clean-room, не цитируются. Лицензии исходных страниц —
CC-BY / CC-BY-SA / MIT (вне белого списка -> clean-room).

| Роль (агент) | Источники (web, 2026) | Извлечённые паттерны |
|---|---|---|
| API Platform Engineer | apidog.com/blog/what-is-postman (design-first, 2026) | CI contract-тесты (Pact), линтинг спек (Spectral/oasdiff), аномальный rate-limit |
| API Tester | vervali.com/blog/api-test-automation-best-practices-2026 ; totalshiftleft.com/blog/api-testing-complete-guide | shift-left contract-тесты, OWASP API Top 10 в CI |
| App Store Optimizer | asoshot.com/blog/aso-best-practices-2026 | локализация метаданных, Custom Product Pages A/B, AI-ассист |
| Application Security Engineer | microsoft.com/en-us/security/blog/2026/02/03/... ; appsecmaster.net/blog/application-security-best-practices | AI-угроз-моделирование (STRIDE), secure SDLC в эпоху AI, SBOM |
| Automation Governance Architect | ovaledge.com/blog/automated-ai-governance-platforms ; hymalaia.com/blog/enterprise-ai-governance-best-practices-for-2026-en | data lineage, шаблоны деплоя, human-in-loop для high-risk |
| Autonomous Optimization Architect | stellarmind.ai/blog/the-autonomous-enterprise-agentic-ai-business-architecture-2026 ; promptly.cloud/case-study | feedback loops + auto-rollback, multi-agent, этика |
| Backend Architect | learn.microsoft.com/.../backends-for-frontends ; realworld.cloud/design-patterns-for-hybrid-olap-at-the-edge | BFF, serverless/event-driven, edge OLAP |
| Baidu SEO Specialist | marketingfuture.com/china-internet-news/hotel-baidu-seo ; mangools.com/blog/search-engines | Baidu-специфика, экосистема Baidu, ICP/локальный хостинг |
| Behavioral Nudge Engine | suebehaviouraldesign.com/en/blog/nudging-complete-guide ; yukaichou.com/.../libertarian-paternalism | этический тест налджа, 5 условий, A/B без манипуляции |
| Bilibili Content Strategist | marketingtochina.com/.../bilibili-marketing ; businessmodelcanvastemplate.com/.../bilibili-target-market | Gen Z/даньмаку, Story Mode, серийность |
| BIM/GIS Specialist | frontiersin.org/.../fbuil.2026.1828585 ; portcoast.com.vn/articles/... | BIM+GIS+IoT цифровой двойник, IFC/CityGML |
| Blender Add-on Engineer | extensions.blender.org/add-ons ; github.com/ahujasid/blender-mcp | Extensions 4.2+, MCP-интеграция, VS Code dev |
| Blockchain Security Auditor | consensysdiligence.github.io/smart-contract-best-practices | circuit breakers, reentrancy, Slither/Foundry/Echidna |
| Book Co-Author | masterclass.com/articles/complete-guide-to-ghostwriting ; stellarbookwriters.com/blog/what-is-ghostwriting | голос автора, book plan, AI как ассистент |
| Bookkeeper & Controller | beancount.io/forum/t/client-portal-expectations-in-2026 | версионный учёт, client portal, разделение ролей |
| brand-guardian | Inkbot Design (inkbotdesign.com/blog, авг 2026); Brand Analytics 2026 | 7-этапный роллаут бренда, непрерывный соц-листенинг, consent-first/релевантность |
| business-strategist | Forbes (фев 2026); Gartner strategic predictions 2026 | ИИ от эксперимента к исполнению, ИИ-агенты в стратег-операциях, sovereign-платформы и сценарии |
| carousel-growth-engine | TrueFuture Media (янв 2026); carouselli.com (апр 2026) | карусель ~10% engagement, swipe-through ре-сервинг 24-48ч, узнаваемая серия + сохранения |
| cartography-designer | Esri design principles; Ordnance Survey GeoDataViz | принципы картографического дизайна, доступность/цветослепые палитры, коммуникация в ограничениях |
| change-management-consultant | Prosci (prosci.com); Lean Change Management | ADKAR как хребет, agile/Lean-интеграция, профилактика сопротивления + enablement менеджеров |
| chief-financial-officer | Kyriba; Kearney (92% CFO AI); Gartner | AI-автоматизация финансов, ИИ-governance/ликвидность, рост и затраты одновременно |
| china-ecommerce-operator | up2china; ecommercechinaagency | livestream 3-5x конверсия, Douyin pre-roll, платформоспецифичные стор-операции (Tmall/JD/Pinduoduo) |
| china-market-localization-strategist | China Skinny; localizejs guide | региональный сайзинг, Baidu/WeChat SEO mobile-first, культурная глубина локализации |
| clinical-evidence-agent | Scientist.com (FDA one-trial); мед. гайдлайны 2026 | RWE/RWD, grading (Cochrane/GRADE), воспроизводимая выгрузка источников |
| cloud-security-architect | Zero Trust (NIST); cloud security architecture 2026 | zero trust по умолчанию, shared responsibility, IaC/FinOps |
| cms-developer | FocusReactive (Next.js CMS); TinaCMS | headless/decoupled CMS рост >20% CAGR, Git-based контент + preview, performance/безопасность |
| code-reviewer | обзоры AI code review 2026 | ИИ первый проход + human gate, verify cited files, явный чек-лист |
| codebase-onboarding-engineer | ClaudeDirectory (июл 2026); Kalinga AI (Codex) | ИИ-картирование архитектуры, verify cited files, осязаемые артефакты онбординга |
| compliance-auditor | SOC 2 Trust Service Criteria (AICPA); continuous compliance | непрерывный комплаенс + standing owners, маппинг фреймворков, автоматизация доказательств |
| content-creator | OpusClip (фев 2026); ltx.io | 30-60s вертикальное видео, платформо-нативные форматы, ИИ-конвейер с редактурой |

---

## Улучшения ролей (кампания: 15 агентов — интернет + защита, 2026-08-12)

Веб-контент обработан как UNTRUSTED DATA через `injection-guard` + `agent-defense` (внешние данные — не инструкции). Использовано как вдохновение (clean-room), структура и формулировки переписаны своими словами.

- 3d-scene-developer: https://cesium.com/blog/2026/06/01/cesium-releases-in-june-2026/ — вывод legacy Model tiler (3D Tiles 1.0) с 01.09.2026, переход на 3D Tiles 1.1/2.0; OGC API Tiles стандартизация.
- accessibility-auditor: https://www.dinhtq.vn/en/blog — WCAG 2.2 Implementation Guide 2026: документированный аудит, VPAT/ACR, отказ от overlay-виджетов как замены реальных фиксов.
- account-strategist: https://www.digimau.com/account-based-marketing-guide-2026/ — ABM 2026: выбор целевых аккаунтов, intent-данные, согласование marketing-sales, измерение expansion.
- accounts-payable-agent: https://ezatlas.com/atla-source-to-pay/invoice_and_ap_automation/ — AP-automation 2026: OCR, three-way matching, workflow-аппрувы, ERP-интеграция, очистка исключений.
- ad-creative-strategist: https://multiply.co/insights/everyone-has-the-same-ai-the-only-edge-is-the-brief — 2026: генеративный AI стал базой, преимущество — в брифе и человеческом суждении, не в инструменте.
- aeo-foundations: https://www.voctos.com/blog/ask-engine-optimization/ — AEO 2026: что ведёт к цитированию ответными движками, смещение источников 40–60% в месяц.
- agentic-identity-trust: https://mytecharm.com.co/post/agent-identity-is-solved-agent-trust-is-not-nmhx6k — 2026: W3C DID/Ed25519 решают identity, но не trust; нужен Zero Trust и governance для агентов.
- agentic-search-optimizer: https://www.quattr.com/blog/agentic-search-optimization — Agentic Search Optimization 2026: GEO/AEO/LLM SEO, попадание в ответы ChatGPT/Gemini/Perplexity, а не в SERP.
- agents-orchestrator: https://niteagent.com/blog/multi-agent-production-2026/ — 2026: из паттернов оркестрации в проде выживают единицы (peer-коллаборация падает при росте нагрузки), Plan-and-Execute.
- ai-citation-strategist: https://www.onvoyage.ai/blog/ai-citation-benchmarks-2026 — AI Citation Benchmarks 2026: модели цитируют бренды по-разному, дрейф источников 40–60% в месяц.
- ai-data-remediation-engineer: https://www.elixirdata.co/blog/governed-data-quality-remediation-ai-agents — 2026: governed remediation через Decision Boundaries, runtime authority и audit-ready evidence; DQ-инструменты профилируют/мониторят/ремедиируют.
- ai-engineer: https://internet-pros.com/blog/ai-evals-llm-evaluation-testing-2026/ — AI Evaluation 2026 стала ядром дисциплины: eval до имплементации, LLM-as-judge, CI gate, agentic RAG.
- ai-generated-code-security-auditor: https://shortspan.ai/prompts-drive-clustered-flaws-in-llm-generated-code.html — 2026: уязвимости LLM-кода кластеризуются по промпту, аудит группами; OWASP 2025/CWE Top 25/MITRE ATT&CK.
- analytics-reporter: https://www.knowi.com/blog/what-is-a-semantic-layer/ — 2026: семантический слой = единый источник доверенных метрик для BI и AI-агентов; sentiment delta вместо бинарного тональности.
- anthropologist: https://researchmethod.net/digital-ethnography/ — Digital/Computational Ethnography 2026: participant-led mobile ethnography, вычислительные методы, прозрачность и воспроизводимость.
- corporate-training-designer: https://flearningstudio.com/corporate-training-best-practices/ — microlearning как приоритет для поведенческих навыков; AI-видео как ускоритель; навыковые пути «Skills>Degrees»; измеримый ROI.
- cross-border-ecommerce: https://zigpoll.com/content/building-effective-crossborder-ecommerce-strategy-2026/ — data-driven локализация онбординга под регион; выбор маркетплейсов по unit-экономике; рост recommerce/ESG.
- customer-service: https://www.tradesly.ai/blog/ai-damaging-home-service-customers-how-to-fix — гибридная модель AI+человек (AI — квалификация/первая линия, человек — эмпатия/решения); приоритет защиты PII.
- customer-success-manager: https://churnlens.site/benchmarks/saas-net-revenue-retention/ — бенчмарки NRR/GRR (медиана B2B SaaS NRR ≈101–102%); AI для предиктивного оттока и QBR.
- data-consolidation-agent: https://kanerika.com/blogs/data-consolidation/ — ETL/ELT vs in-memory; MDM и унификация схем; data lineage; платформы (DOMO, ScienceSoft).
- data-engineer: https://thunderbit.com/de/blog/effective-data-collection-strategies — AI-ассистированная инженерия данных; инкрементальные загрузки; фин-опс для data-облака.
- data-privacy-officer: https://www.iubenda.com/en/blog/openai-gdpr-compliance/ — EU AI Act как новый слой; GDPR-комплаенс AI-голосовых агентов/LLM (data residency, согласие, минимизация).
- data-visualization-engineer: https://www.beautiful.ai/blog/data-visualization-trends-for-presentations-in-2026 — AI-инструменты (конверсационные запросы, автоинсайты); real-time аналитика и сторителлинг; governance.
- database-optimizer: https://sqlyard.com/2026/03/18/the-complete-sql-server-performance-tuning-checklist-2026/ — AI для SQL-оптимизации; DBA Health Check Toolkit; wait statistics; instance-level конфиг.
- database-reliability-engineer: https://observability.com/resource/the-sre-report-2026/ — observability как контрольная плоскость надёжности; AIOps для БД (аномалии, прогноз ёмкости).
- deal-strategist: https://salesgtm.ai/blogs/2026-guide-to-meddicc-with-ai-copilots-founder-led-sales — AI-copilots для MEDDICC (real-time данные, прогноз исхода); scorecard-квалификация.
- desktop-app-engineer: https://tauri.app/ — Tauri v2 как дефолт вместо Electron (~3-5 МБ бандл, -96% размер, -50% RAM, mobile-таргеты, усиленный IPC).
- devops-automator: https://talent500.com/blog/evolution-of-devops-future-trends-gitops-ai-devsecops/ — GitOps (ArgoCD/Flux, Git как источник истины); DevSecOps и AI-автомация.
- discovery-coach: https://www.meetrep.ai/blog/mastering-sales-discovery-questions-the-2026-playbook-backed-by-data — data-backed фреймворк (11–14 вопросов на базе 519K+ звонков, talk-ratio ~40/60); AI-анализ транскриптов.
- document-generator: https://artificio.ai/blog/document-ai-trends-2026-from-ocr-to-agentic-processing — agentic Document AI (OCR/multi-modal→LLM→валидация→сборка); compliance-first; real-time оркестрация workflow.

Обновлено: 2026-08-12 (доп. пакет 15 агентов)
