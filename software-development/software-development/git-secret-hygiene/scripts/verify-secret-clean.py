#!/usr/bin/env python3
"""Ad-hoc verifier for git secret-hygiene work.

Usage: python3 verify-secret-clean.py [REPO_PATH] [SECRET]

Checks:
  A) source has no hard-coded secret; reads from os.environ
  B) git tracks only safe files (.env / secret file excluded)
  C) module is functional: exec source with stub + real key in env
  D) gitleaks reports clean (exit 0, "no leaks found")

This is ad-hoc verification, not a CI suite. Cleans up nothing; run and inspect.
"""
import os, sys, subprocess, types

REPO = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
KEY = sys.argv[2] if len(sys.argv) > 2 else "sk-9a8b7c6d5e4f3a2b1c0d"
SRC = os.path.join(REPO, "notify.py")

# A) source has no hard-coded key; reads from env
src = open(SRC).read()
assert KEY not in src, "LEAK in source"
assert 'os.environ["API_KEY"]' in src, "no env read"

# B) git tracks only safe files; .env excluded
files = subprocess.check_output(["git", "-C", REPO, "ls-files"], text=True).split()
assert ".env" not in files and {"notify.py", ".gitignore"} <= set(files), f"bad tracked set: {files}"

# C) functional exec with stub + real key set in the live os.environ
os.environ["API_KEY"] = KEY
req = types.SimpleNamespace(post=lambda *a, **k: types.SimpleNamespace(raise_for_status=lambda: None))
glb = {"__name__": "v", "os": os, "requests": req}
exec(compile(src, "notify.py", "exec"), glb)
assert glb["API_KEY"] == KEY

# D) gitleaks clean on committed tree
gl = subprocess.run(["gitleaks", "detect", "--source", REPO, "--no-banner"],
                    capture_output=True, text=True)
assert gl.returncode == 0 and "no leaks found" in (gl.stdout + gl.stderr), gl.stdout + gl.stderr

print("ALL VERIFICATION PASSED: no key in source, .env ignored, code reads env, gitleaks clean")
