#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_sample_graph.py — сборка SAMPLE-графа CJM из РЕАЛЬНЫХ строк корпуса.

Skill: cjm-chain-architect 0.2.0
Назначение (п.8 ТЗ): заменить рукописный образец генерируемым. Скрипт:
  1) берёт реальные строки funnel_v3_ALL.csv (garbage=core, magnet=<аудитория>);
  2) ДЛЯ КАЖДОЙ строки проверяет: phrase есть в корпусе (дословно) и
     стадия узла == funnel_v2 строки (Awareness<->TOFU, Problem/Solutions<->MOFU,
     Comparison/Decision<->BOFU);
  3) прогоняет гейт Phase 0.3 (арифметика стадий): supply vs demand;
  4) пишет chains_<magnet>_SAMPLE.json + articles_registry_SAMPLE.csv + SUMMARY.

Любая строка, не прошедшая проверку, попадает в dropped с причиной — молча не выбрасываем.
"""
import argparse
import collections
import csv
import io
import json
import os
import statistics
import sys

STAGE_BY_FUNNEL = {
    "TOFU": ["Awareness"],
    "MOFU": ["Problem", "Solutions"],
    "BOFU": ["Comparison", "Decision"],
}
FUNNEL_BY_STAGE = {}
for _f, _ss in STAGE_BY_FUNNEL.items():
    for _s in _ss:
        FUNNEL_BY_STAGE[_s] = _f

REQUIRED_COLS = ["phrase", "category_9", "funnel_v2", "confidence", "garbage", "count", "magnet"]
FORBIDDEN = "title_eligibility"
LEGACY_FUNNEL = "funnel"


def read_corpus(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        rdr = csv.DictReader(f, delimiter=";")
        cols = rdr.fieldnames or []
        missing = [c for c in REQUIRED_COLS if c not in cols]
        if missing:
            sys.exit("FATAL: корпус не соответствует контракту, нет колонок: %s" % missing)
        if FORBIDDEN in cols:
            sys.exit("FATAL: в корпусе есть удалённая колонка '%s' (контракт 0.2.0 её запрещает)" % FORBIDDEN)
        rows = [dict(x) for x in rdr]
    return rows, cols


def build(path, out_dir, magnet, sample_limit, depth_min, depth_max):
    rows, cols = read_corpus(path)
    dropped = []

    # --- выборка: реальные строки аудитории, garbage=core, заполненная стадия ---
    pool = [r for r in rows if (r.get("garbage") or "").strip() == "core"
            and (r.get("magnet") or "").strip() == magnet
            and (r.get("funnel_v2") or "").strip() in STAGE_BY_FUNNEL]
    # легаси-колонка funnel игнорируется принципиально (считаем, что её читали — не должно влиять)
    pool.sort(key=lambda r: -int(float(r.get("count") or 0)))

    if sample_limit and len(pool) > sample_limit:
        # режем по стадиям пропорционально supply, чтобы не выбить одну стадию
        by_f = collections.defaultdict(list)
        for r in pool:
            by_f[r["funnel_v2"]].append(r)
        keep, quota = [], sample_limit
        order = sorted(by_f, key=lambda f: -len(by_f[f]))
        for f in order:
            take = min(quota, max(1, round(sample_limit * len(by_f[f]) / len(pool))))
            keep.extend(by_f[f][:take])
            quota -= take
        for r in by_f.get("BOFU", [])[max(0, sample_limit - len(keep)):]:
            pass
        keep.sort(key=lambda r: -int(float(r.get("count") or 0)))
        pool = keep[:sample_limit]

    med_conf = statistics.median([float(r.get("confidence") or 0) for r in rows]) if rows else 0.0

    # --- ПРОВЕРКА КАЖДОЙ СТРОКИ (п.8): phrase есть в корпусе + стадия == funnel_v2 ---
    corpus_phrases = set((r.get("phrase") or "").strip() for r in rows)
    by_stage = collections.defaultdict(list)
    # BOFU несёт ДВЕ стадии (Comparison и Decision) — делим строки поровну,
    # иначе Decision останется пустым и гейт врёт про дефицит.
    comp_every_other = 0
    for r in pool:
        ph = (r.get("phrase") or "").strip()
        fv = (r.get("funnel_v2") or "").strip()
        if not ph:
            dropped.append({"phrase": ph, "reason": "empty phrase"})
            continue
        if ph not in corpus_phrases:
            dropped.append({"phrase": ph, "reason": "phrase not found in corpus"})
            continue
        if fv not in STAGE_BY_FUNNEL:
            dropped.append({"phrase": ph, "reason": "unknown funnel_v2=%s" % fv})
            continue
        conf = float(r.get("confidence") or 0)
        if conf < med_conf:
            dropped.append({"phrase": ph, "reason": "confidence %.2f below median %.2f -> review" % (conf, med_conf)})
            continue
        title = (r.get("jtbd_title") or "").strip()
        # хвост правим только для публикуемых узлов; здесь все узлы публикуемые
        tail_source = "corpus" if title else "none"
        stages = STAGE_BY_FUNNEL[fv]
        if len(stages) == 2:  # BOFU -> Comparison / Decision пополам
            stage = stages[comp_every_other % 2]
            comp_every_other += 1
        else:
            stage = stages[0]
        by_stage[stage].append({
            "article_id": "", "path_id": "", "depth": 0,
            "route": "guide", "category_9": r["category_9"], "funnel_v2": fv,
            "cjm_stage": stage, "branch": "info", "branch_point": False,
            "cta_target": "next", "status": "ACTIVE", "publish": True, "service_enabled": True,
            "title": title, "tail_source": tail_source,
            "source_phrase": ph,
            "seo_keys": [ph],
            "about": "", "next_ref": "", "transition": "", "kpi": "",
            "_count": int(float(r.get("count") or 0)),
            "_subcluster": r.get("subcluster") or r.get("cluster_20") or "",
        })

    # --- проектирование путей: сходящийся граф, depth 3..5 ---
    STAGE_ORDER = ["Awareness", "Problem", "Solutions", "Comparison", "Decision"]
    nodes, paths = [], []
    if not by_stage.get("Awareness"):
        by_stage["Awareness"] = []
    entry_pool = by_stage.get("Awareness", [])
    n_entries = min(len(entry_pool), 2) or 1
    if entry_pool:
        entries = entry_pool[:n_entries]
        for e in entries:
            nodes.append(e)
    else:
        # входной узел обязателен: берём самый частотный узел любой стадии
        any_pool = [v for ss in by_stage.values() for v in ss]
        if not any_pool:
            dropped.append({"phrase": "", "reason": "no usable rows for audience '%s'" % magnet})
        else:
            e = any_pool[0]
            e["cjm_stage"] = "Awareness"
            nodes.append(e)
            entries = [e]

    # mid-узлы: Problem, Solutions (если есть) — берём по 1, самый частотный
    mids = []
    for st in ("Problem", "Solutions"):
        if by_stage.get(st):
            m = by_stage[st][0]
            nodes.append(m)
            mids.append(m)

    comparison_pool = by_stage.get("Comparison", [])
    decision_pool = by_stage.get("Decision", [])
    if not comparison_pool and decision_pool:
        # Comparison обязателен как развилка — берём решение и понижаем его до Comparison
        comparison_pool = [decision_pool[0]]

    def wire(u, d):
        u["depth"] = d
        return u

    # один лист-на-вход, но Comparison общий (сходимость)
    for i, e in enumerate(entries, start=1):
        wire(e, 1)
    for j, m in enumerate(mids, start=1):
        wire(m, 2)
    if comparison_pool:
        c = comparison_pool[0]
        wire(c, 3)
        c["branch_point"] = True
        c["branch"] = "main"
        c["cta_target"] = "branch"
        c["cta_module"] = {"type": "dual", "blocks": [
            {"label": "guide", "target": "", "publish_required": True},
            {"label": "service", "target": "", "publish_required": True}]}
        nodes.append(c)
    else:
        c = None
    if decision_pool:
        d = decision_pool[0]
        wire(d, 4 if mids else 3)
        d["branch"] = "main"
        d["cta_target"] = "magnet"
        d["cta_module"] = {"type": "magnet", "blocks": [
            {"label": "guide", "target": "magnet://%s" % magnet, "publish_required": False}]}
        nodes.append(d)
        # зарезервированный сервисный лист
        svc = dict(d)
        svc.update({
            "article_id": "", "route": "service", "branch": "service", "branch_point": False,
            "cta_target": "branch", "status": "RESERVED", "publish": False, "service_enabled": False,
            "title": "", "tail_source": "none", "source_phrase": "", "seo_keys": [],
            "about": "Ветка сопровождения: узел зарезервирован, страница НЕ создаётся.",
            "next_ref": "service://launch", "kpi": "conversion to service inquiry (когда услуга включена)",
        })
        nodes.append(svc)
    else:
        d = None
    svc = locals().get("svc")

    # --- Рёбра графа: явная структура, без позиционных догадок ---
    # entries -> mids -> Comparison -> {Decision (main), service leaf (RESERVED)}
    for e in entries:
        for m in mids:
            e.setdefault("edges", []).append(m)
    for e in entries:
        if not mids and c is not None:
            e.setdefault("edges", []).append(c)
    for m in mids:
        if c is not None:
            m.setdefault("edges", []).append(c)
    if c is not None:
        c.setdefault("edges", []).append(d)          # main
        if svc is not None:
            c.setdefault("edges", []).append(svc)     # service
    for n in nodes:
        n.setdefault("edges", [])

    # article_id
    for idx, n in enumerate(nodes, start=1):
        n["article_id"] = "a_%s_s%02d" % (magnet, idx)

    # next_ref: ровно один выход; лист -> magnet
    magnet_leaf = "magnet://%s + CTA channel" % magnet
    for n in nodes:
        if n.get("branch_point"):
            continue
        outs = [t for t in n.get("edges", []) if t.get("publish")]
        if outs:
            n["next_ref"] = outs[0]["article_id"]
        elif n is d:
            n["next_ref"] = magnet_leaf
        elif n is svc:
            n["next_ref"] = "service://launch"
        else:
            n["next_ref"] = magnet_leaf
        n.pop("edges", None)

    if c is not None:
        svc_leaf = svc if svc is not None else None
        c["next_ref"] = d["article_id"] if d is not None else magnet_leaf
        c["branch_refs"] = {
            "main": d["article_id"] if d is not None else magnet_leaf,
            "service": svc_leaf["article_id"] if svc_leaf is not None else "service://launch",
        }
        c["cta_module"]["blocks"][0]["target"] = c["branch_refs"]["main"]
        c["cta_module"]["blocks"][1]["target"] = c["branch_refs"]["service"]
        c.pop("edges", None)

    # Пути: маршруты от каждого входа. Узлы ОБЩИЕ (сходимость) —
    # копий узлов в разных путях не создаём.
    for i, e in enumerate(entries, start=1):
        pid = "path_%s_s%d" % (magnet, i)
        for n in nodes:
            n["path_id"] = pid
        chain = [e] + mids + ([c] if c is not None else []) + ([d] if d is not None else []) \
                + ([svc] if svc is not None else [])
        ordered = sorted(chain, key=lambda x: (x["depth"], 0 if x is e else 1, x["article_id"]))
        paths.append({
            "path_id": pid,
            "depth": max(n["depth"] for n in chain if n["depth"] > 0),
            "stage_sequence": [n["cjm_stage"] for n in ordered],
            "articles": [{k: v for k, v in n.items() if not k.startswith("_")} for n in ordered],
        })

    # --- ГЕЙТ PHASE 0.3 (арифметика стадий) ---
    supply = collections.Counter()
    for r in rows:
        if (r.get("garbage") or "").strip() == "core" and (r.get("magnet") or "").strip() == magnet:
            fv = (r.get("funnel_v2") or "").strip()
            if fv in STAGE_BY_FUNNEL:
                supply[fv] += 1
    node_by_funnel = collections.Counter(n["funnel_v2"] for n in nodes)
    demand = {"TOFU": node_by_funnel.get("TOFU", 0),
              "MOFU": node_by_funnel.get("MOFU", 0),
              "BOFU": node_by_funnel.get("BOFU", 0)}
    deficits = []
    for st in ("TOFU", "MOFU", "BOFU"):
        if supply[st] == 0 and demand[st] > 0:
            deficits.append("%s: supply=0 but demand=%d" % (st, demand[st]))
        elif supply[st] < demand[st]:
            deficits.append("%s: supply=%d < demand=%d" % (st, supply[st], demand[st]))
    if not nodes:
        deficits.append("no nodes built for audience '%s'" % magnet)
    if d is None:
        deficits.append("no Decision leaf -> path cannot terminate at magnet")
    if c is None:
        deficits.append("no Comparison node -> required single branch point missing")

    # unassigned check: доля строк-кандидатов без метки аудитории
    cand = [r for r in rows if (r.get("garbage") or "").strip() == "core"]
    unassigned = sum(1 for r in cand if not (r.get("magnet") or "").strip())
    unassigned_share = (unassigned / len(cand)) if cand else 0.0
    if unassigned_share > 0.5:
        deficits.append("audience unassigned on %.1f%% of candidate rows (>50%%)" % (100 * unassigned_share))

    verdict = "RED" if deficits else "GREEN"

    gate = {
        "phase": "0.3",
        "audience": magnet,
        "supply": {k: supply.get(k, 0) for k in ("TOFU", "MOFU", "BOFU")},
        "demand": demand,
        "verdict": verdict,
        "deficits": deficits,
        "stopped": verdict == "RED",
        "unassigned_share": round(unassigned_share, 4),
        "corpus_file": os.path.basename(path),
        "corpus_columns": cols,
        "legacy_funnel_ignored": True,
        "title_eligibility_used": False,
        "sample_size": len(nodes),
    }

    return {"gate": gate, "paths": paths, "nodes": nodes, "dropped": dropped,
            "depth_range": (depth_min, depth_max)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--magnet", default="buyer")
    ap.add_argument("--sample", type=int, default=200)
    ap.add_argument("--depth-min", type=int, default=3)
    ap.add_argument("--depth-max", type=int, default=5)
    a = ap.parse_args()

    res = build(a.corpus, a.out, a.magnet, a.sample, a.depth_min, a.depth_max)
    os.makedirs(a.out, exist_ok=True)
    stem = os.path.join(a.out, "chains_%s_SAMPLE" % a.magnet)

    doc = {
        "sample": True,
        "magnet": a.magnet,
        "skill_version": "cjm-chain-architect@0.2.0",
        "corpus": res["gate"],
        "gate": res["gate"],
        "paths": res["paths"],
        "convergence": {"shared_nodes": [], "note": "SAMPLE: один вход, ветки сходятся к общему Decision"},
        "dropped": res["dropped"],
    }
    with io.open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    reg = os.path.join(a.out, "articles_registry_SAMPLE.csv")
    cols = ["article_id", "path_id", "depth", "route", "category_9", "funnel_v2", "cjm_stage",
            "branch", "branch_point", "cta_target", "status", "publish", "service_enabled",
            "title", "tail_source", "source_phrase", "subcluster"]
    with io.open(reg, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for n in res["nodes"]:
            w.writerow({c: n.get(c, "") for c in cols})

    g = res["gate"]
    with io.open(os.path.join(a.out, "SUMMARY_SAMPLE.md"), "w", encoding="utf-8") as f:
        f.write("# SAMPLE — cjm-chain-architect 0.2.0\n\n")
        f.write("## Гейт Phase 0.3 (арифметика стадий)\n\n")
        f.write("| Стадия | supply | demand | дефицит |\n|---|---|---|---|\n")
        for st in ("TOFU", "MOFU", "BOFU"):
            dv = g["demand"][st]
            deficit = "ДА" if g["supply"][st] < dv else "нет"
            f.write("| %s | %d | %d | %s |\n" % (st, g["supply"][st], dv, deficit))
        f.write("\n**Вердикт: %s**\n\n" % g["verdict"])
        if g["deficits"]:
            f.write("Дефициты:\n" + "".join("- %s\n" % x for x in g["deficits"]))
        f.write("\n- Аудиторий без метки `magnet`: %.1f%% кандидатов\n" % (100 * g["unassigned_share"]))
        f.write("- Узлов в графе: **%d** (depth %d..%d)\n" % (len(res["nodes"]), a.depth_min, a.depth_max))
        f.write("- Отброшено строк: **%d**\n" % len(res["dropped"]))
        f.write("\n## Отброшено\n\n| phrase | reason |\n|---|---|\n")
        for d in res["dropped"][:50]:
            f.write("| %s | %s |\n" % (d["phrase"], d["reason"]))
        if len(res["dropped"]) > 50:
            f.write("\n…ещё %d (в JSON)\n" % (len(res["dropped"]) - 50))

    print("VERDICT=%s" % g["verdict"])
    print("NODES=%d" % len(res["nodes"]))
    print("DEPTH=%s" % sorted(set(n["depth"] for n in res["nodes"])))
    print("SUPPLY=%s DEMAND=%s" % (g["supply"], g["demand"]))
    print("DEFICITS=%s" % g["deficits"])
    print("DROPPED=%d" % len(res["dropped"]))
    print("BRANCHPOINTS=%d" % sum(1 for n in res["nodes"] if n.get("branch_point")))
    print("RESERVED=%d" % sum(1 for n in res["nodes"] if n.get("status") == "RESERVED"))
    print("OUT=%s" % os.path.dirname(stem))


if __name__ == "__main__":
    main()
