---
name: flutter-template-scaffold
description: Flutter Riverpod scaffold; fix freezed/auto_route conflict.
license: MIT
version: "1.0.0"
author: hermes
---

# Flutter Clean Template Scaffold

Build a *working* Flutter Clean Architecture + Riverpod starter from a reference repo. The hard part is NOT copying files — it is the **pubspec dependency conflict chain** that breaks `flutter pub get` on almost any template using `freezed` + `auto_route` + `state_notifier_test`. This skill records the exact conflict matrix and the fix proven to build on Flutter 3.44 / Dart 3.12.

## When to use
- "Create a template from <flutter clean architecture repo>"
- Starting a new isolated Flutter project (Telegram Mini App, marketplace, etc.)
- `flutter pub get` fails with "version solving failed" mentioning freezed / auto_route / source_gen / analyzer / state_notifier_test.

## Workflow
1. **Scaffold in place, not in a temp sibling.** Copy straight into the target project dir (e.g. `C:\Projects\lazy-unicorn\app\`). Do NOT clone to a parallel `flutter-clean-template` folder and then `cp` it over — that wastes a round trip and risks diverging from the project's existing `AGENTS.md`/config. Respect per-project isolation; keep the destination's `AGENTS.md`.
2. **Fetch the reference repo honestly.** `git clone --depth 1 <url> /tmp/src`, then read `pubspec.yaml`, `README.md`, `folder_structure.md` to learn the real architecture and *current* versions. Do NOT guess versions.
3. **Copy, excluding junk:** `.git`, `.dart_tool`, `coverage`, `.DS_Store`, `pubspec.lock`. On Windows git-bash `rsync` is absent → use `cp -r` then `find ... -delete` (see references/windows-flutter-gotchas.md).
4. **Rename the package everywhere:**
   - Dart imports `flutter_project` → `<pkg>` (e.g. `app`)
   - `pubspec.yaml` `name:`
   - Android `applicationId` `com.example.flutter_project` → `com.<org>.<pkg>`
   - physically move `android/.../kotlin/com/example/flutter_project/` → `com/<org>/<pkg>/`
   - iOS `Info.plist` `<string>flutter_project</string>` and `project.pbxproj` `com.example.flutterProject`
   - Verify with `grep -rn` that zero old names remain.
5. **Pin a conflict-free pubspec** (see references/pubspec-conflict-matrix.md). Critical moves:
   - DROP `state_notifier_test` entirely (root of the analyzer conflict).
   - `freezed: ^2.5.0` (NOT 2.5.8+ — that pulls source_gen 2.x, clashing with auto_route_generator 7.x).
   - `json_serializable: ^6.6.2` (NOT 6.7.1+).
   - `mocktail: ^1.0.2` (NOT 0.3.0).
6. **Rewrite the tests that used `stateNotifierTest`.** See references/state-notifier-test-rewrite.md — replace with a `recordStates` helper built on `StateNotifier.addListener`. Also delete the boilerplate `test/widget_test.dart` that `flutter create` adds (it references a nonexistent `MyApp`).
7. **Run codegen:** `flutter pub run build_runner build --delete-conflicting-outputs`.
8. **Verify for real (never claim success without this):**
   - `flutter analyze` → must show **0 errors** (info/warning about `use_super_parameters` / deprecated `background` are OK on fresh Flutter).
   - `flutter test` on the rewritten test files → all green.
   - If **Android SDK is missing** (common on this Windows host), enable web and compile-proof instead: `flutter create . --platforms web` then `flutter build web --release`. A successful web build proves the entire Dart tree compiles to a binary.

## Riverpod 2.x → 3.x migration (proven to build)

The "stay on 2.x" advice is the SAFE default, but Riverpod 3 + freezed 3 IS achievable and is the right call when the user explicitly asks for "the latest version." Confirmed building on Flutter 3.44 / Dart 3.12 with: `flutter_riverpod ^3.4.1`, `freezed ^3.2.5`, `freezed_annotation ^3.1.0`, `go_router ^16.3.0` (NOT auto_route — see ⚠️ below).

**Migration steps (mechanical, per file):**
1. `class X extends StateNotifier<S>` → `class X extends Notifier<S>`; delete the constructor that took repos; add `@override S build() => const S.initial();`; get deps via `late final _repo = ref.read(repoProvider);` inside `build()`.
2. `StateNotifierProvider<X, S>(X.new)` → `NotifierProvider<X, S>(X.new)`.
3. `class T extends ChangeNotifier` (e.g. theme) → `class T extends Notifier<ThemeMode> { @override ThemeMode build() => ThemeMode.light; void toggle() => state = ...; }` and `ChangeNotifierProvider` → `NotifierProvider`. Update call sites that read `.value`/`.mode` to use the notifier `state` directly.
4. `stateNotifierTest` (from `mocktail`) does NOT compile under Riverpod 3 (it needs the removed `StateNotifier`). Rewrite tests with `test()` + a `recordStates` helper on `Notifier.addListener`, OR drop `state_notifier_test` and rewrite as in `references/state-notifier-test-rewrite.md`.
5. `WidgetsFlutterBinding.instance.ensureInitialized()` → `WidgetsFlutterBinding.ensureInitialized();` (no `.instance`).

⚠️ **auto_route vs go_router:** if the reference uses `auto_route`, AVOID upgrading to `auto_route ^11` — its codegen makes `dart analyze lib/` (and occasionally `flutter build`) HANG for 100+ minutes on Dart 3.12 (analyzer chokes on the generated `*.gr.dart`). Either stay on `auto_route ^7` OR **swap to `go_router`** (the path this session took: `pubspec` + routes file rewritten to `GoRoute`/`ShellRoute`). go_router has no codegen, so `analyze`/`build` finish in seconds-to-minutes.

## Unicorn-foundation hardening (when the template is a startup's base)

For a template meant to scale to a funded startup, keep it a **modular monolith** and harden the boundaries that are expensive to retrofit:
- **Secrets/endpoints out of source.** Use one source of truth for `String.fromEnvironment('BASE_URL')`. Development may use an explicit local value, but production must fail fast when a required define is absent; never hide a missing production endpoint behind a plausible `api.example.com` fallback.
- **Use cases layer.** Pull business orchestration out of `Notifier` into `domain/use_cases/<name>_use_case.dart`. Parsing JSON and mapping DTOs to domain entities stay in `data`; presentation only invokes use cases and maps results to UI state.
- **Domain-neutral failures.** Domain code must not import an HTTP/Dio-named exception. Define a neutral `Failure`/result contract inward and translate transport exceptions in the data adapter.
- **Production-safe observers.** Do not attach a verbose `ProviderObserver` in production unless values are redacted. Provider state may contain tokens, credentials, or personal data.
- **Android identity consistency.** Rename `applicationId`, `namespace`, manifest package/label, Kotlin package declaration, and the physical `MainActivity` path together. Search for the old package and placeholder app title afterward.
- **Release signing is explicit.** A production workflow must never silently sign with the debug key. Use a documented release signing setup or fail fast until credentials are configured.
- **`ARCHITECTURE.md`** at repo root: boundaries, Dependency Rule, bootstrap/rename procedure, environment contract, Definition of Done, and verified platform status.
- **Strict CI:** pin one Flutter version consistently, then run format, generated-code drift check, architecture import check, analyze, tests+coverage, and an Android debug APK build. A release AAB belongs in a separate release workflow.
- **Generated/coverage policy.** Choose one generated-code policy and enforce it. For an application template, committing generated Dart and checking for post-codegen diff is usually cheaper than requiring every consumer to regenerate blindly. Ignore `coverage/`; publish reports as CI artifacts.
- **Stronger `analysis_options.yaml`:** enable `avoid_print`, `avoid_dynamic_calls`, `unawaited_futures`, `always_declare_return_types`, `sort_pub_dependencies`, `prefer_const_constructors`.
- Drop stale dependencies and resist speculative enterprise layers, generic base use cases, and microservices until concrete product pressure appears.

## Golden version set (proven to build & pass 73/73 tests)

The following versions were proven on **Flutter 3.44.8 / Dart 3.12 / Windows 11 (git-bash)**:

```yaml
dependencies:
  connectivity_plus: ^7.3.1
  dio: ^5.4.0
  equatable: ^2.0.5          # optional; freezed covers this
  flutter_riverpod: ^3.4.2    # not 2.x
  go_router: ^16.3.0          # NOT auto_route — see ⚠️ below
  freezed_annotation: ^3.1.0
  json_annotation: ^4.9.0
  shared_preferences: ^2.2.0

dev_dependencies:
  build_runner: ^2.4.5
  flutter_lints: ^6.0.0
  freezed: ^3.2.5
  http_mock_adapter: ^0.6.1
  json_serializable: ^6.9.0
  mocktail: ^1.0.2
  test_coverage_badge: ^0.3.2
```

Add `flutter_lints: ^6.0.0` when you want strict analysis_options.yaml (see below).

## Plan B: when to copy a known-good template (not incremental migrate)

When a template migration exceeds 3 iterations with analyzer hangs / test flakes / unclear direction:

1. **Find a working reference** in your workspace (another isolated project that's already on the target stack)
2. **Copy wholesale** (`cp -r`), exclude `.git`/`.dart_tool`/`coverage`/`pubspec.lock`
3. **Rename package** in pubspec.yaml + all Dart imports (`grep -rl old_package lib/ test/ | xargs sed -i 's/old/new/g'`)
4. **Fix any stale imports** that weren't caught
5. **Run `flutter test`** — if it passes, you're done in hours instead of days
6. **Run the unicorn foundation verification** (`references/unicorn-foundation-verification.md`)

This session's pivot took 2 hours from broken app template → verified v0.2.0 with 11/11 gates green. The incremental approach was on track for 5+ hours with no green tests.

## Pitfalls
- **Respect project/profile isolation even when a working reference exists.** Never inspect or copy from a sibling project/profile unless the user explicitly authorizes it. Prefer a tag/history from the same isolated Git repo or generate a temporary reference with the installed `flutter create`. If the user switches from “fix it” to “describe only,” stop edits immediately and leave a compact handoff/PROGRESS note.
- **Separate JDK presence from Android toolchain readiness.** Verify both `java -version` and `flutter doctor -v`. JDK 17 being installed does not prove that the required Android platform/build-tools are present. Do not install missing SDK components without consent.
- **Never claim Android readiness from Dart tests.** `flutter test` proves Dart behavior; it does not validate Gradle, AGP/Kotlin compatibility, manifests, package paths, signing, or SDK components. Require a fresh `flutter build apk --debug --dart-define=BASE_URL=...` exit 0, and add the same build gate to CI.
- **Generated Flutter references may use different filenames.** After `flutter create`, inspect the actual generated tree before reading assumed paths such as `settings.gradle.kts`; do not infer Kotlin DSL versus Groovy DSL.
- **Do not commit verification artifacts.** Keep `coverage/lcov.info`, local Gradle caches, temporary reference trees, and `local.properties` out of Git. Use OS temp paths with a `hermes-verify-` prefix and clean them after inspection.
- **NEVER claim the template "builds" on `flutter pub get` + `build_runner` alone.** `pub get` only resolves deps; `analyze` only type-checks. A real platform build is required for a platform-readiness claim. If Android cannot build, report the exact `flutter doctor -v` or build blocker; a web build may prove Dart compilation but not Android readiness.
- **Gradle version mismatch after copying from marketplace/upstream.** Copied templates often ship with Gradle 8.3 or older. Flutter 3.44+ requires Gradle ≥8.7. Always check `android/gradle/wrapper/gradle-wrapper.properties` → `distributionUrl=https\\://services.gradle.org/distributions/gradle-8.7-all.zip`. Without this fix, `flutter build apk` fails with "Gradle version is lower than Flutter's minimum supported version."
- **Dead code in copied templates: duplicate env vars.** Marketplace/upstream templates sometimes define `BASE_URL` in TWO places (e.g. `app_configs.dart` + `app_env.dart`). After copying, grep for `String.fromEnvironment` across all `lib/` files — there should be exactly ONE source of truth per env var. Remove the duplicate and its unused getters (`connectionString`, `isProduction` if never referenced).
- **Missing `.jks`/`.keystore` in .gitignore.** Copied templates rarely include Android signing key patterns. Add `*.jks` and `*.keystore` to `.gitignore` immediately — these are the release signing keys, and accidental commits would leak your app's signing identity.
- **Stale CI from marketplace/upstream.** Marketplace templates often ship with `checkout@v1`, `Flutter 3.10.5`, `macos-latest`, or missing `push:` trigger. ALWAYS replace the entire `.github/workflows/main.yml` with a modern workflow (checkout@v4, Flutter 3.44, ubuntu-latest, push+pull_request, cache:true). This is the #1 thing that doesn't transfer when copying a known-good template.
- **Default is 2.x; 3.x only on explicit request.** Stay on 2.x unless the user asks for the latest. If they do, follow the Riverpod 3 migration above — it builds, but mind the auto_route hang trap.
- **`dart analyze lib/` can HANG (100+ min) on projects with auto_route 11 codegen.** Do NOT poll it in a loop (see Conduct below). Verify instead via `flutter build web` (proves compilation in 2-4 min) or per-folder `dart analyze lib/features/authentication/` (each finishes in ~160s). The hang is an analyzer/typesystem issue with the generated file, NOT a code error — a clean `build web` is sufficient proof.
- **`state_notifier_test` is unmaintained** (max 0.0.10, `test ^1.16.0` → `analyzer <5.0.0`) and fundamentally incompatible with any `freezed >=2.4.2` (`analyzer >=5.13`). Remove it; do not try to upgrade it.
- **Ad-hoc verify after edits:** after ANY test/pubspec edit, re-run `flutter analyze` + `flutter test` on the changed files before reporting done. A "fix" that isn't re-run can leave hidden failures (the first test rewrite passed `analyze` but failed 14/16 tests until the `recordStates` initial-emit skip was added).
- **Complex one-liner `grep -rl ... | wc -l` commands get BLOCKED by the command parser** on this host — split into simpler terminal calls or use `awk`.
- **`flutter analyze lib/` exit code differs with stdout redirect.** When stdout is redirected (e.g. `> /dev/null 2>&1`), `flutter analyze lib/` exits 1 even though it exits 0 in the terminal. This is a terminal-detection quirk — always run analyze without redirect or check the terminal output.
- **`sed -i` on Windows/MSYS touches ALL files** even when the pattern doesn't match, because `sed -i` rewrites every file it operates on. Use `grep -rl pattern files | xargs sed -i 's/old/new/g'` instead of `find ... -exec sed ... +` to only touch matching files.
- **ProviderObserver must be guarded with `kDebugMode`.** A logger that serializes provider state into logs is a production security risk (tokens, credentials, personal data). Always wrap `didUpdateProvider`/`didDisposeProvider` body with `if (kDebugMode) { ... }` and import `package:flutter/foundation.dart` for the constant.
- **Not every architectural improvement belongs in a startup template.** The user may push back on changes that increase initial complexity. Distinguish P0 (buildability, security, CI) from P1 (architecture purity, domain abstractions) and defer P2. When in doubt, ask: "Does this block the app from compiling or running safely?" If not, it's probably P1 or P2.
- **Ad-hoc verify after edits:** after ANY test/pubspec edit, re-run `flutter analyze` + `flutter test` on the changed files before reporting done. A "fix" that isn't re-run can leave hidden failures (the first test rewrite passed `analyze` but failed 14/16 tests until the `recordStates` initial-emit skip was added).
- **Complex one-liner `grep -rl ... | wc -l` commands get BLOCKED by the command parser** on this host — split into simpler terminal calls or use `awk`.

## References
- `references/pubspec-conflict-matrix.md` — exact proven version set + the conflict chain explained.
- `references/state-notifier-test-rewrite.md` — drop-in `recordStates` helper + per-test shape + gotchas.
- `references/windows-flutter-gotchas.md` — Windows git-bash quirks and environment setup checks.
- `references/unicorn-foundation-verification.md` — legacy focused verification gates.
- `references/unicorn-foundation-audit.md` — production-readiness checklist covering architecture, security, Android identity/build, reproducibility, and evidence.
