"""Ad-hoc verification template for Hermes on Windows git-bash (MSYS).

Copy to %TEMP%\\hermes-verify-<thing>.py, edit PROJECT_DIR + cases, then run with a
NATIVE path so MSYS doesn't mangle the argument:

    python "C:\\Users\\<user>\\AppData\\Local\\Temp\\hermes-verify-<thing>.py"

Or against a project venv:

    .venv/Scripts/python.exe "C:\\...native...\\hermes-verify-<thing>.py"

Key rules baked in below:
  - sys.path uses a raw NATIVE path (r"C:\\..."), never "/c/..." — Windows Python
    does not resolve MSYS paths.
  - Prints PASS/FAIL per case and exits non-zero on any failure, so the terminal
    exit code is real verification evidence.
"""
import sys

# EDIT: native Windows path to the project so `import` finds your module.
sys.path.insert(0, r"C:\Users\<user>\path\to\project")

from your_module import your_func  # EDIT

# EDIT: input -> expected output
cases = {
    "Hello World! 2026": "hello-world-2026",
}

fail = 0
for src, want in cases.items():
    got = your_func(src)
    ok = got == want
    fail += not ok
    print(f"{'PASS' if ok else 'FAIL'}: {src!r} -> {got!r} (want {want!r})")

print("RESULT:", "ALL PASS" if not fail else f"{fail} FAILED")
sys.exit(1 if fail else 0)
