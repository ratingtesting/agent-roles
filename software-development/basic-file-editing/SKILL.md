---
name: basic-file-editing
description: Edit files to fix typos and replace text.
---

# Basic File Editing

## When to Use
Use this skill for simple text modifications like:
- Fixing typos in text files
- Replacing specific strings
- Making minor text corrections
- Simple find-and-replace operations

## Workflow

1. **Locate the file(s)**
   - Use `search_files` with target='files' to find all instances
   - Check multiple locations if the file might exist in different places

2. **Verify the content**
   - Use `read_file` to see current content
   - Use terminal commands like `cat`, `xxd` to inspect exact characters

3. **Make the change**
   - Use `patch` with mode='replace' for precise string replacement
   - Include sufficient context in old_string to ensure uniqueness
   - Verify the change with diff output

4. **Verify the fix**
   - Re-read the file to confirm the change
   - Use multiple methods (read_file, terminal cat) for confirmation

## Pitfalls & Corrections

- **Assuming file location**: Always search for files rather than assuming location
  - *Fix*: Use search_files(target='files') to find all instances

- **Missing the exact text**: Files may appear correct but contain hidden characters
  - *Fix*: Use terminal commands like `xxd` or `cat -A` to inspect exact content

- **Making overly broad changes**: Replace-all can cause unintended modifications
  - *Fix*: Use unique context strings in old_string to ensure precision

- **Stream timeouts on large tool arguments**: A single `write_file` or `patch`
  call whose content exceeds ~8K tokens can stall mid-stream ("Stream stalled
  mid tool-call ... action was not executed") and the write is DROPPED — nothing
  lands on disk, and the system tells you not to retry the same large call.
  - *Fix*: Pre-split large files. Write the file in one small `write_file`
    (header + first section, well under 8K tokens), then APPEND the rest with
    several small `patch(mode='replace')` calls that each anchor on the file's
    current last lines. If a call does time out, verify state (read the file or
    `ls`) before continuing — never assume partial success, never blindly resend
    the same oversized payload.

## Verification
Always verify changes by:
1. Reading the file back
2. Checking with terminal commands
3. Confirming the exact text replacement worked as intended

## Example
To fix "helllo" to "hello" in typo.txt:

```
# Find all instances
search_files(pattern="typo.txt", target="files")

# Check content
read_file(path=".\typo.txt")

# Make precise replacement
patch(mode="replace", path=".\typo.txt", old_string="helllo", new_string="hello")

# Verify
read_file(path=".\typo.txt")
```

## Related Skills
- `clean-code-review`: For code quality improvements beyond simple text edits
- `verification-before-completion`: For verifying changes before considering work done