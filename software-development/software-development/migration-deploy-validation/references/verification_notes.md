# Key techniques observed

- Portability guard: `command -v sqlite3 >/dev/null 2>&1` prevents apply failure on hosts without an SQL engine.
- Auto-rollback sugar: on apply failure restore from `.seed_migration.pre_apply.txt` immediately and exit non-zero.
- Validation scaffold: checksum stability over source file plus optional `validate.sh` hook keeps post-deploy checks minimal but deterministic.
- Ad-hoc verification: copy control dir into mktemp workspace; never mutate source control dir during tests.
