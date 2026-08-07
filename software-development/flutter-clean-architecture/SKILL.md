---
name: flutter-clean-architecture
description: 'Flutter Clean Architecture patterns.'
license: MIT
metadata:
  author: emelya-agent
  version: "1.0.0"
---

# Flutter Clean Architecture Patterns

Concrete patterns for Flutter/Dart projects following Clean Architecture. Based on the `app_foundation` template (Riverpod 3 + Clean Architecture).

## Core Flutter Violations (Fix These First)

### 1. Domain Models with JSON/Password

**Problem:** Domain models contain `toJson()`/`fromJson()`/`password`/`token`.

**Fix pattern:**
```dart
// ❌ WRONG: Domain model with JSON and password
class User extends Equatable {
  final String password; // NO!
  Map<String, dynamic> toJson() => {...}; // NO!
}

// ✅ CORRECT: Pure domain model
class User extends Equatable {
  final int id;
  final String username;
  // No password, no token, no toJson
  @override
  List<Object?> get props => [id, username, ...];
}
```

### 2. DTO Pattern for Data Layer

**Create DTOs in `lib/shared/data/dto/`:**

```dart
// credentials.dart — for login requests
class Credentials {
  final String username;
  final String password;
  Map<String, dynamic> toJson() => {'username': username, 'password': password};
}

// user_dto.dart — for API responses
class UserDto {
  final int id;
  final String username;
  final String token; // token stays in DTO, not domain
  
  factory UserDto.fromJson(Map<String, dynamic> json) => ...;
  
  // Convert to domain (without token)
  User toDomain() => User(id: id, username: username, ...);
  
  // Token for secure storage
  String get accessToken => token;
}
```

### 3. Data Source Uses DTOs

```dart
// auth_remote_data_source.dart
Future<Either<AppException, User>> loginUser({
  required Credentials credentials, // DTO, not domain
}) async {
  final response = await networkService.post(
    '/auth/login',
    data: credentials.toJson(), // DTO handles JSON
  );
  final userDto = UserDto.fromJson(response.data);
  return Right(userDto.toDomain()); // Return domain model
}
```

### 4. Secure Storage for Tokens

**Problem:** Tokens stored in `SharedPreferences` with password.

**Fix:** `flutter_secure_storage` for tokens, `SharedPreferences` only for non-sensitive user data.

```dart
// user_local_datasource.dart
Future<bool> saveUser({required User user, required String token}) async {
  final userDto = UserDto(
    id: user.id,
    username: user.username,
    token: token, // Token goes to secure storage, not domain
  );
  // Save domain fields to SharedPreferences
  // Save token to flutter_secure_storage
}
```

## Use Case Pattern

**Location:** `lib/features/<feature>/domain/usecases/`

```dart
// fetch_products_use_case.dart
class FetchProductsUseCase {
  final DashboardRepository repository;
  
  FetchProductsUseCase(this.repository);
  
  Future<Either<Failure, List<Product>>> call({
    int page = 1,
    String? query,
  }) async {
    return repository.fetchProducts(page: page, query: query);
  }
}
```

**Rules:**
- Framework-free (no Flutter imports)
- Return `Either<Failure, T>`
- Single responsibility
- Testable without Flutter

## Composition Root (DI)

**Problem:** 5+ separate Provider files scattered across features.

**Fix:** Single `lib/core/di/injector.dart`:

```dart
// injector.dart
final loginUseCaseProvider = Provider<LoginUseCase>((ref) {
  return LoginUseCase(ref.watch(authRepositoryProvider));
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(ref.watch(networkServiceProvider));
});
```

## Testing Patterns

### Domain Model Tests
```dart
// test/features/authentication/domain/models/user_test.dart
test('Should support value equality', () {
  const user1 = User(id: 1, username: 'test');
  const user2 = User(id: 1, username: 'test');
  expect(user1, equals(user2)); // Equatable
});
// NO JSON tests for domain models!
```

### Use Case Tests
```dart
test('Should return products on success', () async {
  when(() => mockRepository.fetchProducts())
      .thenAnswer((_) async => Right([product1, product2]));
  
  final result = await fetchProductsUseCase();
  
  expect(result.isRight(), true);
});
```

## Quick Diagnostic for Flutter Projects

| Question | If No | Action |
|----------|-------|--------|
| Do domain models have `toJson`/`fromJson`? | JSON in domain | Move to DTOs in data layer |
| Do domain models have `password`/`token`? | Sensitive data in domain | Create `Credentials` DTO, use secure storage |
| Is business logic in Notifier/Bloc? | Logic in presentation | Extract Use Cases |
| Are there 5+ Provider files? | DI scattered | Create single `injector.dart` |
| Are tokens in `SharedPreferences`? | Insecure storage | Use `flutter_secure_storage` |
| Can you test Use Cases without Flutter? | Use Cases import Flutter | Remove Flutter imports from domain |

## Common Flutter Mistakes

| Mistake | Fix |
|---------|-----|
| `User` model with `password` field | Remove `password`, create `Credentials` DTO |
| Business logic in `DashboardNotifier` | Extract Use Cases |
| `print()` for logging | Structured logger with correlation IDs |
| No `flutter_secure_storage` | Add for tokens |
| Direct `Dio` in presentation | Use repository interface + DI |

## References

- See [templates/flutter_domain_model.dart](templates/flutter_domain_model.dart) for a clean domain model template
- See [templates/flutter_dto.dart](templates/flutter_dto.dart) for DTO template
- See [templates/flutter_use_case.dart](templates/flutter_use_case.dart) for Use Case template
