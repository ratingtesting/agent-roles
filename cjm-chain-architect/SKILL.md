---
name: cjm-chain-architect
emoji: "🧭"
color: "purple"
description: Design CJM lead-magnet content funnels — 5-stage customer journey maps and converging 3-5 node article paths from a keyword corpus to a lead magnet, with a stage-arithmetic gate before building.
version: 0.2.0
author: Петр (ratingtesting), Hermes Agent
license: MIT-0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cjm, customer-journey-map, lead-magnet, content-funnel, nurture, tofunnel]
    related_skills: [jtbd-article-writer, jtbd-editor, seo-content-writer, agent-defense]
---

# CJM Chain Architect (Карта пути клиента → сходящиеся графы контента)

Senior CJM architect who turns a **keyword/SERP corpus + funnel categories** into a **Customer Journey Map (CJM)** and a set of **converging article paths (depth 3–5)** that warm a reader to a lead magnet (e.g. a gated guide) and drive the final CTA (e.g. Telegram lead capture).

**Core philosophy (неизменно):**
- **CJM-first, not keyword-first.** Start from the customer's job-to-be-done (JTBD) at each stage, not from a keyword list. A CJM matrix (stages × dimensions) is the backbone; articles *fill* it.
- **One path = one audience = one lead magnet.** No "average" CJM that serves no one.
- **No invented phrases.** Every `source_phrase` must exist in the corpus — 0 exceptions.
- **Every article transitions.** No dead ends; the last CTA → lead magnet / channel.
- **Re-auditable:** KPI per stage, last-audited date, % corpus covered.

---

## When to Use
- Designing a Customer Journey Map for one audience segment + product/lead magnet.
- Planning blog/SEO articles that nurture a reader toward a lead magnet.
- Converting a classified corpus (funnel_v2 + category_9 + subcluster) into a content graph.
- **Don't use for:** writing the articles (`jtbd-article-writer`), editing titles (`jtbd-editor`), or raw keyword research.

---

## PHASE 0 — INPUTS, SCOPE & ARITHMETIC GATE

### 0.1 — Required inputs
| Input | What to ask for |
|---|---|
| **Corpus** | Classified keyword list with **funnel_v2**, **category_9**, **count**, and (optionally) `cluster_20`, `subcluster`, `magnet`, `jtbd_title`. See §0.5 for the exact contract. |
| **Lead magnet** | The end-product the path drives to. 1 magnet = 1 audience = 1 CJM. |
| **CTA target** | Final conversion action (Telegram channel / paywall URL). |
| **Audience segment** | One persona — never "all customers". Multiple segments = multiple CJMs. |

Missing inputs → ask before building. A CJM on assumptions is a *hypothesis*, not a CJM.

### 0.2 — Scope: a converging graph, not a fixed 5-article list

> **Change in 0.2.0:** the chain is no longer a fixed `TOFU→MOFU→MOFU→BOFU→BOFU` list. It is a **directed graph of nodes with `depth` 3–5 that converges** toward the magnet. The **5 CJM stages stay as stage labels** on nodes, not as an article count.

Rules:
- **depth** = length of the longest route from an entry node to a leaf (3–5). `depth` is a property of the graph, and each node also carries its own `depth` (its position from entry).
- **Convergence** = several branches may share downstream nodes. Shared nodes are the point: one strong Decision article can serve 5 Comparison articles.
- **Stage sequence is preserved on every path**: every path walks the stages in order (Awareness → Problem → Solutions → Comparison → Decision), but a path may **skip** intermediate stages when the corpus is thin — a 3-node path may go Awareness → Comparison → Decision. A path may **never** go backwards or skip Decision (every path terminates at the magnet).
- A cluster with enough volume stands alone as its own graph. A thin cluster (<100 phrases) is merged into the nearest graph.
- Node count per path is driven by corpus supply (Phase 0.3), not by a template.

### 0.3 — PHASE 0.3: GATE «арифметика стадий» (mandatory, run BEFORE building)

Count supply and demand **per audience (magnet) and per stage**, then decide. If the corpus cannot supply the stages a graph needs, **STOP and report** — do not invent, do not stretch one stage's phrases to cover another.

**Supply** = count of corpus rows for the audience, grouped by `funnel_v2` and `category_9`.
**Demand** = nodes required by the graph you intend to build:
```
demand(stage) = number of graph nodes labelled with that stage
                = (entry nodes) + (mid nodes) + (leaves)   [leaves = Decision]
```
Because paths converge, **the scarcest stage constrains the whole graph**: leaves (Decision) are the scarce resource, and the entry stage must be the widest.

Gate verdicts:
| Condition | Verdict | Action |
|---|---|---|
| Every stage of every intended path has supply ≥ demand | **GREEN** | build the graph |
| Any stage supply < demand | **RED — deficit** | **STOP.** Report the deficit per stage. Do not build. |
| Any path's terminal stage has supply = 0 | **RED — no exit** | **STOP.** A path with no Decision node cannot terminate at the magnet. |
| Audience has rows but `magnet`/audience label unset on >50% of candidate rows | **RED — unassigned** | **STOP.** Assign audiences first (this is a corpus-contract problem, not a graph problem). |

**Gate output is mandatory and machine-readable** — record it in `SUMMARY.md` and in the JSON (`gate` block) so a later run can reproduce the decision:
```
supply_TOFU / supply_MOFU / supply_BOFU, demand_* , verdict GREEN|RED, deficits[], stopped: true|false
```

> **Why this gate exists (0.2.0):** the funnel is not uniformly populated. In a real corpus MOFU can be *half* the size of TOFU, and the tightest audience can be an order of magnitude smaller than the largest. A fixed 5-article template then silently forces either duplicated nodes or stage-crossing. The gate makes the deficit visible **before** the graph is drawn.

### 0.4 — Audience map
Map `category_9` → magnet. **`category_9` is immutable** — it is the commercial intent label from the corpus and is never rewritten by this skill. Where the audience map is 1:many (several categories feed one magnet), record the mapping; where a category has **no** audience, it is `info` by default and must be declared in `SUMMARY.md`.

### 0.5 — Corpus contract (authoritative, 0.2.0)

The canonical corpus file is **`funnel_v3_ALL.csv`**, `;`-delimited, UTF-8 BOM, one header row:

| Column | Use |
|---|---|
| `phrase` | the search phrase — **the unit of work**; must exist verbatim |
| `category_9` | commercial intent — **immutable**, input to the audience map |
| `funnel_v2` | **the only** funnel column to read (TOFU / MOFU / BOFU) |
| `signal` | the surface signal that produced the stage |
| `confidence` | classifier confidence; low confidence → route to `review` |
| `garbage` | `core` = usable; anything else = **excluded from the graph** |
| `garbage_type`, `reason` | exclusion diagnostics (used for the dropped list) |
| `count` | search volume — used for node priority, never for stage |
| `cluster_20` | legacy broad cluster |
| `jtbd_title` | pre-assigned JTBD title — **input as-is**, see §0.6 |
| `subcluster` | finer grouping; preferred cluster key for graph building |
| `magnet` | audience label; **empty ⇒ audience unassigned** (gate RED) |
| `has_stages` | optional hint, informational only |

**Contract rules:**
- **`title_eligibility` is REMOVED** — do not reference it, do not filter on it. Use `garbage == "core"`.
- Use `garbage`, `confidence`, `review`. A row with `confidence` below the corpus median, or explicitly marked for review, is **not silently dropped** — it lands in the dropped list with a reason.
- **The legacy `funnel` column is IGNORED.** Some corpus files carry both `funnel` (old, coarse) and `funnel_v2` (current). Read `funnel_v2` only. Never merge or reconcile the two.
- **`funnel_v2` is never modified** — it is an input, not a work field.
- **`cjm_stage` is stored separately** (in the graph/registry), never written back into the corpus.

### 0.6 — Titles
- **Do not invent titles.** `source_phrase` and `jtbd_title` are taken from the corpus as-is.
- **Tail edits happen only after the graph is built, and only for articles that will actually be written.** A node with `publish=false` or `status=RESERVED` is never tail-edited — there is no article to write yet.
- Every title records **`tail_source`**: `corpus` (taken verbatim from `jtbd_title`), `tail_matrix` (phrase + a tail chosen from the pre-generated tail matrix), or `none`.
- If a node has no usable title, that is a **gate finding**, not a licence to write one.

---

## PHASE 1 — CJM CORE (5 stages × dimensions)

### 1.1 — The 5 CJM stages (labels for graph nodes)
| Stage | Customer state | Node role |
|---|---|---|
| **1. Awareness (TOFU)** | "I have a problem, I'm exploring." | Broad educational content matching a high-volume entry node. |
| **2. Problem recognition (MOFU)** | "I now see the specifics of my risk." | Deepens the problem; builds credibility. |
| **3. Solutions (MOFU)** | "What are the ways to solve this?" | Surveys solution types; positions your approach. |
| **4. Comparison (BOFU)** | "Do I do this myself or buy help?" | The **only** branch point. |
| **5. Decision (BOFU)** | "I'm ready — show me the plan + where to buy." | Terminal node; CTA to magnet / channel. |

A node's `cjm_stage` is a **label**. The same stage may appear on many nodes; a stage may have zero nodes on a short path. Stages are never renumbered to fit article count.

### 1.2 — CJM Dimensions (rows of the matrix)
For each of the 5 stages fill (see `references/cjm-matrix-template.md`):
**Thought · Emotion (−5..+5) · Objection/barrier · Information sought · Touchpoints · Transition trigger · KPI · Opportunity (optional)**.

**A cell with no real customer quote and no real metric is a `hypothesis`.** Mark it as such in the matrix (⚠) and list it in the validation backlog — an unmarked guess is a defect. See the template for the exact notation and the optional "awareness level" row.

---

## PHASE 2 — GRAPH DESIGN

For each node, produce:
1. **`cjm_stage`** (from Phase 1) and **`depth`** (position from entry).
2. **`route`** — `guide` or `service` (see §2.1). Immutable per node.
3. **`category_9`** — carried from the corpus, unchanged.
4. **JTBD** — the job the reader hires this node for.
5. **`source_phrase`** — real corpus row; **`jtbd_title`** as-is; **`tail_source`**.
6. **`seo_keys`** — real phrases from the same `subcluster`.
7. **1–2 sentence** `about`.
8. **`next_ref`** / **`branch_refs`** per §2.2.
9. **CTA** via the CTA module (§2.3).

### 2.1 — `route` and service-only paths
- **`route: "guide"`** — the reader hires a **product** (self-service guide / playbook).
- **`route: "service"`** — the reader hires **assistance** (realtor accompaniment, done-with-you).
- **Service-only paths are legitimate graphs**: a path may consist entirely of `route:"service"` nodes (for an audience whose product is assistance, not a guide). A service-only path still terminates at the magnet/CTA.
- `route` is decided by the audience map and the corpus `category_9`; it is never inferred from the title.

### 2.2 — Branching: exactly one fork, at Comparison
- **Exactly ONE node per graph carries `branch_point: true`**, and it is the **Comparison** node.
- That node has **two exits** in `branch_refs`: `main` (→ guide path / magnet) and `service` (→ service path).
- **Every other node has exactly one `next_ref`** (or, for a leaf, a `magnet` CTA target). Single-exit rule is absolute — no node outside Comparison may have two refs.
- The fork is expressed **in the CTA module**, not in prose (see §2.3). The body text of the Comparison node must not hand-pick a branch for the reader.

### 2.3 — CTA module and the reserved branch
The Comparison node renders a **CTA module** with two blocks (guide CTA / service CTA). A block renders **only if its target satisfies `target.publish == true`**.

**Reserved service branch:**
- Reserved service nodes carry `status: "RESERVED"`, `publish: false`, `service_enabled: false`.
- **No stub/placeholder pages are created** for reserved nodes. They exist in the graph and registry only.
- **Link rule (hard):** a link to any node is rendered only when that node has `publish=true`. A reserved target is never linked from anywhere; the CTA block for it is simply not rendered.
  - **Precise scope of the rule:** it applies to **`next_ref`** (the linear path) — a `next_ref` must never point at a `publish=false` node. The **single** `branch_refs` of the Comparison node **may** name a reserved service node: that is the mechanism by which the graph reserves the service branch before the service exists. The renderer then suppresses the block. The graph record is not a rendered link.
  - Practical check: a `next_ref` pointing to `publish=false` is a **defect**; a `branch_refs` entry pointing to `publish=false` with `cta_module.blocks[*].publish_required=true` is **correct**.
- This lets the whole graph be designed and reviewed while the service is not yet sellable, without publishing dead pages and without the copy implying an offer that doesn't exist.

### 2.4 — Reproducibility check (mandatory)
Before declaring the graph "done":
- Every `source_phrase` **exists in the corpus** (0 invented).
- Every node's stage label is consistent with its `funnel_v2` (Awareness↔TOFU, Problem/Solutions↔MOFU, Comparison/Decision↔BOFU).
- Exactly one `branch_point`, on a Comparison node, with both `main` and `service` refs.
- Every non-Comparison, non-leaf node has exactly one `next_ref`; every leaf resolves to the magnet CTA.
- No link targets a node with `publish=false`.
- CJM matrix has a KPI per stage and flags every `hypothesis` cell.
- Output is **machine-readable JSON** (`references/chain-template.md`) + `SUMMARY.md` with the Phase 0.3 gate result and corpus coverage.

---

## PHASE 3 — OUTPUT ARTIFACTS

Folder `11_cjm_chains/` (or project equivalent):
- `cjm_<magnet>.md` — CJM matrix (5 stages × dimensions, ⚠ on hypotheses).
- `chains_<magnet>.json` — the graph: nodes, `path_id`, `depth`, `route`, `cta_target`, `publish`, `service_enabled`, the single branch point, and the `gate` block.
- `articles_registry.csv` — flat registry: `article_id;path_id;depth;route;category_9;funnel_v2;cjm_stage;branch;branch_point;cta_target;status;publish;service_enabled;title;tail_source;source_phrase;subcluster`.
- `SUMMARY.md` — Phase 0.3 gate table, magnet → #paths → #nodes → phrases covered → % corpus, and the **dropped list** (phrase, reason).

> **Re-use across topics:** structure (stages, converging graph, one fork, CTA module, JSON schema, gate) is topic-agnostic. To switch topic, replace the audience map, corpus path, and CTA channel.

### 3.1 — SAMPLE artifact
The skill ships with a **SAMPLE** graph built by a script from real corpus rows. Rules:
- The old hand-written sample is **removed**, not kept alongside.
- The sample is generated by `scripts/build_sample_graph.py`, which **verifies per row that `phrase` exists in the corpus and that the stage label equals `funnel_v2`**; any row failing verification is dropped with a reason.
- Outputs are named `*_SAMPLE.*` and the JSON carries `"sample": true`.

---

## PHASE 4 — VERIFICATION & RE-AUDIT
- **Re-audit every 6 months** (CJMs go stale). Mark the last-audited date.
- Kill the 2 classic mistakes: **average CJM** (one map for 2+ personas → split) and **decorative CJM** (no KPI → not a CJM).
- Measure: stage drop-off (node 1 → node 2 rate), branch selection rate at the fork, time-to-conversion on the CTA, magnet → paid conversion.

---

## Hard Rules
- **CJM first, keyword second.**
- **One graph = one audience = one lead magnet.**
- **No invented phrases or titles.** Every `source_phrase` is a corpus row; `tail_source` records where any title polish came from.
- **Exactly one fork per graph, at Comparison; one exit everywhere else.**
- **Never link a node with `publish=false`.** Reserved service nodes get no pages.
- **Stage arithmetic first (Phase 0.3).** A deficit stops the build; it is reported, not patched.
- **`category_9` and `funnel_v2` are read-only.** `cjm_stage` lives in the graph.
- **Re-auditable:** KPI per stage, last-audited date, % corpus covered.

## Quality Gates (run before "done")
1. All `source_phrase`s exist in the corpus (0 invented); every node's `cjm_stage` agrees with its `funnel_v2`.
2. **Phase 0.3 gate recorded with verdict; no RED deficit left unbuilt.**
3. Exactly one `branch_point: true` per graph, on Comparison, with `main` + `service` in `branch_refs`.
4. Every non-Comparison non-leaf node has exactly one `next_ref`; every leaf resolves to the magnet CTA.
5. No rendered link targets a node with `publish=false`; reserved service nodes have `status=RESERVED`, `service_enabled=false`, and **no pages**.
6. CJM matrix has a KPI for each of the 5 stages and flags every `hypothesis` cell.
7. `SUMMARY.md` reports corpus coverage %, node count, and the dropped list with reasons.
8. Graph is valid JSON per `references/chain-template.md`; `title_eligibility` appears nowhere.

## Compatibility notes
- **0.1.0 → 0.2.0** (see `references/chain-template.md` §Back-compat): `n` → `depth` (position semantics preserved), `chain_id` → `path_id`; readers of 0.1.0 files must map these on read. `MAIGNET://` was a typo for the magnet target and is fixed. `branch: "soprov"` → `route: "service"`. `status: "PLANNED"` for service nodes → `RESERVED` + `publish:false`. `title_eligibility` removed in favour of `garbage`. `funnel` → `funnel_v2` (legacy column ignored). Old 5-article `chains_*.json` remain readable: fixed T-M-M-B-B lists are valid `depth 5` single-fork graphs.

## License & Sources
- **License:** MIT-0 (no attribution required, commercial use allowed).
- **Whitelist of source licenses:** MIT-0, MIT, Apache-2.0, ISC, Unlicense, 0BSD.
- **Excluded:** CC-BY*, GPL (all), Proprietary, anything requiring attribution/share-alike.
- **Clean-room:** methodology synthesized in our own words from the cited sources; no verbatim copying of third-party text/structure.
- **Sources (verified, read via web-guard on 20.09.2026):**
  - Signavio — *The Fundamentals of Customer Journey Mapping* — https://www.signavio.com/post/customer-journey-mapping/
  - smirnov.marketing — *Customer Journey Map: шаблон, этапы и пример CJM в 2026* — https://smirnov.marketing/blog/customer-journey-map-cjm-shablon
  - Semrush — *TOFu/MoFu/BoFu: A Practical Guide to the Conversion Funnel* — https://www.semrush.com/blog/tofu-mofu-bofu-a-practical-guide-to-the-conversion-funnel/
  - UpliftContent — *Lead Magnet Funnel: 6 Steps to Capture and Convert Prospects* — https://www.upliftcontent.com/blog/lead-magnet-funnel/
  - Local sample (in repo), regenerated 20.09.2026 by `scripts/build_sample_graph.py`: `wordstat-collector/11_cjm_chains/cjm_buyer_SAMPLE.md` + `chains_buyer_SAMPLE.json` + `articles_registry_SAMPLE.csv`
