"""hermes-verify-<name>.py — ad-hoc verification template (no test framework).

Usage:
  1. Copy this to C:\\Users\\<user>\\AppData\\Local\\Temp\\hermes-verify-<name>.py
  2. Replace APP_PATH, NEW_SRC, OLD_SRC, and CASES for your target.
  3. Run: python "C:\\Users\\<user>\\AppData\\Local\\Temp\\hermes-verify-<name>.py"
  4. Clean up: rm the temp file after the run.

The script loads the ACTUAL on-disk file PLUS reconstructed NEW and OLD source
variants, and tests the same cases against all three. If the test passes on
correct and fails on buggy, it is discriminating (not tautological).
"""
import importlib.util
import os
import sys

APP_PATH = r"<absolute-path-to-your-target-file>"
NEW_SRC = "def add(a, b):\n    return a + b\n"
OLD_SRC = "def add(a, b):\n    return 5\n"
CASES = [(2, 3, 5), (0, 0, 0), (-1, 1, 0), (-5, -7, -12), (100, 200, 300)]


def load_add(src):
    spec = importlib.util.spec_from_loader("t", loader=None)
    mod = importlib.util.module_from_spec(spec)
    exec(compile(src, APP_PATH, "exec"), mod.__dict__)
    return mod.add


def run(add_fn, label):
    fails = [f"  add({a},{b}) -> {add_fn(a,b)} (expected {e})"
             for a, b, e in CASES if add_fn(a, b) != e]
    if fails:
        print(f"[{label}] FAIL ({len(fails)}):")
        for f in fails:
            print(f)
        return False
    print(f"[{label}] PASS ({len(CASES)} cases)")
    return True


def main():
    print(f"=== hermes-verify: discriminating verification ===")
    print(f"target: {APP_PATH}\n")
    with open(APP_PATH) as f:
        disk_add = load_add(f.read())
    d = run(disk_add, "ON-DISK")
    n = run(load_add(NEW_SRC), "NEW")
    o = run(load_add(OLD_SRC), "OLD")
    print("\n--- Verdict ---")
    ok = d and n and not o
    print("PASS: on-disk is correct; test is discriminating." if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
