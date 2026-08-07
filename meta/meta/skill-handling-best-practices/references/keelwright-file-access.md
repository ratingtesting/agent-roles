# Accessing Keelwright Skill Files

During autonomous QA sessions, the keelwright skill is frequently accessed. Due to its size, `skill_view(name='keelwright')` returns truncated content marked as `[SKILL_PRUNED]`.

To access specific sections of the keelwright skill, use the `file_path` parameter:

## Frequently Accessed Files

- QA Testing Methodology: `references/qa-testing.md`
- Loop Audit Checklist: `references/loop-audit-checklist.md`
- Phases Documentation: `references/phases.md`
- Security Gates: `references/security-gates.md`
- Writing Code Guidelines: `references/writing-code.md`
- Circuit Breaker: `references/circuit-breaker.md`
- Stability and Learning: `references/stability-and-learning.md`
- QA Trap Catalog: `references/qa-trap-catalog.md`
- QA Results Archive: `references/qa-results-*.md`

## Access Pattern

```
# To access QA testing methodology:
skill_view(name='keelwright', file_path='references/qa-testing.md')

# To access loop audit checklist:
skill_view(name='keelwright', file_path='references/loop-audit-checklist.md')

# To access security gates:
skill_view(name='keelwright', file_path='references/security-gates.md')
```

## Working Directory Access (Development Only)

When not in automated runs, you can access files directly:
- Windows: `%LOCALAPPDATA%\\hermes\\skills\\keelwright\\references\\`
- Linux/macOS: `$HOME/.local/share/hermes/skills/keelwright/references/`

Note: During automated QA runs, the skill directory is isolated and made read-only for safety.

## Common Pitfall

**Problem**: Assuming `skill_view(name='keelwright')` returns the complete skill content.
**Result**: Missing critical information from truncated sections.
**Solution**: Always use `file_path` parameter to access specific referenced files when working with large skills like keelwright.