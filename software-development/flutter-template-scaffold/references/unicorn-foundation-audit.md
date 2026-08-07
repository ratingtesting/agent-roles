# Unicorn Foundation Audit Checklist

Use after dependency resolution and before calling a Flutter startup template production-ready.

## Prioritization — not every improvement belongs in a template

| Priority | When to fix | Examples |
|----------|------------|----------|
| **P0 — Critical** | Fix before any real feature work | Android builds, CI, env config, release signing safety |
| **P1 — Important** | Fix early but not blocking | Business logic in wrong layer, neutral domain failures |
| **P2 — Defer** | Wait until project is live | Abstract base classes, umbrella use cases |
| **Over-engineering** | Resist until concrete pressure | Microservices, generic base UseCase, mega-core layers |

## Architecture

- Feature-first modular monolith; no speculative microservices.
- Domain imports no Flutter, Riverpod, Dio, JSON DTOs, or transport-named exceptions.
- Repository contracts and use cases live inward; data implements contracts and maps DTOs.
- Notifiers remain thin state adapters; pagination/search/login orchestration lives in use cases.
- Dependency graph is cycle-free; composition happens at the application edge.

## Configuration and security

- One source of truth per build-time variable (grep for `String.fromEnvironment` across entire lib/).
- **No `defaultValue` for production-required env vars** — either fail-fast (compile error) or use a clearly-fake placeholder that cannot accidentally ship.
- `ProviderObserver` (or equivalent) guards state logging with `kDebugMode` — provider state may contain tokens/credentials.
- Production observers/loggers redact values or are disabled.
- `.env`, `*.jks`, `*.keystore`, Firebase files, local properties, Gradle caches, coverage, and build output are ignored.
- Release builds never silently use debug signing (`signingConfigs.debug` in release block). Default: `signingConfig = null`.
- Secret/dependency scanning is automated in CI.

## Android identity and build

- `applicationId`, `namespace`, manifest package, Kotlin package declaration, physical `MainActivity.kt` path, and app label are **all consistent** (grep for `com.example`, `flutter_project`, `flutter_template`, and placeholder labels like `Pokemon App`).
- `compileOptions`: `JavaVersion.VERSION_17` (not VERSION_1_8), `kotlinOptions.jvmTarget = '17'`.
- `gradle-wrapper.properties`: Gradle >= 8.7 (Flutter 3.44+ requires ≥8.7).
- Check `java -version` AND `flutter doctor -v`; JDK readiness and Android SDK readiness are separate gates.
- Run a real debug APK build with representative `--dart-define` values.
- CI repeats the Android debug APK build; release AAB is a separate controlled workflow.

## CI/CD

- `checkout@v4`, `ubuntu-latest`, cache enabled, push + pull_request triggers.
- Flutter version pinned consistently in local tooling, CI, and documentation.
- Separate job(s): format check, analyze, test+coverage, (optional) Android debug APK.
- Android APK build supplies `--dart-define=BASE_URL=…`.

## Reproducibility

- Flutter version is pinned consistently in local tooling, CI, and documentation.
- Generated-code policy is explicit and machine checked.
- Coverage baseline is explicit; reports are CI artifacts, not committed files (`coverage/` in .gitignore).
- Bootstrap/rename procedure removes every placeholder identifier and title.
- Architecture import checks and generated-drift checks are scripts, not reviewer memory.

## Placeholder cleanup — search for these

| Pattern | Where | Example failure |
|---------|-------|----------------|
| `com.example.*` | android/ gradle + manifest + MainActivity | Old template package never renamed |
| `Pokemon App` | AndroidManifest.xml label | Copied from upstream template |
| `Flutter TDD` / `Q Flutter TDD` | lib/main/app.dart, lib/main/app_env.dart | Remnant from marketplace copy |
| `flutter_project` | android/ paths or package decls | Kotlin package mismatch |
| `api.example.com` | String.fromEnvironment defaultValue | Silent broken production build |
| `Flutter CI` | CI workflow name | Generic placeholder |

## Evidence required before completion

1. `flutter analyze lib/` exits 0.
2. `flutter test --coverage` exits 0 with expected count and baseline.
3. `flutter build apk --debug --dart-define=BASE_URL=<url>` exits 0.
4. Architecture and security scripts pass.
5. `git status --short` contains no unintended artifacts.
6. Documentation describes only verified platform status.

Do not substitute Dart tests or a web build for Android build evidence. When a required SDK component is missing, report the exact blocker and request consent before installation.
