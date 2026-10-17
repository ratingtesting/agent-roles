#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Keeper волны канбан-роя: держит ровно N активных (ready+running) карточек.
Запуск: python keeper_wave.py <board_slug> [N=15] [interval=120]

Правила (см. SKILL.md «KEEPER»):
- Только поднимает статусы archived -> ready SQL-ом. НЕ вызывает dispatch,
  НЕ спавнит процессы — делает это штатный gateway-диспетчер (тик ~60c).
- Потолок: промоутит лишь когда ready+running < N (защита от всплеска).
- Обычный background-процесс (НЕ persist): умирает вместе с сессией.
- Сам завершается, когда archived и активные пусты.
- Чистит мёртвый .install.lock (пустой и старше 10 мин) на каждом тике —
  он оставляет воркеры падать с exit 255 (см. SKILL.md).
"""
import sqlite3, time, sys, os, glob

HERMES_HOME = os.environ.get("HERMES_HOME") or os.path.expanduser(
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes"))
INTERVAL = int(sys.argv[3]) if len(sys.argv) > 3 else 120

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: keeper_wave.py <board_slug> [N=15] [interval=120]")
    board = sys.argv[1]
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    db = os.path.join(HERMES_HOME, "kanban", "boards", board, "kanban.db")
    assert os.path.exists(db), f"no kanban.db for board {board}: {db}"
    print(f"keeper[{board}] N={target} interval={INTERVAL}s", flush=True)
    n = 0
    while True:
        try:
            # мёртвый install.lock чистка
            for lk in glob.glob(os.path.join(HERMES_HOME, "installs", "*", ".install.lock")):
                try:
                    if os.path.getsize(lk) == 0 and time.time() - os.path.getmtime(lk) > 600:
                        os.remove(lk); print("removed dead .install.lock", flush=True)
                except OSError: pass
            con = sqlite3.connect(db); cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('ready','running')")
            active = cur.fetchone()[0]
            promo = 0
            if active < target:
                cur.execute(
                    """UPDATE tasks SET status='ready', claim_lock=NULL, claim_expires=NULL,
                       current_run_id=NULL, worker_pid=NULL, consecutive_failures=0
                       WHERE id IN (SELECT id FROM tasks WHERE status='archived'
                                    ORDER BY created_at LIMIT ?)""", (target - active,))
                promo = cur.rowcount
            con.commit()
            cur.execute("SELECT COUNT(*) FROM tasks WHERE status='archived'")
            left = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM tasks WHERE status='done'")
            done = cur.fetchone()[0]
            con.close()
            n += 1
            print(f"[{n}] {time.strftime('%H:%M')} active={active} promo={promo} archived={left} done={done}", flush=True)
            if left == 0 and active == 0:
                print("QUEUE EMPTY — keeper exiting", flush=True); return
        except Exception as e:
            print(f"err: {e}", flush=True)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
