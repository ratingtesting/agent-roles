#!/usr/bin/env python3
"""Проверка битых относительных ссылок .md в пакете документов (Proof Pack и аналоги).

Запуск:  python check_md_links.py /path/to/doc-pack
Игнорирует: .swarm/, graphify-out/, ссылки на https://, корневые-конвенционные имена.
Относительные ссылки считаются от папки текущего файла.
"""
import os, re, sys

def main(root):
    md = []
    for dp, dn, fn in os.walk(root):
        if any(x in dp for x in (".swarm", "graphify-out", ".git")):
            continue
        md += [os.path.join(dp, f) for f in fn if f.endswith(".md")]
    existing = {os.path.normpath(p).lower() for p in md}
    ref_re = re.compile(r'[`\[]([A-Za-z0-9_ ./\\-]+\.md)[`\]]')
    broken, allrefs = [], set()
    for fp in md:
        try:
            lines = open(fp, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            for m in ref_re.finditer(line):
                ref = m.group(1).strip()
                allrefs.add(ref)
                if ref.startswith(("http", "www", "#")):
                    continue
                if not ref.startswith(("../", "./", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "M", "B")):
                    continue  # корневое соглашение — пропускаем
                base = os.path.dirname(os.path.abspath(fp))
                tgt = os.path.normpath(os.path.join(base, ref))
                if os.path.abspath(tgt).lower() not in existing:
                    broken.append((os.path.relpath(fp, root), i, ref))
    print("Всего упоминаний .md:", len(allrefs))
    print("Битых ссылок:", len(set(broken)))
    for b in sorted(set(broken)):
        print("  ", b[0], f"L{b[1]}", "->", b[2])

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    main()