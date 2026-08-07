---
name: hermes-state-db-recovery
description: Recover original file body from Hermes state.db.
---

# Hermes State DB file recovery

Use when a document/file on disk was corrupted or truncated by an agent that
"recreated it from memory" (common with long specs: FOUNDER_DECISIONS, MASTER_SPEC,
any 20-40KB markdown). The reliable fix is NOT to reconstruct again from memory and
NOT to trust git history that was created AFTER the corruption — it's to extract the
**original `write_file` tool-call body** that the producing agent actually wrote to its
own session, which lives in the Hermes SQLite session store.

## Principle

The agent that FIRST generated a file wrote it through `write_file`, and the full
`content` argument is persisted verbatim in the message store. That is the source of
truth — far more reliable than human/LLM recall. Once corruption is detected, restore
from the DB, not from a paraphrase.

## Steps

1. Locate the profile store: `C:\Users\<user>\AppData\Local\hermes\profiles\<profile>\state.db`
   (NOT the kanban board DB; user-facing sessions live in `state.db`, table `messages`).

2. Find the original write call. A python (sqlite3) query over `state.db`:
   - list `messages` rows where `tool_calls` contains the filename;
   - the message carries a `tool_calls` JSON column; entry with
     `function.name == "write_file"` and `function.arguments.path` ending in the filename;
   - take the `arguments.content` — that IS the original text.

3. **Pick the largest / earliest producing write**, not a re-write by a "fixer" agent.
   In this session the worker's original was the biggest (messages 5816/6050); the
   fixer-session writes were smaller (3K-18K) and still corrupted. Sort candidates by
   content length descending and compare to disk to confirm authenticity.

4. Compare on disk vs candidate — byte size via `len(content.encode('utf-8'))`
   exposes corruption instantly (e.g. 10953 vs 32545 bytes = truncated 3x).

5. Write recovered content to the target path, then re-verify: byte size, heading
   count, conflict markers, structural invariants (e.g. `## ` count, `CONFLICT`, `ADR-0`).

## Pitfalls

- **git is not a safe restore source if `git init` happened AFTER the corruption**
  (baseline/checkpoint already holds broken text). Check `git log` dates vs crash
  timeline; pre-corruption git is good only when it predates the break.
- **Distinguish producer vs repairer sessions.** `session_id` on the `messages` row
  tells which context wrote it. Producer worker session holds the authentic body; a
  later "restore from memory" session holds the corrupted one.
- **Inspect never paraphrase.** Compare the first lines of disk vs candidate — a
  single-token drift is a real corruption signature, not a cosmetic diff.
- **Log evidence.** Always print byte count + structural markers into the restore log
  so the next session (and a user asking "did you really do this?") sees proof.

## See also

- `references/state-db-schema.md` — `messages`/`tool_calls` column layout and the SQL
  used to locate a `write_file`.