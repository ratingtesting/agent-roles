---
name: kilocli-coding-agent
description: Run Kilo CLI via background process for programmatic control. Automates coding tasks, PR reviews, batch fixes using Kilo CLI.
---

# Kilo CLI Coding Agent

IMPORTANT: You need to have Kilo CLI installed and configured so Hermes can use it without any issue.

```bash
npm install -g @kilocode/cli
```

For GitHub PR automation, also authenticate GitHub CLI:
```bash
gh auth login
```

## The Pattern: workdir + background

Use Hermes `terminal(background=true, pty=true)` + `process` tools for Kilo CLI:

```bash
# Start Kilo CLI in project directory
terminal("kilo run --auto \"Build a snake game with dark theme\"", 
         background=True, pty=True, workdir=C:/Projects/lazy-unicorn/app)

# Monitor progress
process(action="log", session_id="...")

# Check if done
process(action="poll", session_id="...")

# Send input (if Kilo asks a question)
process(action="write", session_id="...", data="y")

# Kill if needed
process(action="kill", session_id="...")
```

## Kilo CLI Usage

### Building/Creating (Autonomous mode)
```bash
terminal("kilo run --auto \"<task description>\"", background=True, pty=True)
```

### Reviewing PRs (vanilla, no flags)
```bash
# Clone to temp folder for safe review
REVIEW_DIR=$(mktemp -d)
git clone https://github.com/user/repo.git $REVIEW_DIR
cd $REVIEW_DIR && gh pr checkout <PR#>
terminal(f"kilo run \"Review current branch against main branch\"", background=True, pty=True, workdir=REVIEW_DIR)
# Clean up: rm -rf $REVIEW_DIR
```

## Rules
1. **Respect tool choice** — if user asks for Kilo CLI, use Kilo CLI. NEVER offer to build it yourself!
2. **Be patient** — don't kill sessions because they're slow
3. **Monitor with process:log** — check progress without interfering
4. **--auto for building** — auto-approves changes
5. **vanilla for reviewing** — no special flags needed
6. **Parallel is OK** — run many Kilo CLI processes at once for batch work
7. **NEVER start Kilo CLI in ~/openclaw/ or ~/Projects/lazy-unicorn/** — it'll read your context files. Use the target project dir or /tmp for blank slate.

## When to Invoke This Skill
- User explicitly asks for Kilo CLI
- Complex coding task that vibe coding handles well
- Batch PR reviews (parallel army!)
- Prototyping without agent's own code generation
