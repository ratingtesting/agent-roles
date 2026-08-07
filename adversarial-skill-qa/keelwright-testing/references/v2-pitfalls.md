# v2 Pitfalls Discovered

- **Protected-skill edit prohibition**: Manual authored skills (e.g., `keelwright`) have `created_by=None` and cannot be patched directly. Attempting to edit them results in rejection.
- **Wrapper-skill requirement**: Any modification or extension must be done via a new class-level skill (e.g., `keelwright-testing`) placed above the `skills/` directory.
- **Isolation validation**: Before unattended operations, run `python scripts/workspace_guard.py isolate-skill-tree <new-skill-dir>` to ensure read-only protection remains intact.
- **Reference leakage**: Do not place files inside `skills/keelwright/`; use a separate directory under `skills/` to avoid ambiguity.
- **Create‑by verification**: Confirm `created_by` is not `None` in the new skill’s metadata before performing any `skill_manage` edit operations.