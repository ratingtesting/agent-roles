---
name: skill-handling-best-practices
description: Best practices for large Hermes skills.
---

# Skill Handling Best Practices

## Working with Large Skills

When using `skill_view` on a large skill (like `keelwright`), the returned content may be truncated (marked as `[SKILL_PRUNED]`). This is a mechanism to prevent the context from being overwhelmed.

### How to Access Full Content

1. **Use Linked Files**: Instead of relying on the full `SKILL.md`, access the specific references, templates, or scripts you need by specifying the `file_path` parameter in `skill_view`.
   Example:
   ```
   skill_view(name='keelwright', file_path='references/qa-testing.md')
   ```

2. **Access the Skill Directory Directly** (outside of automated runs):
   When not in an automated run (e.g., when developing or debugging), you can read the skill files directly from the filesystem:
   - On Windows: `%LOCALAPPDATA%\\hermes\\skills\\<skill-name>\\`
   - On Linux/macOS: `$HOME/.local/share/hermes/skills/<skill-name>/`
   
   Note: During automated runs (like QA tests), the skill directory is made read-only and isolated for safety.

3. **Check for Pruning**: If the output of `skill_view` includes `[SKILL_PRUNED]`, treat the content as incomplete and use the above methods.

## General Skill Usage

- Always check the skill's `references/` directory for detailed guidance.
- Use the `templates/` and `scripts/` directories for reusable assets.
- When a skill requires a skill in a subagent's context, pass the specific file paths needed rather than assuming the subagent inherits the skill.

## Related Skills

- `hermes-agent`: For configuring and extending Hermes itself.
- `skill-publishing`: For creating and maintaining your own skills.
- `writing-skills`: For guidance on writing effective skills.

---

## Example: Working with the Keelwright Skill

To access the QA testing methodology in the keelwright skill without relying on the pruned SKILL.md:

```
skill_view(name='keelwright', file_path='references/qa-testing.md')
```

To access the loop audit checklist:

```
skill_view(name='keelwright', file_path='references/loop-audit-checklist.md')
```

---

## Changelog

* 2026-07-25: Initial version based on lessons learned during autonomous QA of the keelwright skill.