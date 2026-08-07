#!/usr/bin/env python3
"""Mutation battery — machine proof that loop-guard tests actually discriminate.

Copy next to the loop you are building, edit SOURCES + MUTATIONS, run it.

Why this exists: tests for autonomous-loop guards are unusually prone to passing for the
wrong reason. The loop stops, the test sees "stopped", green — but the specific brake
under test may be dead code. This runner disables ONE guard at a time in a throwaway copy
of the tree and requires the SAME test suite to go RED. Green on a mutant means that guard
is untested.

Design notes learned the hard way:
  * Mutate in a COPY (arena dir), never in place. Never touch the real sources.
  * Delete __pycache__ in the arena, or stale bytecode masks the mutation.
  * A missing anchor string is INCONCLUSIVE (exit 2), never a pass. Refactoring the loop
    WILL break anchors — that is the runner telling you to re-anchor, not a test failure.
    Re-run the battery after every refactor of the code under test.
  * Prefer anchors on the guard's condition line (`if X >= cap:` -> `if False:`); they are
    short, unique, and survive formatting churn better than whole blocks.

Exit codes: 0 = every mutation caught · 1 = some mutation survived (tests too weak)
            2 = inconclusive (suite not green on correct code, or anchor not found)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE / ".mutation-battery"

# --- EDIT ME -------------------------------------------------------------------
# Every file the test suite needs, including the test file itself.
SOURCES = ["loop.py", "breaker.py", "throttle.py", "resource_mock.py", "test_loop.py"]

# How to run the suite inside the arena. Works with a plain script or pytest.
TEST_CMD = [sys.executable, "test_loop.py"]

# (name, file, anchor_to_replace, replacement) — each disables exactly ONE guard.
MUTATIONS: list[tuple[str, str, str, str]] = [
    ("no-stability-window", "loop.py",
     "reached = self.consecutive_green >= self.config.stable_polls",
     "reached = True"),
    ("no-similarity-breaker", "breaker.py",
     "if self.similar_streak >= self.config.similarity_cap:", "if False:"),
    ("no-absolute-ceiling", "breaker.py",
     "if iteration > self.config.absolute_max_iters:", "if False:"),
    ("no-per-item-cap", "loop.py",
     "if used >= self.config.max_actions_per_item:", "if False:"),
    ("no-call-budget", "breaker.py",
     "if self._external_calls_this_iter >= self.config.external_calls_per_iter:",
     "if False:"),
    ("no-rate-limit", "throttle.py",
     "if len(self._events) >= self.max_events:", "if False:"),
    # Autonomy-boundary mutation: make the loop perform an irreversible action itself.
    # Tests that assert the mock's irreversible-action journals stay empty must catch it.
    ("autonomous-irreversible-action", "loop.py",
     "        escalation: dict[str, Any] = {",
     "        self.resource.revert(item.commit)\n        escalation: dict[str, Any] = {"),
]
# --- END EDIT ------------------------------------------------------------------


def run_tests(where: Path) -> tuple[bool, str]:
    proc = subprocess.run(TEST_CMD, cwd=where, capture_output=True, text=True, timeout=300)
    return proc.returncode == 0, proc.stdout + proc.stderr


def seed(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in SOURCES:
        shutil.copy2(HERE / name, dest / name)
    shutil.rmtree(dest / "__pycache__", ignore_errors=True)


def main() -> int:
    shutil.rmtree(ARENA, ignore_errors=True)

    control = ARENA / "00-correct"
    seed(control)
    green, out = run_tests(control)
    if not green:
        print("INCONCLUSIVE: suite is not green on the correct code\n" + out[-2000:])
        return 2
    print("control (correct implementation): GREEN")

    survived = 0
    for name, target, old, new in MUTATIONS:
        arm = ARENA / name
        seed(arm)
        path = arm / target
        text = path.read_text(encoding="utf-8")
        if old not in text:
            print(f"INCONCLUSIVE: anchor for mutation '{name}' not found in {target} "
                  f"— re-anchor it (did you refactor?)")
            return 2
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

        mutant_green, mout = run_tests(arm)
        if mutant_green:
            survived += 1
            print(f"SURVIVED  {name}: suite stayed green — this guard is untested")
        else:
            failed = [l for l in mout.splitlines() if l.startswith("FAILED")]
            print(f"caught    {name}: {len(failed)} test(s) failed")

    total = len(MUTATIONS)
    print(f"\nMUTATION BATTERY: {total - survived}/{total} caught")
    if survived:
        print("RESULT: FAIL — strengthen the tests (never weaken the guards)")
        return 1
    print("RESULT: PASS — tests discriminate on every guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
