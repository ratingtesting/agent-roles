"""
Валидатор цепочек CJM. Гейт для масштабирования: сборка не проходит, пока не GREEN.

Запуск:  python cjm_gate.py V10_final.json [corpus.csv]
Корпус:  2-й аргумент или env CJM_CORPUS; иначе поиск рядом со скриптом.
Выход:   0 = GREEN, 1 = RED (список нарушений)

Правила (G1..G12). Каждое проверяет то, что человек на масштабе не проверит глазами.
Смысловые проверки (гео-микс, смена JTBD, развилка, ширина ствола по count) НЕ входят
в гейт — гнать отдельно батареей из references/semantic-battery.md.
"""
import csv
import io
import json
import os
import re
import sys

CORPUS_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                              "funnel_v3_ALL__magnet_v2.csv")
# 1% корпоративных случаев: имя ветки = id волны, не тема.
# ВАЖНО: для multi-leaf branches темы ВСЕХ листьев законны (поправка владельца 2026-10-10).

# ── G1: КОНКРЕТИЗАЦИЯ В ЗВЕНЕ ─────────────────────────────
# Всё, что сужает тему по объёму фраз, идёт в листья. В mid — нельзя (§1.2f/§1.2h).
CONCRET = {
    "тип дома": r"хрущ[её]в|сталин|пятиэтаж|панель|кирпич|деревянн|монолит|девятиэтаж|брежнев",
    "новый дом": r"новострой|от застройщика|застройщик|от застройщика|первичк",
    "новый москва": r"новой москв|новую москв|новая москв|новомосков",
    "метро": r"\bметро\b",
    "район": r"сокольник|люблино|отрадн|бутыр|печатник|электрозавод|калужск|варшавск|"
              r"таганск|комсомольск|курск|пролетарск|карач|черкиз|крым|ясенево|тверск|речн",
    "ремонт": r"ремонт|отделк|евроремонт|капремонт|перепланиров",
    "ипотека": r"ипотек|ипотеч|льготн|семейн.{0,12}ипотеч|кредит под",
    "этаж": r"\d\s*этаж|первый этаж|последний этаж",
    "комнатность": r"однокомн|двухкомн|трехкомн|двушка|однушка|трешк",
    "без посредников": r"без посредник|от собственника|без риелтор|от хозяина",
    "залог": r"залог|обременен",
}
# Исключения: конкретизация ДОЛЖНА быть звеном, если её объём ≥ порога ствола (§1.2h)
# Фраза попадает в исключение, если по ней ≥ порог фраз в ветке — проверяется в G2.
CONCRET_MIN_PHRASES = 30


def corpus_paths(path_arg=None):
    cand = []
    if path_arg:
        cand.append(path_arg)
    if os.environ.get("CJM_CORPUS"):
        cand.append(os.environ["CJM_CORPUS"])
    cand.append(CORPUS_DEFAULT)
    return cand


def load_corpus(path=None):
    """Корпус = множество НИЖНЕрегистровых фраз (ядро собрано в нижнем регистре;
    фразы новых волн могут идти с другой регистровой формой — сверять только lower)."""
    for cand in corpus_paths(path):
        if cand and os.path.exists(cand):
            with io.open(cand, encoding="utf-8-sig", newline="") as f:
                return {(r["phrase"] or "").strip().lower() for r in csv.DictReader(f, delimiter=";")}
    return set()


def corpus_count(path=None):
    for cand in corpus_paths(path):
        if cand and os.path.exists(cand):
            with io.open(cand, encoding="utf-8-sig", newline="") as f:
                return {(r["phrase"] or "").strip().lower(): int(r["count"] or 0)
                        for r in csv.DictReader(f, delimiter=";")}
    return {}


def stage_num(x):
    try:
        return int(x)
    except Exception:
        return -1


# Тема ветки — её собственная конкретизация. В mid она ЗАКОННА (§1.2h: ствол и звенья
# ветки про то, о чём ветка). Проверяется только конкретизация, ЧУЖАЯ ветке.
def branch_topic(name):
    n = (name or "").lower()
    for cls, kw in (("тип дома", "дом"), ("тип дома", "панель"), ("тип дома", "хрущ"), ("новый дом", "новострой"), ("новый дом", "застройщик"),
                    ("новый москва", "новой москв"), ("метро", "метро"), ("район", "район"),
                    ("ремонт", "ремонт"), ("ремонт", "отделк"), ("ипотека", "ипотеч"),
                    ("ипотека", "кредит"), ("этаж", "этаж"), ("комнатность", "комнатност"),
                    ("без посредников", "посредник"), ("залог", "риск")):
        if kw in n:
            return cls
    return None


def topics_for_branch(b, v, leaves):
    """Множество законных классов конкретизации ветки.
    Имя ветки может быть id волны (C5D2, r7_012-A), а не темой — тогда тема живёт
    в leaf_phrase / jtbd / самих листьях (мультилист легален: законны классы ВСЕХ
    листьев, поправка владельца 2026-10-10)."""
    t = branch_topic(b)
    topics = {t} if t else set()
    scope = " ".join([b or "", v.get("leaf_phrase") or "", v.get("jtbd") or ""] +
                     [(c.get("phrase") or "") for c in leaves]).lower()
    for cls, rx in CONCRET.items():
        if re.search(rx, scope, re.I):
            topics.add(cls)
    return topics


def check(branch_name, v, corpus, errs, warns):
    b = branch_name
    leaves = v.get("leaves") or []
    mid = v.get("mid") or []
    trunk = v.get("trunk")
    allc = leaves + mid + ([trunk] if trunk else [])
    topics = topics_for_branch(b, v, leaves)

    # G2: цепочка читателя. Cold — ровно 5 (1 лист + 3 звена + ствол).
    # Hot (первый лист stage_num==3) — 3–5: без TOFU-интро (§1.2n, поправка владельца).
    chain = 1 + len(mid) + (1 if trunk else 0)
    leaf_stage = leaves[0].get("stage_num") if leaves else None
    hot = leaf_stage == 3
    if hot:
        if not (3 <= chain <= 5):
            errs.append((b, "G2", "горячая цепочка %d статей, положено 3–5 (§1.2n: без TOFU-интро)" % chain))
    elif chain != 5:
        errs.append((b, "G2", "цепочка %d статей, положено ровно 5 (1 лист + 3 звена + ствол)" % chain))

    # G1: конкретизация в mid (кроме законных классов ветки)
    for i, c in enumerate(mid):
        for cls, rx in CONCRET.items():
            if cls in topics:
                continue
            if re.search(rx, c["phrase"], re.I):
                errs.append((b, "G1", "звено %d — ЧУЖАЯ конкретизация «%s» в звене: «%s» "
                                       "(тема ветки — %s; §1.2f: конкретизация вверх, в листья)"
                             % (i + 2, cls, c["phrase"], ", ".join(sorted(topics)) or "не задана")))

    # G1b: звено — ТОТ ЖЕ конкретный подтип, что уже есть в листе (§1.2c).
    # Ловит «лист хрущевка → звено хрущевка». Не ловит «лист от застройщика → звено
    # застройщики москвы»: подтипа там нет, звено просто шире.
    SUBTYPE = r"хрущ[её]в|сталин|пятиэтаж|панель|кирпич|брежнев|монолит|деревянн|девятиэтаж"
    # Подтип из ОБЪЯВЛЕННОЙ темы ветки (имя + leaf_phrase + jtbd, без самих листьев —
    # иначе leaf_sub всегда попадал бы в branch_sub и G1b никогда не срабатывал).
    topic_scope = " ".join([b or "", v.get("leaf_phrase") or "", v.get("jtbd") or ""])
    branch_sub = set(re.findall(SUBTYPE, topic_scope.lower().replace("ё", "е")))
    leaf_sub = set()
    for c in leaves:
        leaf_sub |= set(re.findall(SUBTYPE, c["phrase"].lower().replace("ё", "е")))
    for i, c in enumerate(mid):
        for s in set(re.findall(SUBTYPE, c["phrase"].lower().replace("ё", "е"))):
            if s in leaf_sub and s not in branch_sub:
                errs.append((b, "G1b", "звено %d «%s» — тот же подтип «%s», что уже есть в листьях "
                                       "(замена одного типа дома на другой ничего не меняет в пути, §1.2c)"
                             % (i + 2, c["phrase"], s)))

    # G3: подписи переходов — их должно быть 4 (лист→з1, з1→з2, з2→з3, з3→ствол)
    if not leaves or not leaves[0].get("link"):
        errs.append((b, "G3", "нет подписи перехода «лист → звено 1» (поле link у первого листа)"))
    for i, c in enumerate(mid):
        if not c.get("link"):
            errs.append((b, "G3", "нет подписи перехода к «%s» (звено %d)" % (c["phrase"], i + 2)))

    # G4: ступени не убывают по вертикали
    seq = [stage_num(c.get("stage_num")) for c in mid + ([trunk] if trunk else [])]
    for i in range(len(seq) - 1):
        if seq[i] < 0 or seq[i + 1] < 0:
            errs.append((b, "G4", "не задана ступень у звена %d или ствола" % (i + 2)))
        elif seq[i] > seq[i + 1]:
            errs.append((b, "G4", "ступень идёт назад: %d → %d между звеном %d и %d"
                         % (seq[i], seq[i + 1], i + 2, i + 3)))

    # G5: ствол шире последнего звена по объёму фраз и не совпадает со звеном
    if trunk and mid:
        if trunk["phrase"] in {c["phrase"] for c in mid}:
            errs.append((b, "G5", "ствол совпадает с звеном: «%s»" % trunk["phrase"]))
        if len(trunk["phrase"].split()) < len(mid[-1]["phrase"].split()) - 2:
            warns.append((b, "G5", "ствол «%s» может быть уже последнего звена «%s» — проверь глазами"
                          % (trunk["phrase"], mid[-1]["phrase"])))

    # G6: ствол — про ту же задачу, что ветка (по ключевым словам ветки)
    if trunk and mid:
        a = set(re.findall(r"[а-яё]{5,}", trunk["phrase"].lower()))
        bset = set(re.findall(r"[а-яё]{5,}", mid[-1]["phrase"].lower()))
        if bset and not (a & bset):
            warns.append((b, "G6", "ствол «%s» не делит слов с последним звеном «%s» — ветка может быть замкнута на чужой ствол"
                          % (trunk["phrase"], mid[-1]["phrase"])))

    # G7: фразы только из корпуса (регистронезависимо)
    for c in allc:
        if c.get("synthetic"):
            continue
        if corpus and (c["phrase"] or "").strip().lower() not in corpus:
            errs.append((b, "G7", "фразы нет в корпусе: «%s»" % c["phrase"]))

    # G8: синтез — только с обоснованием поиска
    for c in allc:
        if c.get("synthetic"):
            if not c.get("_syn") or not c["_syn"].strip():
                errs.append((b, "G8", "синтез без обоснования: «%s»" % c["phrase"]))
            # Синтез в середине ЗАПРЕЩЁН, кроме тонких веток: если конкретизация < порога
            # ствола (30 фраз), реального спроса на промежуточные звенья нет — тогда §1.2h
            # разрешает собирать ветку на синтезе, но с обоснованием поиска.
            if c.get("tag") == "mid":
                thin = len([x for x in leaves + mid + ([trunk] if trunk else [])]) < CONCRET_MIN_PHRASES
                if not thin:
                    errs.append((b, "G8", "синтез в середине цепочки: «%s» — при >=30 фраз в ветке "
                                          "промежуточный спрос проверяем, его отсутствие значит "
                                          "ветка собрана неверно (§1.2e)" % c["phrase"]))
                elif len(c.get("_syn", "")) < 60:
                    errs.append((b, "G8", "синтез в середине тонкой ветки без развёрнутого обоснования: "
                                          "«%s»" % c["phrase"]))

    # G9: хвост — год следующий (n+1), ровно один раз
    for c in allc:
        t = c.get("tail") or ""
        if t.count("202") != 1:
            errs.append((b, "G9", "в хвосте %d упоминаний года: «%s»" % (t.count("202"), t)))
        elif "2027" not in t:
            errs.append((b, "G9", "в хвосте не 2027 (текущий 2026 → n+1): «%s»" % t))

    # G10: 8 полей карточки заполнены (info_sought/info, content_angle/angle)
    ALIAS = {"info_sought": ("info_sought", "info"),
             "content_angle": ("content_angle", "angle")}
    for c in allc:
        card = c.get("card") or {}
        for fld, names in list(ALIAS.items()) + [(f, (f,)) for f in
                                                ("thought", "emotion", "objection",
                                                 "barrier", "pain", "tail")]:
            if not any((c.get(n) or card.get(n) or "").strip() for n in names):
                errs.append((b, "G10", "пустое поле %s у «%s»" % (fld, c["phrase"])))

    # G11: нет повторов фраз внутри ветки
    seen = {}
    for c in allc:
        if c["phrase"] in seen:
            errs.append((b, "G11", "фраза повторяется в ветке: «%s»" % c["phrase"]))
        seen[c["phrase"]] = 1

    # G12: находки, рекомендации и план присутствуют (R10)
    for key in ("findings", "recommendations", "plan"):
        if not v.get(key):
            errs.append((b, "G12", "нет блока «%s» (§1.5: находки становятся планом)" % key))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "V10_final.json"
    corpus_csv = sys.argv[2] if len(sys.argv) > 2 else None
    data = json.load(open(path, encoding="utf-8"))
    if isinstance(data, dict) and "chains" in data:
        # формат списка цепочек -> формат гейта: конвертирует convert_to_gate.py
        sys.stderr.write("ОЖИДАЕТСЯ dict веток {leaves,mid,trunk}. Прогони сначала convert_to_gate.py.\n")
        return 2
    corpus = load_corpus(corpus_csv)

    errs, warns = [], []
    for name, v in data.items():
        check(name, v, corpus, errs, warns)

    print("=" * 96)
    print("CJM GATE — %d веток, корпус %s фраз" % (len(data), len(corpus) if corpus else "НЕ ЗАГРУЖЕН"))
    print("=" * 96)
    if errs:
        by = {}
        for b, g, m in errs:
            by.setdefault(g, []).append((b, m))
        for g in sorted(by):
            print("\n%s — %d нарушений" % (g, len(by[g])))
            for b, m in by[g]:
                print("   %-24s %s" % (b, m))
    if warns:
        print("\nПРЕДУПРЕЖДЕНИЯ (не блокируют, требуют глаз):")
        for b, g, m in warns:
            print("   %-24s [%s] %s" % (b, g, m))
    print("\n" + "=" * 96)
    print("ИТОГ: %s — ошибок %d, предупреждений %d"
          % ("GREEN" if not errs else "RED", len(errs), len(warns)))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
