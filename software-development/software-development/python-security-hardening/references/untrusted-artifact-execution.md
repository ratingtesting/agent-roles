# Untrusted-artifact execution (OWASP A08:2021)

Threat model and proof technique for installers/importers/loaders that execute code
originating from the artifact they just unpacked.

## The shape of the bug

Found in a real skill installer. Abridged:

```python
POST_INSTALL_CHECKS = [
    ("snapshot verify", 'python "{skill}/scripts/snapshot_skill.py" verify'),
    ("validate_run.py", 'python "{skill}/scripts/validate_run.py"'),
]

def run_checks(skill_dir):
    for label, tmpl in POST_INSTALL_CHECKS:
        cmd = tmpl.replace("{skill}", str(skill_dir))
        subprocess.run(cmd, shell=True, cwd=str(skill_dir))   # runs THEIR code

def import_skill(zip_path, ...):
    ...
    count = extract_skill(zf, INSTALL_TO)
    checks = run_checks(INSTALL_TO)        # ← unconditional. RCE on unpack.
```

Reading it top-down it looks responsible: there's a manifest, a SHA256 loop, a refusal
path, and the commands are "just our own verification scripts". Every one of those
reassurances is wrong once the archive is attacker-supplied.

## Why the integrity check does not help

The tempting defense is "we verify SHA256 before installing". Trace the trust chain:

```
_MANIFEST.json  ──lives inside──>  the .zip
     │
     └── contains the hashes used to validate ... the same .zip
```

The manifest is **self-attested**. An attacker edits `scripts/snapshot_skill.py`,
recomputes its SHA256, rewrites the manifest entry, and the integrity gate reports
`All 12 files verified OK`.

> Integrity proves **self-consistency**. It says the archive is internally coherent —
> not that it came from someone you trust. Only an **out-of-band** anchor establishes
> provenance: a detached signature verified against a pinned public key, or a digest
> the user fetched from a channel the attacker doesn't control.

Corollary: never let an integrity check *authorize* execution. It answers a different
question than the one being asked.

## The fix

```python
def import_skill(zip_path: Path, force: bool = False, include_internal: bool = True,
                 run_post_checks: bool = False):        # ← default OFF
    ...
    count = extract_skill(zf, INSTALL_TO)

    all_ok = True
    if run_post_checks:
        print("\n--- Post-install checks (executing code from the imported skill) ---")
        for label, ok, output in run_checks(INSTALL_TO):
            print(f"  [{'OK' if ok else 'FAIL'}] {label}: {output}")
            all_ok = all_ok and ok
    else:
        print("\n--- Post-install checks: SKIPPED ---")
        print("  These run shell commands from the imported skill, so they are opt-in.")
        print(f"  Inspect {INSTALL_TO}, then re-run with --run-checks if you trust it.")

    if not run_post_checks:
        print("  Status: installed, unverified (checks skipped — see --run-checks)")
```

And pin the invariant where the danger lives, not only at the call site:

```python
def run_checks(skill_dir: Path):
    """Run post-install verification checks.

    SECURITY: this EXECUTES code from the freshly imported skill. Never call it
    implicitly — it must stay behind the explicit --run-checks flag, because a .zip is
    untrusted input and its manifest is self-attested (an attacker who edits a script
    also recomputes its SHA256, so integrity verification does not establish trust).
    """
```

CLI surface carries the warning too, so the risk is discoverable without reading source:

```python
parser.add_argument("--run-checks", action="store_true",
                    help="Run post-install checks. WARNING: executes shell commands "
                         "from the imported skill — only for archives you trust.")
```

## Proving it — build a genuinely hostile archive

Do not assert on help text or on the presence of an `if`. Assert on **whether code ran**.
The marker file is the whole proof: if it exists after a default import, that is RCE.

```python
import hashlib, json, os, pathlib, shutil, subprocess, tempfile, zipfile

work = pathlib.Path(tempfile.mkdtemp(prefix="hermes-verify-"))
skills, marker, zpath = work / "skills", work / "PWNED.txt", work / "hostile.zip"
skills.mkdir()

files = {
    "SKILL.md": "---\nname: victim\nversion: 9.9.9\n---\n",
    # The payload. A real attacker exfiltrates; the marker is the harmless stand-in.
    "scripts/snapshot_skill.py": f"import pathlib\npathlib.Path(r'{marker}').write_text('PWNED')\nprint('OK')\n",
    "scripts/validate_run.py": "print('OK')\n",
}
with zipfile.ZipFile(zpath, "w") as zf:
    for p, c in files.items():
        zf.writestr(p, c)
    # Recompute hashes so the integrity gate PASSES — this is the point.
    zf.writestr("_MANIFEST.json", json.dumps({
        "files": len(files),
        "entries": [{"path": p, "sha256": hashlib.sha256(c.encode()).hexdigest(),
                     "size": len(c)} for p, c in files.items()]}))

def run_import(*flags):
    r = subprocess.run([sys.executable, str(IMPORTER), str(zpath), *flags],
                       capture_output=True, encoding="utf-8", errors="replace",
                       env={**os.environ, "HERMES_SKILLS": str(skills)})
    return (r.stdout or "") + (r.stderr or "")

out = run_import()
assert not marker.exists(), "RCE: archive code executed on plain unpack"
assert (skills / "victim" / "SKILL.md").is_file(), "extraction must still work"
assert "SKIPPED" in out and "--run-checks" in out, "skip must be announced"
assert "unverified" in out, "must not imply a clean bill of health"

out = run_import("--force", "--run-checks")
assert marker.exists(), "opt-in path must still work"
assert "executing code from the imported skill" in out, "must warn before running"
```

Checklist the test encodes:

| Assertion | Guards against |
|---|---|
| no marker after default import | the actual RCE |
| files still installed | fixing security by breaking the feature |
| `SKIPPED` + flag name in output | silent skip the user can't act on |
| `unverified` in status | "SUCCESS" implying checks passed when they never ran |
| marker present with `--run-checks` | over-correcting into a dead feature |
| warning printed before execution | consent after the fact |
| `--help` mentions the risk | undiscoverable danger |

## Related traps in the same family

- **`git reset --hard` during a merge silently reverts local edits.** If a hostile-archive
  fix (or any fix) is on a diverged branch, `reset --hard origin/master` discards it. Re-grep
  for the fix after the reset and before claiming it shipped.
- **Auto-discovery loaders.** `for f in plugins_dir.glob("*.py"): import_module(f.stem)` is
  the same bug without a zip. Anything dropped in the directory executes.
- **Post-install hooks** (`setup.py`, npm `postinstall`, `Makefile` targets) inherit this
  entire threat model — the package manager runs attacker code by design.
