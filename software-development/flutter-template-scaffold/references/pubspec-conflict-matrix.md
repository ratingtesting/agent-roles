# pubspec conflict matrix (proven on Flutter 3.44.8 / Dart 3.12.2)

## The conflict chain
A Clean-Arch Riverpod template typically pins:
- `freezed` 2.x (+ `freezed_annotation` 2.x) — needs `source_gen` + `analyzer`
- `auto_route` 7.x (+ `auto_route_generator` 7.x) — pins `source_gen ^1.2.7`
- `state_notifier_test` 0.0.10 — pins `test ^1.16.0` → transitively `analyzer <5.0.0`
- `mocktail` 0.3.0 — also `test ^1.16.0`
- `json_serializable` 6.7.1 — newer `source_gen`

These collide:
1. `freezed >=2.5.8` → `source_gen ^2.0.0`  ✗ with `auto_route_generator 7.x` (`source_gen ^1.2.7`)
2. `freezed >=2.4.2` → `analyzer >=5.13.0`  ✗ with `state_notifier_test`/`mocktail 0.3.0` (`analyzer <5.0.0` via old `test`)
3. `json_serializable >=6.7.1` → `source_gen ^1.5.0` chain also pulls newer `analyzer` ✗ with old `test`

## Proven conflict-free set (2.x line, API-compatible with Riverpod 2.x StateNotifier)
dependencies:
  auto_route: ^7.4.0
  connectivity_plus: ^4.0.1
  cupertino_icons: ^1.0.2
  dio: ^5.4.0
  equatable: ^2.0.5
  flutter_riverpod: ^2.6.0
  freezed_annotation: ^2.4.4
  json_annotation: ^4.9.0
  shared_preferences: ^2.2.0
  state_notifier: ^0.7.2+1

dev_dependencies:
  auto_route_generator: ^7.3.0
  build_runner: ^2.4.5
  flutter_lints: ^4.0.0
  freezed: ^2.5.0          # <=2.5.2 pulls source_gen 1.5.0, compatible w/ auto_route_generator 7.x
  http_mock_adapter: ^0.4.4
  json_serializable: ^6.6.2  # NOT 6.7.1+
  mocktail: ^1.0.2           # NOT 0.3.0 (old test -> analyzer<5)
  test_coverage_badge: ^0.2.0
  # state_notifier_test: REMOVED entirely

Notes:
- `freezed_annotation` latest 2.x is 2.4.4 (it jumped 2.x→3.1.0; there is no 3.0).
- `freezed` 2.5.x uses `source_gen 1.5.0` and `analyzer 6.4.1` — resolves fine with auto_route_generator 7.3.2.
- Do NOT use `freezed ^2.5.8` or `^3.x`: 2.5.8 needs source_gen 2.x (clash with auto_route 7).
- Do NOT jump to Riverpod 3.x / freezed 3.x: reference code uses `StateNotifier` (deprecated in 3.x).

## Symptom→fix quick ref
| Error during `flutter pub get` | Cause | Fix |
|---|---|---|
| `freezed ... depends on source_gen ^2.0.0 and auto_route_generator ... source_gen ^1.2.7` | freezed ≥2.5.8 | pin `freezed: ^2.5.0` |
| `state_notifier_test >=0.0.4 ... incompatible with freezed >=2.4.2` | old `test`/analyzer | remove `state_notifier_test` |
| `mocktail >=0.1.3 ... incompatible with freezed` | mocktail 0.3.0 old test | `mocktail: ^1.0.2` |
| `json_serializable >=6.7.1 ... incompatible with state_notifier_test` | json_serializable too new | `json_serializable: ^6.6.2` |
