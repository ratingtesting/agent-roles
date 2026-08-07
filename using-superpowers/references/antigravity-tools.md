\# Antigravity CLI (\`agy\`) Tool Mapping

Skills speak in actions ("dispatch a subagent", "create a todo", "read a file"). On the Antigravity CLI (\`agy\`) these resolve to the tools below.

\| Action skills request \| Antigravity CLI equivalent \|
\|----------------------\|----------------------\|
\| Dispatch a subagent (\`Subagent (general-purpose):\` template) \| \`invoke\_subagent\` with a built-in \`TypeName\` — \`self\` for full-capability work, \`research\` for read-only (see \[Subagent support\](#subagent-support)) \|
\| Task tracking ("create a todo", "mark complete") \| a \*\*task artifact\*\* — \`write\_to\_file\` with \`IsArtifact: true\` and \`ArtifactType: "task"\` (see \[Task tracking\](#task-tracking)). \*\*Not\*\* \`manage\_task\`, which manages background processes. \|

\## Task tracking

Antigravity has \*\*no todo tool\*\* (\`manage\_task\` manages background
processes — \`list\`/\`kill\`/\`status\`/\`send\_input\` — it is \*not\* a checklist). When a
skill says to create a todo list or track tasks, maintain a \*\*task artifact\*\*: a
markdown checklist saved with \`write\_to\_file\` (\`IsArtifact: true\`,
\`ArtifactMetadata.ArtifactType: "task"\`), edited with \`replace\_file\_content\` /
\`multi\_replace\_file\_content\` as you go.

At the start of any multi-step task, create the task artifact listing every step of
your plan. As you complete each step, edit the artifact to mark it done (\`- \[x\]\`).
If the plan changes, update the checklist. Keep it current — it is your source of
truth for what remains; once the conversation gets long, re-read it before starting
each step.