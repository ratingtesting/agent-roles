# Clean-Architecture Verification Pattern

## Problem

After building a clean-architecture app (entities → repositories → use-cases → adapters → delivery), you need to prove:
1. The Dependency Rule holds — inner layers never import outer layers.
2. Endpoints behave correctly (existing user → 200 + JSON, missing user → 404).

This is a specialized case of ad-hoc verification where the "behavior" is structural (dependency direction) plus runtime (endpoint responses).

## Technique

Create a temp verification script under the OS temp dir. The script should:

1. **Import all layers** — catches circular imports and wrong dependency direction at import time.
2. **AST-based import analysis** — parse each inner-circle file and verify it does not import from outer-circle packages. This is a static check that doesn't require executing the code.
3. **Flask test client** — build the app via the composition root and test endpoints without starting a real server.

## Script template

```python
import os, sys, tempfile, ast

TREATMENT_DIR = r"C:\path\to\project"
sys.path.insert(0, TREATMENT_DIR)

tmp_dir = tempfile.mkdtemp(prefix="hermes-verify-")
db_path = os.path.join(tmp_dir, "test_users.db")
os.environ["USER_DB_PATH"] = db_path  # inject temp DB

# 1. Import all layers (catches circular imports)
from app.entities.user import User
from app.repositories.user_repository import UserRepository
from app.use_cases.get_user import GetUserUseCase
from app.adapters.sqlite_user_repository import SqliteUserRepository
from app.delivery.flask_app import create_app

# 2. AST-based dependency rule check
def get_imports(filepath):
    with open(filepath, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports

# Verify inner layers don't import outer layers
for layer_file in ["app/entities/user.py", "app/repositories/user_repository.py", "app/use_cases/get_user.py"]:
    imports = get_imports(os.path.join(TREATMENT_DIR, layer_file))
    outer = {i for i in imports if i.startswith("app.adapters") or i.startswith("app.delivery")}
    assert not outer, f"{layer_file} imports outer layer: {outer}"

# 3. Flask test client
repo = SqliteUserRepository(db_path=db_path)
uc = GetUserUseCase(user_repository=repo)
app = create_app(user_use_case=uc)
client = app.test_client()

resp = client.get("/user/1")
assert resp.status_code == 200
assert resp.get_json()["name"] == "Alice"

resp404 = client.get("/user/999")
assert resp404.status_code == 404
assert resp404.get_json()["error"] == "User not found"

# Cleanup
os.remove(db_path)
os.rmdir(tmp_dir)
print("All verification checks passed.")
```

## Why This Works

- **No server needed** — Flask's `test_client()` simulates HTTP requests in-process, so there's no port conflict or startup delay.
- **Temp DB isolation** — each run gets a fresh SQLite database, so tests are deterministic and don't clobber real data.
- **AST analysis** — statically verifies the Dependency Rule without executing the code, catching violations that runtime tests might miss.
- **Temp file cleanup** — the script removes its temp DB and directory after running, leaving no artifacts behind.

## When to Use This

When the project follows clean-architecture layering and you need to verify:
- Inner layers don't import outer layers (Dependency Rule).
- The composition root correctly wires dependencies.
- Endpoints return the right status codes and JSON payloads.

## See Also

- `windows-msys-shell` — for native path handling and the `-c` flag approval gate workaround.
- `references/approval-guard-triggers.md` — when the temp script stalls on `pending_approval`.
