# Chain JSON Schema v0.2.0 — сходящийся граф (converging graph)

Каждый магнит = 1 JSON-объект с массивом `paths` (путей). Путь — это **маршрут от входного узла к листу**, длиной **3–5** (`depth`). Ветки **сходятся**: разные пути могут вести к общим downstream-узлам. Схема фиксируется, чтобы `jtbd-article-writer` (этап 12) мог читать её и не выдумывать.

## Отличие от 0.1.0

В 0.1.0 цепочка была фиксированным списком из 5 статей (`n: 1..5`, последовательность T-M-M-B-B). В 0.2.0:
- узлы — **граф**, у каждого свой `depth` (позиция от входа), не сквозная нумерация пути;
- **длина пути 3–5**, она не фиксирована — определяется ресурсом корпуса (Phase 0.3);
- 5 этапов CJM — **метки стадий** (`cjm_stage`), а не число статей;
- пути **сходятся** (shared nodes), одна сильная Decision-статья может обслуживать несколько Comparison-статей.

## Поля узла

```json
{
  "article_id": "a_<magnet>_<n>",        // сквозной уникальный ID (registry + next_ref)
  "path_id": "path_<magnet>_<k>",        // к какому пути относится (0.1.0: chain_id)
  "depth": 1,                             // позиция узла от входа 1..5 (0.1.0: n)
  "route": "guide|service",               // НОВОЕ: читатель нанимает продукт (гайд) или помощь (услугу)
  "category_9": "self_kupit",             // НЕИЗМЕНЯЕМАЯ: из корпуса, не переписывается скиллом
  "funnel_v2": "TOFU|MOFU|BOFU",          // из корпуса, только для чтения
  "cjm_stage": "Awareness|Problem|Solutions|Comparison|Decision",  // хранится ОТДЕЛЬНО, в корпус не пишется
  "branch": "main|service|info",          // main=основная (к гайду), service=ветка услуги, info=вход
  "branch_point": false,                  // true РОВНО у одного узла в графе и только на Comparison
  "cta_target": "next|branch|magnet|channel",
  "cta_module": {                         // НОВОЕ: развилка рендерится модулем, не текстом
    "type": "next|dual|magnet",
    "blocks": [
      { "label": "guide",  "target": "<article_id|magnet://…>", "publish_required": true },
      { "label": "service","target": "<article_id>", "publish_required": true }
    ]
  },
  "status": "ACTIVE|PLANNED|DONE|RESERVED",
  "publish": true,                        // НОВОЕ: страница существует/будет опубликована
  "service_enabled": true,                // НОВОЕ: услуга доступна к покупке
  "title": "рабочий JTBD-заголовок (из корпуса, дословно)",
  "tail_source": "corpus|tail_matrix|none",  // НОВОЕ: откуда взят заголовок
  "source_phrase": "поисковая фраза, из корпуса (обязательно реальная)",
  "seo_keys": ["ключ1", "ключ2"],         // реальные фразы того же subcluster
  "about": "1–2 предложения: о чём статья",
  "next_ref": "article_id следующего узла | magnet://…",
  "branch_refs": { "main": "<article_id>", "service": "<article_id>" },
  "transition": "интригующий переход дальше по маршруту",
  "kpi": "метрика стадии (read-to-next / выбор ветки / конверсия в заявку)"
}
```

### Инварианты узла
1. `route` — `guide` или `service`, решается по карте аудиторий и `category_9`, **не выводится из заголовка**; неизменяем.
2. `category_9` и `funnel_v2` — **только чтение**, из корпуса.
3. `cjm_stage` хранится в графе/registry **отдельно** и никогда не пишется в корпус.
4. `branch_point: true` — **не более одного на граф**, только на стадии `Comparison`.
5. Все прочие узлы: **ровно один** `next_ref` (или `magnet://` у листа).
6. Ссылка на узел рендерится **только при `publish: true`** у цели.
7. Заголовок не сочиняется: `title` = `jtbd_title` из корпуса, а来源 правок фиксируется в `tail_source`.
8. Хвост правится **только после построения графа и только для публикуемых статей** (`publish: true`). Для `publish: false` / `status: RESERVED` — `tail_source: "none"`, хвост не трогаем.

## Резервная ветка услуги

```json
{ "article_id": "a_buyer_kvart_1_5s", "route": "service", "branch": "service",
  "status": "RESERVED", "publish": false, "service_enabled": false,
  "title": "", "tail_source": "none", "source_phrase": "", "seo_keys": [],
  "about": "Ветка сопровождения: узел зарезервирован, страница НЕ создаётся.",
  "next_ref": "service://launch", "kpi": "conversion to service inquiry (когда услуга включена)" }
```

- `status=RESERVED`, `publish=false`, `service_enabled=false`.
- **Заглушки/страницы не создаются** — узел живёт только в графе и registry.
- Блок CTA для этой цели **не рендерится**, пока `publish` не станет `true`.
- Развилка (выбор гайд/услуга) — через `cta_module`, **не через текст** в теле статьи.

## Полный файл `chains_<магнит>.json`

```json
{
  "sample": true,
  "magnet": "Гайд «Безопасная сделка»",
  "cta_channel": "Telegram @kvartirometr / paywall",
  "cluster": "kupit_kvartiru",
  "category_9": "self_kupit",
  "corpus": {
    "file": "funnel_v3_ALL.csv",
    "audience_filter": "magnet=buyer",
    "garbage_filter": "garbage=core",
    "stage_column": "funnel_v2",
    "legacy_funnel_ignored": true,
    "title_eligibility_used": false
  },
  "gate": {
    "phase": "0.3",
    "supply": { "TOFU": 0, "MOFU": 0, "BOFU": 0 },
    "demand": { "TOFU": 0, "MOFU": 0, "BOFU": 0 },
    "verdict": "GREEN|RED",
    "deficits": [],
    "stopped": false
  },
  "paths": [
    {
      "path_id": "path_buyer_kvart_1",
      "depth": 3,
      "stage_sequence": ["Awareness", "Comparison", "Decision"],
      "articles": [
        { "article_id": "a_buyer_kvart_1_1", "path_id": "path_buyer_kvart_1", "depth": 1,
          "route": "guide", "category_9": "self_kupit", "funnel_v2": "TOFU",
          "cjm_stage": "Awareness", "branch": "info", "branch_point": false,
          "cta_target": "next", "cta_module": { "type": "next", "blocks": [] },
          "status": "ACTIVE", "publish": true, "service_enabled": true,
          "title": "Купить квартиру в москве: Что будет с ценами в 2027",
          "tail_source": "tail_matrix",
          "source_phrase": "купить квартиру в москве",
          "seo_keys": ["купить квартиру в москве", "квартиры в москве"],
          "about": "Как устроен рынок вторички, из чего складывается цена, с чего начать поиск.",
          "next_ref": "a_buyer_kvart_1_2",
          "transition": "Вы нашли варианты. Но объявление ничего не гарантирует — дальше разберём риски.",
          "kpi": "CTR + read-to-next ≥ 40%" },
        { "article_id": "a_buyer_kvart_1_2", "path_id": "path_buyer_kvart_1", "depth": 2,
          "route": "guide", "category_9": "self_kupit", "funnel_v2": "BOFU",
          "cjm_stage": "Comparison", "branch": "main", "branch_point": true,
          "cta_target": "branch",
          "cta_module": { "type": "dual", "blocks": [
            { "label": "guide",   "target": "a_buyer_kvart_1_3",   "publish_required": true },
            { "label": "service", "target": "a_buyer_kvart_1_3s",  "publish_required": true } ] },
          "status": "ACTIVE", "publish": true, "service_enabled": true,
          "title": "Купить квартиру в москве недорого — самому или с риелтором",
          "tail_source": "corpus",
          "source_phrase": "купить квартиру в москве недорого",
          "seo_keys": ["купить квартиру недорого", "купить с риелтором"],
          "about": "Самостоятельная сделка vs сопровождение; цена ошибки vs цена услуги.",
          "next_ref": "a_buyer_kvart_1_3",
          "branch_refs": { "main": "a_buyer_kvart_1_3", "service": "a_buyer_kvart_1_3s" },
          "transition": "Кому-то нужен полный план, кому-то живой специалист — выбирайте блок ниже.",
          "kpi": "branch-selection rate (выбор ветки)" },
        { "article_id": "a_buyer_kvart_1_3", "path_id": "path_buyer_kvart_1", "depth": 3,
          "route": "guide", "category_9": "self_kupit", "funnel_v2": "BOFU",
          "cjm_stage": "Decision", "branch": "main", "branch_point": false,
          "cta_target": "magnet",
          "cta_module": { "type": "magnet", "blocks": [
            { "label": "guide", "target": "magnet://Безопасная сделка", "publish_required": false } ] },
          "status": "ACTIVE", "publish": true, "service_enabled": true,
          "title": "Купить однокомнатную квартиру в москве безопасно — пошаговый план",
          "tail_source": "corpus",
          "source_phrase": "купить однокомнатную квартиру в москве",
          "seo_keys": ["купить однокомнатную квартиру", "безопасная сделка"],
          "about": "Сводим всё в пошаговый план; прямой CTA на гайд + клуб.",
          "next_ref": "magnet://Безопасная сделка + TG @kvartirometr",
          "transition": "CTA: «Скачайте гайд и вступите в канал. Заявка: Telegram @kvartirometr.»",
          "kpi": "конверсия в заявку/оплату гайда" },
        { "article_id": "a_buyer_kvart_1_3s", "path_id": "path_buyer_kvart_1", "depth": 3,
          "route": "service", "category_9": "soprov_kupit", "funnel_v2": "BOFU",
          "cjm_stage": "Decision", "branch": "service", "branch_point": false,
          "cta_target": "branch", "status": "RESERVED", "publish": false, "service_enabled": false,
          "title": "", "tail_source": "none", "source_phrase": "", "seo_keys": [],
          "about": "Ветка сопровождения покупки: узел зарезервирован, страница не создаётся.",
          "next_ref": "service://launch",
          "kpi": "conversion to service inquiry (когда услуга включена)" }
      ]
    }
  ],
  "convergence": {
    "shared_nodes": ["a_buyer_decision_1"],
    "note": "Один Decision-узел обслуживает несколько Comparison-веток — ветки сходятся."
  },
  "dropped": [
    { "phrase": "…", "reason": "confidence below median" }
  ]
}
```

## Файл `articles_registry.csv`

Колонки:
```
article_id;path_id;depth;route;category_9;funnel_v2;cjm_stage;branch;branch_point;cta_target;status;publish;service_enabled;title;tail_source;source_phrase;subcluster
```

- `article_id` уникален и сквозной — по нему этап 12 (написание) и внутренние ссылки.
- Фильтр `branch=service` **И** `status=RESERVED` → заготовки под услугу (страниц нет).
- Фильтр `status=PLANNED|ACTIVE` → весь план до написания.
- Фильтр `publish=true` → только то, что реально публикуется и на что можно ссылаться.

## Файл `SUMMARY.md`

1. **Гейт Phase 0.3** — таблица `supply` / `demand` / `verdict` / `deficits` / `stopped`.
2. Таблица покрытия: `магнит → #путей → #узлов → фраз охвачено → % корпуса`.
3. **Список отброшенного** — `phrase;reason` (по `garbage`, `confidence`, `review`).

Покрытие = (использованные `source_phrase` в графе) / (фразы корпуса выборки аудитории, `garbage=core`).

## Quality Gates (перед «готово»)
1. Все `source_phrase` реально есть в корпусе (0 выдуманных); `cjm_stage` узла совпадает с его `funnel_v2` (Awareness↔TOFU, Problem/Solutions↔MOFU, Comparison/Decision↔BOFU).
2. Зафиксирован результат гейта Phase 0.3; RED-дефицит не остался незакрытым.
3. **Ровно один** `branch_point: true` на граф, на стадии Comparison, с `main` + `service` в `branch_refs`.
4. У каждого не-Comparison не-листового узла **ровно один** `next_ref`; каждый лист резолвится в CTA магнита.
5. **Ни одна ссылка не ведёт на узел с `publish=false`**; узлы-резервы имеют `status=RESERVED`, `service_enabled=false` и **не имеют страниц**.
6. Узлы-резервы имеют `tail_source="none"` — хвосты не правились.
7. CJM-карта имеет KPI по каждой из 5 стадий и помечает `hypothesis`-клетки.
8. `SUMMARY.md` содержит покрытие %, число узлов и список отброшенного с причинами.
9. JSON парсится и валиден по схеме выше; `title_eligibility` не упоминается.

## Back-compat (0.1.0 → 0.2.0)
Читатель старых файлов должен маппить поля при чтении:

| 0.1.0 | 0.2.0 | Что делать |
|---|---|---|
| `chain_id` | `path_id` | переименовать |
| `n` | `depth` | смысл тот же (позиция), но `depth` — свойство узла, а не сквозной номер пути |
| `branch: "soprov"` | `route: "service"` + `branch: "service"` | разнести: `route` = суть, `branch` = положение в графе |
| `status: "PLANNED"` (узел услуги) | `status: "RESERVED"`, `publish: false`, `service_enabled: false` | добавить флаги, страницу не создавать |
| `MAIGNET://` | `magnet://` | опечатка исправлена |
| `funnel` (легаси) | `funnel_v2` | читать только `funnel_v2`; `funnel` игнорировать |
| `title_eligibility` | `garbage == "core"` | удалено из контракта |
| фиксированный список T-M-M-B-B (`n: 1..5`) | граф, `depth` 3–5, одна развилка | старый список — это валидный граф одной ветки с `depth 5` |

Обратная совместимость: **старые `chains_*.json` (0.1.0) остаются валидными входными данными** — они читаются как граф с одной развилкой и глубиной 5; при пересохранении поля мапятся по таблице выше. Новые поля (`route`, `publish`, `service_enabled`, `tail_source`, `cta_module`, `gate`) в старых файлах отсутствуют и трактуются дефолтами: `route="guide"`, `publish=true`, `service_enabled=true`, `tail_source="corpus"`, `cta_module` выводится из `cta_target`.
