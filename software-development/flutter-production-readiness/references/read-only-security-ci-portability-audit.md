# Read-only Flutter template audit: clean-checkout protocol

Use this recipe when auditing security, CI reproducibility, and template portability without changing the repository.

## Clean-checkout reproduction

Local success can depend on ignored generated files. Reproduce GitHub Actions from tracked content only:

```bash
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git archive HEAD | tar -x -C "$tmp"
cd "$tmp"
flutter pub get

dart format --output=none --set-exit-if-changed .
flutter analyze lib/
flutter test --coverage
flutter build apk --debug --dart-define=BASE_URL=https://dev.api.example.invalid
```

Run failed stages separately after the first failure so formatting does not mask analyze, test, codegen, or build failures. Record each exit code and test pass/fail count.

## Generated-source consistency

Check both sides of the contract:

```bash
git ls-files '*.g.dart' '*.freezed.dart'
git grep -n -E '^part .*(freezed|g)\.dart' -- '*.dart'
git status --ignored --short | grep -E '\.(g|freezed)\.dart$'
```

If source files use `part` but generated files are ignored/untracked, CI must run `dart run build_runner build --delete-conflicting-outputs` before format/analyze/test. Otherwise a developer machine can pass only because stale ignored artifacts exist.

## Security checks

- A networked Android app needs `android.permission.INTERNET` in the main manifest; debug/profile-only permission produces a non-networking release.
- `--dart-define` protects values from source control, not from extraction from client binaries. Treat endpoints and feature flags as public configuration; never document client-side defines as safe storage for backend secrets.
- Do not serialize credentials into a general `User` model. Separate login request, authenticated profile, and session token. Store session material in platform secure storage, never ordinary SharedPreferences.
- Even debug HTTP logging should redact password, token, authorization, cookies, and response bodies that may contain session data.
- Run `gitleaks detect --source . --no-banner --redact -v`. JWT-shaped test fixtures can make the gate permanently red; replace them with obviously fake non-secret sentinels or add a narrowly justified allowlist.

## CI and portability checks

- Compare the workflow push branch with `git branch --show-current` and repository policy (`main` versus `master`).
- For Flutter applications, track `pubspec.lock`; broad `*.lock` ignores undermine reproducibility.
- Verify Android wrapper bootstrap files are tracked where standalone Gradle reproducibility is expected.
- Exercise release configuration, not only debug APK, while keeping release signing fail-fast rather than falling back to debug keys.
- Audit rename surfaces across Dart package imports, Android namespace/application ID/Kotlin path, iOS bundle ID/team, app labels, and Web manifest/title.
- Check README version, package version, Git tags, dependency tables, claimed test counts, license links, and actual tracked files against one another.

## Read-only closure

Before reporting, run `git status --short`, `git diff --stat`, and `git diff --cached --stat`. Distinguish pre-existing untracked or modified files from audit effects. Findings should lead, ordered by severity, with concrete file/line references and actual command evidence.
