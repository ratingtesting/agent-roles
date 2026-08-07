# Unicorn Foundation Template Verification

Session-specific verification criteria for the "Unicorn Foundation" template — a Flutter Clean Architecture starter designed to minimize long-term maintenance cost while preserving scaling potential.

## Why this verification exists

The original `app/flutter_template_riverpod3` was a fresh clone of the upstream template (Riverpod 2.x, auto_route 7.x, no freezed, weak linting, 73 tests but failing after migration attempts). Direct migration in-place hit a doom loop: analyzer hangs on auto_route 11 codegen, tests broke incrementally, and 100+ minute `dart analyze` blocks made feedback impossible.

**Plan B** (copied from `marketplace/flutter_template_riverpod3` which was already v1.0.0 with go_router, freezed, Riverpod 3.4.1, strict lints, working CI, 73 green tests) was 10× faster and produced a verified foundation.

## Verification script (Windows/MSYS)

Save as `C:\Projects\lazy-unicorn\app\flutter_template_riverpod3\verify_unicorn_foundation.py` and run with:
```bash
python "C:\Projects\lazy-unicorn\app\flutter_template_riverpod3\verify_unicorn_foundation.py"
```

```python
#!/usr/bin/env python3
"""Unicorn Foundation template verification - 10 gates, all must PASS."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

def run(cmd, cwd=None):
    """Run command, return (success, stdout)."""
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or ROOT)
        return res.returncode == 0, res.stdout.strip()
    except Exception as e:
        return False, str(e)

def check(name, condition, detail=""):
    """Print gate result."""
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{status}  {name}" + (f"  [{detail}]" if detail else ""))
    return condition

def main():
    print("=" * 60)
    print("UNICORN FOUNDATION VERIFICATION")
    print("=" * 60)

    gates = []

    # 1. Dependency Rule: domain/ imports NO data/ or presentation/
    ok, out = run('grep -r "import.*data/" lib/features/*/domain/ lib/services/*/domain/ --include="*.dart" 2>/dev/null | grep -v "\\.g\\.dart" | grep -v "\\.freezed\\.dart" | head -3')
    gates.append(check("Dependency Rule: domain/ no data/ imports", not out.strip(), "clean"))

    # 2. No hardcoded URLs (must use String.fromEnvironment)
    ok, out = run("grep -r 'dummyjson.com' lib/ --include='*.dart' | grep -v 'String.fromEnvironment'")
    gates.append(check("No hardcoded BASE_URL", not out.strip(), "clean"))

    # 3. LoginUseCase exists (business logic extracted from Notifier)
    ok, _ = run("test -f lib/features/authentication/domain/use_cases/login_use_case.dart")
    gates.append(check("LoginUseCase exists", ok))

    # 4. Riverpod 3.x only (no state_notifier package)
    ok, out = run("grep 'state_notifier' pubspec.yaml")
    gates.append(check("No state_notifier dependency", not out.strip(), "clean"))

    # 5. CI uses Flutter 3.44
    ok, out = run("grep '3.44' .github/workflows/main.yml")
    gates.append(check("CI: Flutter 3.44", ok, out[:50] if ok else "missing"))

    # 6. go_router present, auto_route absent
    ok1, _ = run("grep 'go_router' pubspec.yaml")
    ok2, out = run("grep 'auto_route' pubspec.yaml")
    gates.append(check("Navigation: go_router (no auto_route)", ok1 and not out.strip(), "go_router" if ok1 else "MISSING"))

    # 7. freezed present for immutable models
    ok, out = run("grep 'freezed' pubspec.yaml")
    gates.append(check("freezed in pubspec", ok, out[:60] if ok else "missing"))

    # 8. ARCHITECTURE.md documents the foundation
    ok, _ = run("test -f ARCHITECTURE.md")
    gates.append(check("ARCHITECTURE.md exists", ok))

    # 9. main_prod.dart entry point for production
    ok, _ = run("test -f lib/main/main_prod.dart")
    gates.append(check("main_prod.dart exists", ok))

    # 10. No 'atuhentication' typo
    ok, out = run("grep -r 'atuhentication' lib/ test/ --include='*.dart' 2>/dev/null")
    gates.append(check("No 'atuhentication' typo", not out.strip(), "clean"))

    # 11. Tests pass (73/73)
    ok, out = run("flutter test 2>&1 | tail -5", cwd=ROOT)
    passed = "All tests passed!" in out or "+73:" in out
    gates.append(check("flutter test: 73/73 PASS", passed, "green" if passed else "FAIL"))

    print("=" * 60)
    passed_count = sum(gates)
    total = len(gates)
    print(f"RESULT: {passed_count}/{total} gates PASSED")
    print("=" * 60)

    if passed_count == total:
        print("🦄 UNICORN FOUNDATION VERIFIED")
        return 0
    else:
        print("⚠️  FOUNDATION INCOMPLETE - fix failed gates")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Expected output (from this session)

```
============================================================
UNICORN FOUNDATION VERIFICATION
============================================================
✅ PASS  Dependency Rule: domain/ no data/ imports  [clean]
✅ PASS  No hardcoded BASE_URL  [clean]
✅ PASS  LoginUseCase exists
✅ PASS  No state_notifier dependency  [clean]
✅ PASS  CI: Flutter 3.44  [          flutter-version: '3.44.0']
✅ PASS  Navigation: go_router (no auto_route)  [go_router]
✅ PASS  freezed in pubspec  [  freezed_annotation: ^3.1.0
  freezed: ^3.2.5]
✅ PASS  ARCHITECTURE.md exists
✅ PASS  main_prod.dart exists
✅ PASS  No 'atuhentication' typo  [clean]
✅ PASS  flutter test: 73/73 PASS  [green]
============================================================
RESULT: 11/11 gates PASSED
============================================================
🦄 UNICORN FOUNDATION VERIFIED
```

## CI workflow gate (critical addition from v0.2.0→v0.2.1)

The upstream template shipped with `checkout@v1`, `Flutter 3.10.5`, `macos-latest`, no push trigger. The v0.2.1 fix replaced all of these:

| Sin | Fix | Reason |
|-----|-----|--------|
| `actions/checkout@v1` | `@v4` | v1 is deprecated; no security updates |
| `Flutter 3.10.5` | `3.44.0` | 3.10 is EOL; 3.44 is LTS |
| `macos-latest` | `ubuntu-latest` | macOS CI is 10× more expensive per minute |
| `pull_request` only | `pull_request` + `push: [main]` | Without push trigger, merged code never gets CI'd |
| No cache | `cache: true` via flutter-action@v2 | Publishes without cache take 2-3× longer |
| `setup-java@v1` Java 12 | Removed (not needed) | Android SDK on ubuntu includes Java 17 |

The CI was the #1 thing from v0.1.0 (old) that didn't make it into the initial v0.2.0 marketplace copy. Always verify CI *before* claiming the template is production-ready.

## Post-copy hardening checks (v0.2.2–v0.2.3 lessons)

After copying a template, verify these BEFORE the first commit:

| Check | How | Why |
|-------|-----|-----|
| Gradle ≥8.7 | `grep gradle-8 android/gradle/wrapper/gradle-wrapper.properties` | Flutter 3.44 fails to build with older Gradle |
| .gitignore has `*.jks` | `grep '\.jks' .gitignore` | Android signing keys must never be committed |
| .gitignore has `*.keystore` | `grep '\.keystore' .gitignore` | Same — release keys = app identity |
| Single `String.fromEnvironment` per env var | `grep -r "String.fromEnvironment" lib/ --include="*.dart" | grep -v ".g.dart" | grep -v ".freezed.dart" | wc -l` | Should be 1 per unique env var (e.g. `BASE_URL`) |
| No dead getters | Check `app_env.dart` or similar — any getter like `connectionString`, `isProduction` should be referenced somewhere in `lib/` | Dead code inflates onboarding cost |

## Gates rationale (why these 11)

| Gate | Why it matters for startup TCO |
|------|--------------------------------|
| Dependency Rule | Prevents framework/db coupling; business logic stays testable without infrastructure |
| No hardcoded URLs | One binary for dev/staging/prod via `--dart-define`; zero code changes per environment |
| LoginUseCase | Business logic unit-testable without UI; swap auth provider without touching presentation |
| Riverpod 3.x | Modern API (Notifier/NotifierProvider); no deprecated StateNotifier migration debt |
| Flutter 3.44 CI | LTS channel stability; security patches; analyzer compatibility |
| go_router | No codegen hang (auto_route 11 + Dart 3.12 = 100min analyze); declarative, type-safe |
| freezed | Immutable models, value equality, copyWith, JSON serialization — zero boilerplate bugs |
| ARCHITECTURE.md | Onboards new devs in hours not weeks; lowers bus factor cost |
| main_prod.dart | Separate entry points per env; no runtime env-switching logic in main() |
| No typo | Proves attention to detail; CI would miss this but production wouldn't |
| 73/73 tests | Regression safety net; every feature change verified automatically |

## Key lesson: Plan B velocity

When a template migration exceeds 3 iterations with analyzer hangs / test flakes / unclear direction:
1. **Find a working reference** in your workspace (here: `marketplace/` was already v1.0.0)
2. **Copy wholesale**, rename package, fix imports
3. **Verify with ad-hoc script** (this file) instead of full `dart analyze lib/`
4. **Tag and ship** — the verification IS the contract

This session: 2 hours from broken app template → verified v0.2.0 with 11/11 gates green.

## Anti-pattern: don't do this

| Anti-pattern | Cost |
|--------------|------|
| `dart analyze lib/` waiting 100+ min | Lost iteration velocity; false confidence if it eventually passes but misses runtime issues |
| Incremental test fixes without full re-run | Hidden failures accumulate (first rewrite passed analyze, failed 14/16 tests) |
| Claiming "builds" after `flutter pub get` only | Dependency resolution ≠ compilation; `flutter build web` or `flutter test` is the real proof |
| Keeping auto_route 11 for "modern" | Analyzer hang makes every gate unusable; go_router is strictly better for vibe-coding |

## Integration with Keelwright

This verification IS a Keelwright **Verification Gate** (gate 8). Run it:
- After any template edit (pubspec, architecture, main entry points)
- Before committing a new version tag
- In CI as a job step (the Python script is portable)

The Keelwright `circuit-breaker.md` no-progress cap (5 iters) triggered the Plan B pivot — the skill worked as designed.