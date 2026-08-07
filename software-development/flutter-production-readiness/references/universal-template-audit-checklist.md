# Universal Flutter Template Audit Checklist

Use for a read-only audit of a reusable startup foundation. Run in a tracked-only temporary checkout whenever possible.

## Evidence table

Record command, exit code, and key output separately:

| Gate | Command | Required evidence |
|---|---|---|
| Format | `dart format --output=none --set-exit-if-changed .` | exit 0, zero changed files |
| Analyze | `flutter analyze lib/` | exit 0, do not reinterpret info findings as green |
| Tests | `flutter test --coverage` | exit 0, exact pass/fail count |
| Coverage | parse `coverage/lcov.info` | LH/LF and production files absent from LCOV |
| Android advice | `flutter analyze --suggestions` | compatible AGP/KGP/JDK/Gradle |
| Android build | `flutter build apk --debug --dart-define=BASE_URL=https://dev.api.example.invalid` | exit 0 |
| Web build | `flutter build web --dart-define=BASE_URL=https://dev.api.example.invalid` | exit 0 |
| Environment | `flutter doctor -v` | separate SDK setup gaps from project config defects |

A YAML job is an intention, not evidence. A platform folder is not build support.

## Clean Architecture score (7 checks)

Award a row only when code evidence supports it:

1. Business rules test without UI, network, or storage.
2. Domain imports no data/presentation/framework/infrastructure exception types.
3. Persistence can be swapped behind domain-owned repository contracts.
4. Use cases expose typed domain request/response models, not JSON/transport response objects.
5. Flutter/Riverpod/Dio/SharedPreferences are confined to outer layers.
6. Internal package dependency graph is cycle-free.
7. Composition root/providers wire concrete implementations outside domain.

Folder names do not earn points. Map 6–7 passes to 9–10, 4–5 to 6–8, 2–3 to 3–5, 0–1 to 0–2.

## Security audit

- Separate login credentials, profile, and session token.
- Password is never part of cached user JSON, equality, logs, or persisted state.
- Token uses platform secure storage, not SharedPreferences.
- HTTP and provider logs redact password/token/Authorization/Cookie and auth response bodies, including debug builds.
- Client `--dart-define` values are documented as public configuration, never backend secrets.
- No realistic prefilled credentials in production UI.
- Release signing does not silently use debug keys.
- Run history-aware secret scanning with test fixtures designed not to permanently trip the gate.

## Portability audit

Scan all rename surfaces:

- `pubspec.yaml` package/version/assets
- Dart `package:` imports
- Android namespace, application ID, Manifest labels, Kotlin path/package
- iOS bundle identifiers, display name, schemes
- Web title, PWA manifest, descriptions
- CI commands, docs, generated/ephemeral absolute paths

Require one bootstrap/rename workflow and a post-run placeholder scan. Do not bundle `test/` as production assets.

## Reproducibility and cost

- Exact Flutter/toolchain policy; app lockfile tracked.
- Generated-code policy works in a clean checkout.
- Unused direct dependencies are removed.
- CI covers every claimed platform or documentation narrows the claim.
- README, architecture document, tag, package version, dependency versions, test count, and platform matrix agree.
- Include dependency update automation, secret scan, license, and Definition of Done when the template is distributed.

## Handoff format

Write concise sections:

1. **Fresh evidence** — command results and blockers.
2. **Verdict** — production-ready yes/no and architecture score.
3. **P0** — credential safety, broken builds, lying CI/docs.
4. **P1** — boundary corrections and reproducibility.
5. **P2** — documentation and maintenance automation.
6. **Termination conditions** — exact gates that define done.
7. **Audit integrity** — `git status`, source diff empty, only approved handoff file written.

Do not implement findings when the user assigned fixes to another model.
