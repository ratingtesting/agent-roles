# Thematic Clusters & Warming Chains — Methodology + Worked Example

This reference expands Phase 0.2 of the JTBD Article Writer role. It covers: how to turn a query core into thematic clusters, how each cluster becomes a 5-article warming chain, and a worked real-estate example. Theme-agnostic — swap the domain and the method holds.

---

## 1. From Query Core to Thematic Clusters

**Input:** a classified query core (each phrase tagged with funnel stage and a coarse cluster/category from the cleaning stage).

**Goal:** group the core into ~20 parent themes ("clusters"). Each cluster is a self-contained topic the reader could journey through from awareness to decision.

### Method
1. **Group by intent, not by keyword.** "снять квартиру без посредников" and "аренда квартиры напрямую от собственника" are one cluster (rent-direct), even though wording differs. Read the phrase, decide the job behind it.
2. **One cluster = one journey.** If a group can't support all 5 CJM stages (awareness → decision), it's a sub-topic, not a cluster — merge it up.
3. **Target ~20 clusters.** Fewer than 15 = too broad (each cluster bloated). More than 30 = fragmentation (chains overlap, cross-links tangle). 20 is the working sweet spot for one domain.
4. **Name each cluster by the parent theme**, not a single keyword: "Покупка вторички", "Аренда без посредников", "Проверка юридической чистоты" — not "квартира".
5. **Assign a business role per cluster.** Mark whether the cluster's BOFU leads to a self-service guide or to a done-for-you service inquiry. This decides the CTA of articles #4–#5.

### Scaling note (owner/orchestrator decision, NOT the writer's)
How many clusters and how deep to go (20 clusters × 5 = 100 articles, or split each into sub-clusters for more) is a **content-plan decision made upstream** — by the project owner or orchestrator, not by the article writer. The writer's unit of work is ONE chain done well. Do not bake article-count targets into the writing role; pass the target as an input.

---

## 2. Cluster → 5-Article Warming Chain

Each cluster maps to exactly one chain of 5 articles, one per CJM stage (see SKILL.md §0.2.1–0.2.2). Fixed distribution: **1 TOFU → 2 MOFU → 2 BOFU**.

Per cluster, produce a chain spec:
- **Cluster name** + parent query (1–2 core keywords)
- **Business role** (self-service guide vs service inquiry) → sets #4–#5 CTA
- **5 articles**, each with: working title, CJM stage, funnel, 3–5 SEO queries, 1–2 line description, which article it links to next
- **Cross-link map**: 1→2→3→4→5 forward teasers + backward references

---

## 3. Worked Example — Real Estate (Moscow realtor)

**Domain:** private realtor, Moscow + MO. Business goal: inquiries in Telegram for consultation / transaction support (сопровождение сделки).

### Example cluster: "Покупка квартиры на вторичном рынке"
- **Parent query:** купить квартиру вторичка москва
- **Business role:** service inquiry (soprov_kupit) — BOFU leads to "сопровождение покупки под ключ"

| # | Working title (draft) | CJM | Funnel | SEO queries | Links to |
|---|----------------------|-----|--------|-------------|----------|
| 1 | Вторичка в Москве: с чего начать поиск квартиры и на что смотреть | S1 | TOFU | купить вторичку москва, вторичное жильё москва, квартира вторичка | → #2 |
| 2 | Почему покупка вторички срывается: скрытые риски, о которых молчат | S2 | MOFU | риски покупки вторички, проблемы вторичного жилья, обременение квартиры | → #3 |
| 3 | Как проверить квартиру на вторичке: 5 способов от самостоятельного до эксперта | S3 | MOFU | проверить квартиру перед покупкой, юридическая чистота квартиры, проверка собственника | → #4 |
| 4 | Проверить самому или с риелтором: честное сравнение для покупателя вторички | S4 | BOFU | риелтор для покупки вторички, сопровождение сделки купли-продажи, помощь при покупке квартиры | → #5 |
| 5 | Как купить вторичку в Москве безопасно: пошаговый план и сопровождение сделки | S5 | BOFU | купить квартиру под ключ, сопровождение покупки квартиры москва, безопасная сделка | CTA → TG |

### How the chain reads as one story
- **#1 (S1 Awareness):** reader just started thinking about buying. Article frames the market, dispels myths ("вторичка = всегда риск"), gives first steps. Ends: "Но даже подготовленные покупатели теряют деньги на скрытых рисках — разберём их в следующей части →"
- **#2 (S2 Problem):** deepens fear of hidden risks (обременения, прописанные, долги). Cost of inaction = потеря денег/сделки. Ends: "Хорошая новость — эти риски проверяемы. Разберём способы →"
- **#3 (S3 Solutions):** lays out 5 ways to verify (сам через ЕГРН, юрист, риелтор, …), pros/cons, who each fits. Ends: "Самому или доверить эксперту? Сравним честно →"
- **#4 (S4 Comparison):** honest comparison self-check vs realtor support, criteria table, cases. Positions our сопровождение as best fit for high-stakes deals. Ends: "Решились на сопровождение? Вот пошаговый план →"
- **#5 (S5 Decision):** checklist, last objections ("а вдруг риелтор не нужен"), why clients choose us, 2–3 real cases with outcomes, then the CTA — заявка в Telegram на консультацию/сопровождение.

### Applying to another domain
Swap the parent theme and the queries; the CJM stages, the 1-TOFU-2-MOFU-2-BOFU split, the "story that teases forward" mechanic, and the self-vs-service BOFU positioning stay identical. A medicine cluster ("подготовка к операции"), a styling cluster ("собрать капсульный гардероб"), a legal cluster ("банкротство физлица") all fit the same skeleton — only the domain trust signals (§A4 in SKILL.md) change.

---

## 4. Anti-Template Guarantee (across the batch)
When generating many chains, the biggest failure mode is 20 clusters that all open the same way. Enforce:
- Rotate H1 patterns (question / stat / scenario / myth) across clusters.
- Vary section counts per article (don't lock every S3 to exactly "Топ-5").
- Alternate example types (case / quote / data / checklist).
- Measure **tail/opening uniqueness across the whole batch**, not just within one article. Formal 100% line-uniqueness can still hide identical structures — check structural variety too.
