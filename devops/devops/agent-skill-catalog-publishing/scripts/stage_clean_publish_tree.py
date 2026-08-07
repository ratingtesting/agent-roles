#!/usr/bin/env python3
"""Stage a git-clean copy of a skill for catalog publishing, and refuse if it leaks.

WHY: `clawhub publish <path>` packages EVERY file in the folder and does NOT read
.gitignore. A live skill directory routinely holds private material (internal QA notes,
article drafts, scraped account HTML, __pycache__) that is absent from git. Publishing it
ships that to a public registry, and unlike GitHub a registry release cannot be reverted.

This stages from `git archive <ref>` — so the tree contains exactly what is committed —
then asserts the file count matches `git ls-files` and greps for private patterns.
Exits non-zero on any mismatch so it can gate a publish step.

Usage:
    python stage_clean_publish_tree.py <repo_dir> <git_ref> <stage_dir>

Example:
    python stage_clean_publish_tree.py ~/skills/keelwright v1.4.7 "$TEMP/clawhub-stage"
    # then, only if exit 0:
    cd "$TEMP/clawhub-stage" && clawhub publish . --no-input --version 1.4.7 --slug keelwright
"""
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile

# Anything matching these must never reach a public catalog.
PRIVATE_PATTERNS = [
    "internal",           # QA logs, session notes, private methodology
    "__pycache__",
    ".pyc",
    "-draft.md",
    "-human.md",
    "PUBLISHING_REGISTRY",
    "backups",
    ".env",
    "cookies",
    "secret",
    "token",
]
# Scraped pages / generated assets: match by extension at the tree root.
PRIVATE_SUFFIXES = [".html", ".png", ".jpg", ".jpeg", ".zip"]


def git(repo: pathlib.Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"[stage] git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r.stdout


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2

    repo = pathlib.Path(sys.argv[1]).resolve()
    ref = sys.argv[2]
    stage = pathlib.Path(sys.argv[3]).resolve()

    if not (repo / ".git").exists():
        print(f"[stage] not a git repo: {repo}")
        return 2

    # Refuse to stage a ref whose tree differs from what is committed.
    dirty = [ln for ln in git(repo, "status", "--short").splitlines()
             if ln and not ln.startswith("??")]
    if dirty:
        print("[stage] REFUSING: uncommitted changes — publish would not match the tag:")
        for ln in dirty[:10]:
            print(f"    {ln}")
        return 1

    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # git archive gives exactly the committed tree — no untracked files by construction.
    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tf:
        tar_path = pathlib.Path(tf.name)
    try:
        r = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar",
                            "-o", str(tar_path), ref], capture_output=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(f"[stage] git archive {ref} failed: {r.stderr.strip()}")
            return 1
        with tarfile.open(tar_path) as tar:
            tar.extractall(stage)
    finally:
        tar_path.unlink(missing_ok=True)

    staged = [p for p in stage.rglob("*") if p.is_file()]
    tracked = [ln for ln in git(repo, "ls-files").splitlines() if ln.strip()]

    print(f"[stage] ref={ref}")
    print(f"[stage] staged files : {len(staged)}")
    print(f"[stage] git ls-files : {len(tracked)}")

    failures = []
    if len(staged) != len(tracked):
        failures.append(f"count mismatch: staged {len(staged)} vs tracked {len(tracked)}")

    leaks = []
    for p in staged:
        rel = p.relative_to(stage).as_posix()
        low = rel.lower()
        if any(pat.lower() in low for pat in PRIVATE_PATTERNS):
            leaks.append(rel)
        elif p.suffix.lower() in PRIVATE_SUFFIXES and "/" not in rel:
            leaks.append(rel)  # loose scraped page / cover image at the root
    if leaks:
        failures.append(f"{len(leaks)} private-looking file(s) staged")

    if leaks:
        print("[stage] PRIVATE FILES IN STAGING TREE:")
        for rel in leaks[:20]:
            print(f"    {rel}")

    if failures:
        print("\n[stage] FAIL — do NOT publish:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"\n[stage] CLEAN — safe to publish from: {stage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
