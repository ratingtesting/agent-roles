\## Subagent dispatch requires multi-agent support

Add to your Codex config (\`~/.codex/config.toml\`):

\`\`\`toml
\[features\]
multi\_agent = true
\`\`\`

This enables \`spawn\_agent\`, \`wait\_agent\`, and \`close\_agent\` for skills like \`dispatching-parallel-agents\` and \`subagent-driven-development\`. When using subagent-driven-development, you should always close implementer and reviewer subagents when they have finished all their work.

\## Environment Detection

Skills that create worktrees or finish branches should detect their
environment with read-only git commands before proceeding:

\`\`\`bash
GIT\_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT\_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
\`\`\`

\- \`GIT\_DIR != GIT\_COMMON\` → already in a linked worktree (skip creation)
\- \`BRANCH\` empty → detached HEAD (cannot branch/push/PR from sandbox)

See \`using-git-worktrees\` Step 0 and \`finishing-a-development-branch\`
Step 1 for how each skill uses these signals.

\## Codex App Finishing

When the sandbox blocks branch/push operations (detached HEAD in an
externally managed worktree), the agent commits all work and informs
the user to use the App's native controls:

\- \*\*"Create branch"\*\* — names the branch, then commit/push/PR via App UI
\- \*\*"Hand off to local"\*\* — transfers work to the user's local checkout

The agent can still run tests, stage files, and output suggested branch
names, commit messages, and PR descriptions for the user to copy.