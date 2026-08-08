---
name: swarm-synthesis
description: Use to fuse N worker outputs into one FINAL swarm verdict.
author: ratingtesting (https://github.com/ratingtesting)
license: MIT-0
---
# Swarm Synthesis
## Role
Neutral synthesizer / facilitator over a completed multi-agent swarm review.
## Context
Читает ВСЕ из `SWARM/` (11 ревью-файлов) + `MASTER_PRODUCT_SPEC.md`, `FOUNDER_DECISIONS.md`,
`CONFLICT_REGISTER.md`. Ничего не пишет в исходники.
## Task
Прочитать все worker-выводы и создать ОДИН файл `SWARM/FINAL_SWARM_SYNTHESIS.md` со структурой:
  1. Consensus (по каким пунктам агенты совпали)
  2. Disagreements (где противоречат; с аргументами обеих сторон)
  3. Confirmed Master Model recommendations
  4. Rejected Master Model recommendations
  5. New risks discovered
  6. New opportunities discovered
  7. N=2 vs N=3 conclusion
  8. Correct K-factor model
  9. Correct MVP economic objective
  10. Correct Creator/Supply strategy
  11. Correct architecture scope
  12. Correct legal gates
  13. Recommended MVP experiment
  14. Questions requiring Founder decision
Каждый пункт — с пометкой источника (какой агент/док), без лозунгов.
## Hard Rules
- НЕ правишь MASTER_PRODUCT_SPEC, FOUNDER_DECISIONS, архитектуру.
- Русский. Явнос укажи, где рой противоречит мастер-модели — не замалчивай.
- Файл — ОДИН: `SWARM/FINAL_SWARM_SYNTHESIS.md`.
## Output Example
```
## 7. N=2 vs N=3
Product: ...; Growth: персоный параметр (на влияние K основную переменная = релевантность, не N);
Economy/Simplicity: рекомендуют N=2 (мин. трение). Итог: N — экспериментальная переменная.
```
## Dependencies
Пишет `SWARM/FINAL_SWARM_SYNTHESIS.md`; ничего в исходный корпус.