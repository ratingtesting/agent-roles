# Rewriting stateNotifierTest without the `state_notifier_test` package

`state_notifier_test` is removed (incompatible with freezed 2.x). Replace each
`stateNotifierTest<Notifier, State>(...)` block with a plain `test(...)` that
records emitted states via `StateNotifier.addListener`.

## Drop-in helper (copy into the test file)
```dart
import 'package:state_notifier/state_notifier.dart';

/// Mirrors stateNotifierTest: records every emission after subscription,
/// skipping the immediate initial-state emit that Riverpod's addListener fires.
List<T> recordStates<T>(StateNotifier<T> notifier) {
  final history = <T>[];
  final initial = notifier.state;
  notifier.addListener((state) {
    if (history.isEmpty && state == initial) return;
    history.add(state);
  });
  return history;
}
```

## Per-test shape
```dart
test('emits [loading, success] on success', () async {
  when(() => repo.fetch(any())).thenAnswer((_) async => Right(...));
  final n = MyNotifier(repo);
  final h = recordStates(n);
  await n.fetch();
  expect(h, const [MyState.loading(), MyState.success()]);
});
```
- Create a FRESH notifier inside each `test` (don't reuse a `setUpAll` instance
  whose state is already dirty from a prior test).
- For fire-and-forget calls without `await` (e.g. "called while loading"),
  flush microtasks first: `n.fetch(); n.fetch(); await Future.delayed(Duration.zero);`

## Gotcha that broke the first rewrite (14/16 failed)
Riverpod 2.x `StateNotifier.addListener` fires IMMEDIATELY with the current
state on subscription. Without the `if (history.isEmpty && state == initial) return;`
skip, `history[0]` is the `initial` state, so every `expect` that starts with
`loading` fails with `location [0] is <initial> instead of <loading>`. The skip
reproduces `stateNotifierTest`'s own behaviour.

## Also
- Delete `test/widget_test.dart` if `flutter create` generated it — it asserts
  `MyApp` exists (the template's root widget is named differently, e.g. `App`).
- `notifier.state` access in tests triggers `invalid_use_of_protected_member`;
  silence with `// ignore: invalid_use_of_protected_member` (kept as warning,
  not an error).
