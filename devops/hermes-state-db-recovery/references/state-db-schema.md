# state.db schema & locate-a-write_file SQL

Profile DB: `C:\Users\<user>\AppData\Local\hermes\profiles\<profile>\state.db`
Functions: takes a `tool_calls` JSON column on `messages` with the full `content`.

## messages columns (observed)

`id, session_id, role, content, tool_call_id, tool_calls, tool_name,
effect_disposition, timestamp, token_count, finish_reason, reasoning,
reasoning_content, reasoning_details, codex_reasoning_items, codex_message_items,
platform_message_id, observed, active, compacted, api_content, display_kind,
display_metadata`

`state.db` also has: `sessions`, `messages_fts` (FTS5), `sqlite_sequence`,
`session_model_usage`, `state_meta`, `gateway_routing`, `compression_locks`,
`async_delegations`, `delivery_obligations`.

Kanban boards live in a DIFFERENT db:
`C:\Users\<user>\AppData\Local\hermes\kanban\boards\<board>\kanban.db`
(tables: `tasks, task_links, task_comments, task_events, task_runs,
task_attachments, kanban_notify_subs`). Worker session bodies are in the PROFILE
`state.db` — its `messages.session_id` links to the kanban run; the kanban DB itself
stores only run summaries, not full file writes.

## SQL: find every write_file for a target filename

```python
import sqlite3, json

db = r"C:\Users\<user>\AppData\Local\hermes\profiles\app\state.db"
c = sqlite3.connect(db)
rows = c.execute("SELECT id, session_id, tool_calls FROM messages "
                 "WHERE tool_calls LIKE '%NAME.md%' OR tool_calls LIKE '%write_file%'"
                 " ORDER BY id").fetchall()

for mid, sid, tc in rows:
    try:
        data = json.loads(tc) if isinstance(tc, str) else tc
    except Exception:
        continue
    if not isinstance(data, list):
        data = [data]
    for call in data:
        if call.get("function", {}).get("name") == "write_file":
            args = call["function"]["arguments"]
            args = json.loads(args) if isinstance(args, str) else args
            path  = args.get("path", "")
            content = args.get("content", "")
            print(mid, (sid or "None")[:24], path.split("\\")[-1], len(content))
```

Pick the row whose `len(content)` matches the expected original byte size
(see SKILL.md) — that is the authentic producer write, not a repairer rewrite.

## Sanity: file bytes check

```python
disk  = open(target_path, "r", encoding="utf-8", newline="\n").read()
print("disk bytes ", len(disk.encode("utf-8")),
      "| candidate bytes", len(content.encode("utf-8")))
```

Concrete return: `<other>` exceeds a 3x gap (e.g. 10953 vs 32545) = truncated corruption.