#!/usr/bin/env python3
"""
Reference implementation: autonomous folder-watch loop (stdlib only).

Trigger modes (same code):
  default / --once : run exactly one cycle then exit (use from cron / Task Scheduler)
  --daemon         : long-lived interval loop, supports goal-chasing idle-stop
  webhook          : external hook forces a cycle instead of waiting (optional)

Five design dimensions covered:
  trigger      -> cron one-shot (primary), daemon (secondary), webhook-ready
  per-cycle    -> sentinel, dir-readable, inventory, ledger diff, stability, allowlist
  action       -> mark processing, pluggable processor, done/failed, backoff retry
  stop         -> STOP sentinel, idle-stop, max-runtime, signal
  escalate     -> per-file exhaustion, error-rate, quarantine, backlog, infra-fail

Run a functional self-test, then delete test artifacts before shipping deliverables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

LOG = logging.getLogger("loop")


@dataclass
class Config:
    control_dir: Path = Path(".")
    watch_dir: Path = Path("watch")
    out_dir: Path = Path("out")
    done_dir: Path = Path("done")
    failed_dir: Path = Path("failed")
    state_file: Path = Path("state.json")
    alert_file: Path = Path("alerts.log")
    stop_file: Path = Path("STOP")

    interval_s: float = 60.0
    max_attempts: int = 3
    stability_wait: float = 1.0
    ext_allow: list = field(default_factory=lambda: ["*"])
    recurse: bool = False

    idle_stop: int = 0
    max_runtime_s: float = 0.0
    escalate_error_rate: float = 0.5
    escalate_backlog: int = 50
    backlog_window: int = 5

    processor: Optional[str] = None
    escalation_hook: Optional[str] = None
    delete_done: bool = False

    @classmethod
    def from_env(cls, control_dir: Path) -> "Config":
        def p(name, default):
            v = os.environ.get(name)
            return v if v is not None else default

        def b(name, default):
            v = os.environ.get(name)
            return default if v is None else v.strip() in ("1", "true", "yes")

        ext = p("LOOP_EXT_ALLOW", "*")
        ext_list = ["*"] if ext == "*" else [e.strip().lstrip(".") for e in ext.split(",") if e.strip()]
        return cls(
            control_dir=control_dir,
            watch_dir=control_dir / p("LOOP_WATCH_DIR", "watch"),
            out_dir=control_dir / p("LOOP_OUT_DIR", "out"),
            done_dir=control_dir / p("LOOP_DONE_DIR", "done"),
            failed_dir=control_dir / p("LOOP_FAILED_DIR", "failed"),
            state_file=control_dir / p("LOOP_STATE_FILE", "state.json"),
            alert_file=control_dir / p("LOOP_ALERT_FILE", "alerts.log"),
            stop_file=control_dir / p("LOOP_STOP_FILE", "STOP"),
            interval_s=float(p("LOOP_INTERVAL_S", "60")),
            max_attempts=int(p("LOOP_MAX_ATTEMPTS", "3")),
            stability_wait=float(p("LOOP_STABILITY_WAIT", "1.0")),
            ext_allow=ext_list,
            recurse=b("LOOP_RECURSE", False),
            idle_stop=int(p("LOOP_IDLE_STOP", "0")),
            max_runtime_s=float(p("LOOP_MAX_RUNTIME_S", "0")),
            escalate_error_rate=float(p("LOOP_ESCALATE_ERROR_RATE", "0.5")),
            escalate_backlog=int(p("LOOP_ESCALATE_BACKLOG", "50")),
            backlog_window=int(p("LOOP_BACKLOG_WINDOW", "5")),
            processor=p("LOOP_PROCESSOR", None),
            escalation_hook=p("LOOP_ESCALATION_HOOK", None),
            delete_done=b("LOOP_DELETE_DONE", False),
        )


class Ledger:
    def __init__(self, path: Path):
        self.path = path
        self.records = {}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                self.records = json.loads(self.path.read_text(encoding="utf-8") or "{}")
            except (json.JSONDecodeError, OSError) as e:
                raise RuntimeError(f"cannot read state ledger {self.path}: {e}")
        else:
            self.records = {}

    def save(self):
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.records, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)

    def status(self, key):
        rec = self.records.get(key)
        return rec.get("status") if rec else None

    def update(self, key, **fields):
        rec = self.records.setdefault(key, {})
        rec.update(fields)
        rec["updated"] = time.time()


class FolderWatchLoop:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.ledger = Ledger(cfg.state_file)
        self.started = time.time()
        self._stop = False
        self._pending_history = []
        self._recent = []
        self._setup_dirs()
        self._signals()

    def _setup_dirs(self):
        for d in (self.cfg.watch_dir, self.cfg.out_dir, self.cfg.done_dir, self.cfg.failed_dir):
            d.mkdir(parents=True, exist_ok=True)

    def _signals(self):
        def h(signum, _f):
            LOG.info("signal %s -> graceful shutdown", signum)
            self._stop = True
        try:
            signal.signal(signal.SIGINT, h)
            signal.signal(signal.SIGTERM, h)
        except (ValueError, OSError):
            pass

    def escalate(self, level, message):
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            with self.cfg.alert_file.open("a", encoding="utf-8") as fh:
                fh.write(f"{ts} [{level}] {message}\n")
        except OSError as e:
            LOG.error("alert write failed: %s", e)
        LOG.warning("ESCALATE %s: %s", level, message)
        if self.cfg.escalation_hook:
            try:
                subprocess.run(self.cfg.escalation_hook.replace("{msg}", message),
                               shell=True, capture_output=True, timeout=30,
                               encoding="utf-8", errors="ignore")
            except Exception as e:  # noqa: BLE001
                LOG.error("hook failed: %s", e)

    def _files(self):
        it = self.cfg.watch_dir.rglob("*") if self.cfg.recurse else self.cfg.watch_dir.glob("*")
        for p in it:
            if p.is_file():
                yield p

    def _allowed(self, path):
        if "*" in self.cfg.ext_allow:
            return True
        return path.suffix.lstrip(".").lower() in self.cfg.ext_allow

    def _stable(self, path):
        try:
            s1 = path.stat().st_size
            time.sleep(self.cfg.stability_wait)
            s2 = path.stat().st_size
        except OSError as e:
            LOG.warning("stat fail %s: %s", path, e)
            return False
        return s1 == s2

    @staticmethod
    def _checksum(path):
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _process(self, path):
        if self.cfg.processor:
            cmd = self.cfg.processor.replace("{path}", str(path)).replace("{name}", path.name)
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300,
                                   encoding="utf-8", errors="ignore")
            except Exception as e:  # noqa: BLE001
                LOG.error("processor crashed %s: %s", path, e)
                return False
            if r.returncode != 0:
                LOG.error("processor failed (%s) %s: %s", r.returncode, path, r.stderr.strip())
                return False
            return True
        try:
            dest = self.cfg.out_dir / path.name
            shutil.copy2(path, dest)
            cs = self._checksum(dest)
            (self.cfg.out_dir / (path.name + ".manifest.json")).write_text(
                json.dumps({"source": str(path), "checksum_sha256": cs, "processed": time.time()}, indent=2),
                encoding="utf-8")
            return True
        except OSError as e:
            LOG.error("built-in processor failed %s: %s", path, e)
            return False

    def _quarantine(self, path):
        try:
            shutil.move(str(path), str(self.cfg.failed_dir / path.name))
        except OSError as e:
            LOG.error("move to failed/ failed %s: %s", path, e)

    def _commit_done(self, path):
        if self.cfg.delete_done:
            try:
                path.unlink()
                return
            except OSError as e:
                LOG.error("delete_done failed %s: %s", path, e)
        try:
            shutil.move(str(path), str(self.cfg.done_dir / path.name))
        except OSError as e:
            LOG.error("move to done/ failed %s: %s", path, e)

    def cycle(self):
        if self.cfg.stop_file.exists():
            LOG.info("stop sentinel present")
            self._stop = True
        if not self.cfg.watch_dir.is_dir():
            self.escalate("CRITICAL", f"watch dir unreachable: {self.cfg.watch_dir}")
            raise RuntimeError("watch directory unreachable")

        handled = 0
        pending = 0
        for path in self._files():
            key = str(path.relative_to(self.cfg.watch_dir))
            status = self.ledger.status(key)
            if status == "done":
                continue
            if not self._allowed(path):
                LOG.info("quarantine disallowed: %s", path)
                self._quarantine(path)
                self.ledger.update(key, status="failed", reason="disallowed-extension")
                self.ledger.save()
                self._recent.append("fail")
                self.escalate("QUARANTINE", f"disallowed extension: {key}")
                handled += 1
                continue
            if not self._stable(path):
                pending += 1
                continue
            rec = self.ledger.records.get(key, {})
            attempts = int(rec.get("attempts", 0))
            if status == "pending" and attempts >= 1:
                backoff = min(2 ** attempts, 30)
                if time.time() - rec.get("updated", 0) < backoff:
                    pending += 1
                    continue
            self.ledger.update(key, status="processing", attempts=attempts)
            self.ledger.save()
            LOG.info("processing %s (attempt %d)", key, attempts + 1)
            ok = self._process(path)
            if ok:
                self._commit_done(path)
                self.ledger.update(key, status="done", attempts=attempts + 1,
                                   checksum=self._checksum(self.cfg.out_dir / path.name)
                                   if not self.cfg.delete_done else None)
                self.ledger.save()
                self._recent.append("ok")
                handled += 1
                LOG.info("done: %s", key)
            else:
                attempts += 1
                if attempts >= self.cfg.max_attempts:
                    self._quarantine(path)
                    self.ledger.update(key, status="failed", attempts=attempts, reason="exhausted-retries")
                    self.ledger.save()
                    self._recent.append("fail")
                    self.escalate("PERMANENT", f"exhausted {self.cfg.max_attempts} attempts: {key}")
                    handled += 1
                else:
                    self.ledger.update(key, status="pending", attempts=attempts)
                    self.ledger.save()
                    self._recent.append("fail")
                    pending += 1
                    LOG.warning("transient failure %s (attempt %d)", key, attempts)

        window = self._recent[-20:]
        if window:
            fails = window.count("fail")
            if fails / len(window) > self.cfg.escalate_error_rate and fails >= 3:
                self.escalate("ERROR_RATE", f"{fails}/{len(window)} recent files failed")
        self._pending_history.append(pending)
        self._pending_history = self._pending_history[-self.cfg.backlog_window:]
        if (len(self._pending_history) >= self.cfg.backlog_window
                and all(b >= self.cfg.escalate_backlog for b in self._pending_history)
                and self.cfg.escalate_backlog > 0):
            self.escalate("BACKLOG", f"backlog stuck >= {self.cfg.escalate_backlog} for {self.cfg.backlog_window} cycles")
        return handled

    def _consume_stop(self):
        if self.cfg.stop_file.exists():
            try:
                self.cfg.stop_file.unlink()
            except OSError:
                pass

    def run_once(self):
        try:
            self.cycle()
        except RuntimeError:
            return 2
        self._consume_stop()
        return 0

    def run_daemon(self):
        idle = 0
        while not self._stop:
            try:
                handled = self.cycle()
            except RuntimeError:
                return 2
            idle = 0 if handled > 0 else idle + 1
            if self.cfg.idle_stop and idle >= self.cfg.idle_stop:
                LOG.info("goal met: %d idle cycles", idle)
                break
            if self.cfg.max_runtime_s and (time.time() - self.started) >= self.cfg.max_runtime_s:
                LOG.info("max runtime reached")
                break
            for _ in range(max(1, int(self.cfg.interval_s))):
                if self._stop:
                    break
                time.sleep(1)
        self._consume_stop()
        return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Autonomous folder-watch loop")
    ap.add_argument("--control-dir", default=".")
    ap.add_argument("--daemon", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cd = Path(args.control_dir).resolve()
    cd.mkdir(parents=True, exist_ok=True)
    cfg = Config.from_env(cd)
    loop = FolderWatchLoop(cfg)
    return loop.run_daemon() if args.daemon else loop.run_once()


if __name__ == "__main__":
    sys.exit(main())
