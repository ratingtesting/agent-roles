#!/usr/bin/env python3
"""Swarm Monitor — JSON API + веб-дашборд для наблюдения за роем Hermes Kanban.

Использование:
  1. Скопировать этот файл и swarm_dashboard.html в <проект>/.swarm/
  2. Настроить ROOT, BOARD, FACES под свою доску.
  3. terminal(background=True): cd <проект>/.swarm && python swarm_monitor.py
  4. open_preview("http://127.0.0.1:8777")

Почему не просто `kanban list` в цикле: Пётр требует видеть рой — лицо у каждого
агента, живая строка «чем занят», размеры файлов результата.
"""
import json, os, re, subprocess, threading, time
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = r"C:\path\to\project"      # где рой пишет артефакты
HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = "review-gate"
PORT = 8777

# префикс карточки -> (лицо, имя агента, чем занят)
FACES = {
    "A.":  ("🧭", "Chief Product Architect", "Сводит корпус в единую спеку"),
    "B1.": ("🔴", "Product Killer",        "Атакует сложность MVP"),
    "B2.": ("🔵", "Growth Killer",         "Ломает вирусную петлю"),
    "B3.": ("🟢", "Economy Killer",        "Ищет утечки денег"),
    "B4.": ("🟠", "Architecture Killer",   "Ловит переусложнение"),
    "B5.": ("⚖️", "Risk Reviewer",         "Право и ToS"),
    "C.":  ("👑", "Founder Decision Gate", "Готовит решения основателю"),
}
# ожидаемые артефакты в корне ROOT
WANT_FILES = ["MASTER_PRODUCT_SPEC.md", "CONFLICT_REGISTER.md", "FOUNDER_DECISIONS.md"]
REVIEW_DIR = "REVIEW"

STATE = {"tasks": [], "files": {}, "reviews": {}, "log": [], "ts": 0}
# ВАЖНО: ⊙ и прочие глифы статусов тоже включены — иначе карточка молча пропадёт с дашборда
ROW = re.compile(r"^([●◻⊘✓⊙])\s+(\S+)\s+(\w+)\s+(\S+)\s+(.+?)\s*$")


def sh(args, timeout=50):
    """kanban log на длинном воркере не укладывается в 60с — держим свой timeout."""
    try:
        p = subprocess.run(args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.stdout
    except Exception:
        return ""


def poll():
    while True:
        raw = sh(["hermes", "--profile", "app", "kanban", "--board", BOARD, "list"])
        tasks = []
        for line in raw.splitlines():
            m = ROW.match(line.strip())
            if not m:
                continue                      # шапка "Board: ..." отсеивается тут
            glyph, tid, status, _asg, title = m.groups()
            key = next((k for k in FACES if title.startswith(k)), None)
            face, name, duty = FACES.get(key, ("🤖", title, ""))
            tasks.append({"id": tid, "status": status, "title": title,
                          "face": face, "name": name, "duty": duty})

        files = {}
        for f in WANT_FILES:
            p = os.path.join(ROOT, f)
            files[f] = os.path.getsize(p) if os.path.exists(p) else 0

        reviews = {}
        rd = os.path.join(ROOT, REVIEW_DIR)
        if os.path.isdir(rd):
            for f in sorted(os.listdir(rd)):
                if f.endswith(".md"):
                    reviews[f] = os.path.getsize(os.path.join(rd, f))

        act = []
        for t in tasks:
            if t["status"] == "running":
                lg = sh(["hermes", "--profile", "app", "kanban", "--board", BOARD,
                         "log", t["id"]], timeout=40)
                for ln in reversed(lg.splitlines()):
                    s = re.sub(r"\s+", " ", ln.strip())
                    s = re.sub(r"^[┊╭╰│─\s]+", "", s)   # снять рамки TUI
                    if len(s) > 12 and not s.startswith("╮"):
                        act.append({"who": t["name"], "face": t["face"], "line": s[:150]})
                        break

        STATE.update(tasks=tasks, files=files, reviews=reviews,
                     log=act, ts=int(time.time()))
        time.sleep(30)


class H(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api"):
            b = json.dumps(STATE, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return
        self.path = "/swarm_dashboard.html"
        return SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    os.chdir(HERE)
    threading.Thread(target=poll, daemon=True).start()
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
