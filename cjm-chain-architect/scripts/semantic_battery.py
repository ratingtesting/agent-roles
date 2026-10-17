# -*- coding: utf-8 -*-
"""Семантическая батарея CJM — проверки вне G1-G12.
Запуск:  python semantic_battery.py ALL_CHAINS_*.json [core.csv]
Вывод:   JSON: {geo_mix:[...], jtbd_conflict:[...], no_fork:[...], guide_mismatch:[...],
         hot_tofu:[...], trunk_not_wider:[...]}
Выход:   0 чисто / 1 есть конфликты (красные блоки)."
import json, os, re, csv, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------- ГЕО ----------
MO_RX = re.compile(r"област|подмосков|люберц|ногинск|красногорск|пущин|домодедов|мытищ|балаших|"
    r"подольск|одинц|электросталь|ивантеев|фрязин|шатур|сергиев|дубн(?!инск)|\bклин\b|\bклина\b|"
    r"коломн(?!ская)|орехово[\-\s]+зуево|(?<!рег)\bистр[ау]\b|(?<!метро\s)(?<!на\s)(?<!улиц[ае]\s)\bщёлково\b|"
    r"химк|долгопрудн", re.I)
NEWMSK_RX = re.compile(r"новой\s+москв|новомоскв|зеленоград|троицк|щербинк|воскресенск(ое|ой|ая)|"
    r"орехово[\-\s]+борисов|солнечн", re.I)
BOTH_OK = re.compile(r"москв[а-яё]*\s+и\s+(област|московск)|под\s+москв|москва\s+или|москве\s+или|"
    r"рядом\s+с\s+москв", re.I)

def geo(ph):
    pl = (ph or "").lower()
    if BOTH_OK.search(pl): return "both"
    if NEWMSK_RX.search(pl): return "msk"
    if MO_RX.search(pl): return "mo"
    if "москв" in pl: return "msk"
    return "none"

# ---------- JTBD ----------
INTENT = [("buy", r"\bкуп(ить|аю|ал|али)\b|покупк|приобрет"),
          ("sell", r"прода(ть|жа|ли|л|ю)|продат"),
          ("rent_in", r"\bснять\b|снят|съём|снима|найм"),
          ("rent_out", r"\bсдать\b|сдач|сдаёт|арендодат|сдавать|аренд[ау]\b")]
def intents(ph):
    pl = re.sub(r"купли\s+продаж|купля\s+продаж", "сделка", (ph or "").lower())
    return {n for n, rx in INTENT if re.search(rx, pl)}
CONFLICT_PAIRS = [{"buy","sell"}, {"rent_in","rent_out"}, {"buy","rent_in"}, {"sell","rent_out"}]

GUIDE_MAP = {"buy":"guide_buy_safe_v8","self_kupit":"guide_buy_safe_v8","покупка":"guide_buy_safe_v8",
    "купить":"guide_buy_safe_v8","self_proverit":"guide_buy_safe_v8","проверка":"guide_buy_safe_v8",
    "sell":"guide_sell_profit_v3","self_prodat":"guide_sell_profit_v3","продажа":"guide_sell_profit_v3",
    "продать":"guide_sell_profit_v3","let":"guide_rent_smart_full","snyat":"guide_rent_smart_full",
    "снять (self_snyat)":"guide_rent_smart_full","rent_out":"guide_let_profit_v3","sdat":"guide_let_profit_v3"}

def node_phrase(n):
    # гео: исходная фраза если была; намерение: текущая
    return n.get("phrase") or ""

def node_geo_phrase(n):
    # ТЕКУЩая phrase: читателю продаётся она; phrase_original_synth — только маркер
    # замены текущего раунда. По исходникам прошлых раундов батарея даёт фантомные
    # миксы из уже исправленных узлов.
    return n.get("phrase") or ""

def is_synth(n):
    ph = node_phrase(n)
    return bool(n.get("synthetic")) or ph.startswith("[SYNTH]") or ph.lower().startswith("синтез")

def main():
    path = sys.argv[1]
    core_csv = sys.argv[2] if len(sys.argv) > 2 else None
    d = json.load(open(path, encoding="utf-8"))
    chains = d["chains"] if isinstance(d, dict) and "chains" in d else list(d.values() if isinstance(d, dict) else d)
    if core_csv and os.path.exists(core_csv):
        pass  # count-фолбэк из ядра — при желании подключить сюда
    out = {"geo_mix":[], "jtbd_conflict":[], "no_fork":[], "guide_mismatch":[],
           "hot_tofu":[], "trunk_not_wider":[], "dup_chain_id":0}
    ids = [c.get("chain_id") for c in chains]
    out["dup_chain_id"] = len(ids) - len(set(ids))
    for c in chains:
        cid = c.get("chain_id")
        nodes = sorted(c.get("nodes") or [], key=lambda n: n.get("depth") or 0)
        geos = collections.defaultdict(int)
        for n in nodes:
            g = geo(node_geo_phrase(n))
            if g in ("mo","msk"): geos[g]+=1
        if len(geos)==2: out["geo_mix"].append([cid, dict(geos), (c.get("jtbd") or "")[:60]])
        u = set()
        for n in nodes:
            if not is_synth(n): u |= intents(node_phrase(n))
        for pair in CONFLICT_PAIRS:
            if pair <= u:
                out["jtbd_conflict"].append([cid, sorted(pair)])
                break
        if not c.get("fork"): out["no_fork"].append(cid)
        else:
            tgt = GUIDE_MAP.get(str(c.get("direction") or "")) or GUIDE_MAP.get(str(c.get("direction") or "").lower())
            gb = c["fork"].get("guide_branch") or ""
            if tgt and gb and gb != tgt:
                has_check = any("провер" in (n.get("phrase") or "").lower() for n in nodes)
                # легальная связка: sell-ветка с звеном проверки допускает buy-гайд
                # (проверка — часть безопасной сделки). Не наоборот.
                if not (tgt=="guide_sell_profit_v3" and gb=="guide_buy_safe_v8" and has_check):
                    out["guide_mismatch"].append([cid, c.get("direction"), gb, tgt])
        if nodes:
            hot = (nodes[0].get("cjm_stage") or "").upper().find("BOFU") >= 0 or c.get("leaf_type")=="hot"
            if hot and any((n.get("cjm_stage") or "").upper()=="TOFU" for n in nodes):
                out["hot_tofu"].append(cid)
        trunks=[n for n in nodes if n.get("role")=="trunk"]
        lcs=[n.get("count") for n in nodes if n.get("role")=="leaf" and isinstance(n.get("count"), int)]
        if trunks and lcs and isinstance(trunks[0].get("count"), int) and trunks[0]["count"] <= max(lcs):
            out["trunk_not_wider"].append([cid, trunks[0]["count"], max(lcs)])
    bad = any(out[k] for k in ("geo_mix","jtbd_conflict","no_fork","guide_mismatch","hot_tofu","trunk_not_wider")) or out["dup_chain_id"]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
