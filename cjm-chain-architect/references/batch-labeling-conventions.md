# Batch labeling conventions (Ф3, `f3_batches/` → `f3_out/`)

Per-row `cjm_stage` labeling follows `f3_SPEC.md`. This file records the
tie-break conventions that the spec leaves open, derived by inspecting 20
completed batches (4000 rows). Apply them so stages stay comparable across
batches — batch-to-batch drift in stage assignment is the main failure mode
of this pass.

## Stage by intent, not by keyword presence

| Signal in phrase | MOFU | BOFU |
|---|---|---|
| bare noun query, no verb (`стоимость 2 х квартиры`, `квартира ... до 5 млн`) | Solutions | — |
| bare noun + budget/area (`купить` absent) | Solutions 0.5–0.6 | — |
| concrete action verb + object/locale (`купить в ...`, `снять в ...`, `продать`) | — | Decision |
| transaction noun without verb (`продажа квартир ...`) | — | Decision 0.6–0.85 |
| portal/agency name + action (`циан купить`, `авито снять`, `пик купить`) | — | Decision — a named channel is still an action |
| action + portal in **MOFU** (`циан снять квартиру в москве`) | Solutions — reads as "a way to rent" | — |

## Recurring lexical triggers

- **`отзывы` (ЖК, дом, застройщик, рынок) → Problem**, conf 0.55–0.7. Reviews are
  the user checking for risk. Exception: `риэлторы/агенты ... отзывы` →
  Solutions (evaluating a performer, not an asset).
- **`стоимость` / `цена` / `калькулятор` / `как узнать стоимость` → Solutions** —
  it is a method for pricing, not a purchase.
- **`проблемы` in a ЖК/дом name → Problem**, conf 0.85.
- **`под снос` → Solutions** when the verb is absent (`дома под снос в МО`),
  **Decision** when present (`купить квартиру под снос`).
- **`обмен` → Decision** in BOFU, Solutions in MOFU (ways to structure a deal).
- **Paying a condition to the verb (`в рассрочку`, `без взноса`, `с пропиской`,
  `под ключ`) keeps the verb's stage.** In BOFU the condition is a Decision
  attribute; in MOFU the same words are Solutions (searching for a way).
- **Truncated / brand-only phrases** (`москва баня коттедж`, `квартирное бюро
  москва`, `жилье ру москва аренда`): cjm_conf **0.3–0.5** — do not claim 0.8+.

## `funnel_check` discipline

- `confidence >= 0.6` → always `"agree"`, `review: false`. Never override.
- `confidence < 0.6` → all three values are legitimate. `agree` at low
  confidence is **correct**, not an error: the field asks whether your stage
  reading is right, and a clear phrase can sit at low corpus confidence.
  Observed split across 21 batches: agree 61 / unsure 73 / disagree 55.
- Use `disagree` when the phrase text clearly implies a stage outside its
  `funnel_v2` (e.g. MOFU phrase containing a plain action verb). Use `unsure`
  when the phrase supports both stages or is too thin to call.
- `review` is derived, never authored: `review = funnel_check in (disagree, unsure)`.

## Validator gotcha

A checker that asserts `confidence < 0.6 ⇒ funnel_check != "agree"` will report
false failures. Validate these instead: count equality, phrase/funnel_v2
verbatim equality, stage ∈ allowed set, stage ∈ funnel's legal pair, and
`review == (funnel_check in (disagree, unsure))`.
