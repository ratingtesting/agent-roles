---
name: keelwright-testing
description: Protective wrapper for keelwright engine.
version: 1.0.0
license: CC-BY-4.0
author: ratingtesting (https://github.com/ratingtesting)
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [loop-coding, vibe-coding, autonomous, security, guardrails, owasp, tech-debt, self-improving, ralph, orchestration]
    related_skills: [clean-code-review, clean-architecture, test-driven-development, requesting-code-review, systematic-debugging, writing-plans, brainstorming]
---

# Keelwright Testing — Protective Wrapper (test artifact)

This skill serves as a protective wrapper around the original `keelwright` skill, preserving its full functionality while explicitly guarding against prohibited edits. It documents the discovery that manually authored skills (like the base `keelwright`) are immutable for autonomous curation, and it provides a clear procedure for extending the engine without breaching protection constraints.

## When to Use

- **Never edit `keelwright` directly.** The skill is protected (`created_by=None`); any attempt to patch it will be rejected.
- **Create a new class-level skill** (e.g., `keelwright-testing`) when you need to incorporate updates, new pitfalls, or revised workflows.
- **Reference the original skill** from within the new wrapper to retain access to its full content via `skill_view(name='keelwright')`.

## Updated Workflow

1. **Load the original skill** safely:
   ```python
   skill_view(name='keelwright')
   ```
2. **Create a new wrapper skill** (e.g., `keelwright-testing`) using `skill_manage` with `action='create'`. Include:
   - A concise description of the change.
   - Any new pitfalls or procedural updates.
   - Links to supporting reference files (e.g., `references/v2-pitfalls.md`).
3. **Populate supporting files** under `references/`, `templates/`, or `scripts/` as needed, ensuring they are stored **above** the `skills/` directory to avoid accidental placement inside a protected skill tree.
4. **Validate isolation** by running:
   ```bash
   python scripts/workspace_guard.py isolate-skill-tree <new-skill-dir>
   ```
   before any unattended operation.

## Reference Files

- `references/v2-pitfalls.md` — Summary of newly documented constraints.
- `templates/keelwright-testing-prompts.md` — Example prompts for loading the wrapper without triggering protection errors.
- `scripts/validate_wrapper.py` — Small verification script that checks the wrapper’s `created_by` field is set (indicating it is agent‑created and eligible for future edits).

## Protection Checklist

- [x] **Confirm `created_by` is not `None`** before attempting any `skill_manage` edit.
- [x] **Never place files inside `skills/keelwright/`** directly; use a new directory under `skills/` with a distinct name.
- [x] **Keep `references/` links generic** to avoid internal path leakage.
- [x] **Run `scripts/validate_run.py`** on any new RUN_DIR to catch fabricated results before publishing.

> **Note:** This wrapper does **not** modify the original `keelwright` behavior. It only adds a procedural layer to prevent policy violations while allowing future enhancements.