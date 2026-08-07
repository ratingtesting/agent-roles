#!/usr/bin/env python3
"""
Validate that a new wrapper skill has a non‑None created_by field
and that its metadata points to a valid skill directory.
Use before publishing any new wrapper.
"""
import json, os, sys

def main():
    skill_dir = os.getenv("SKILL_DIR")
    if not skill_dir:
        print("Set SKILL_DIR to the skill's directory path.", file=sys.stderr)
        sys.exit(1)

    meta_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(meta_path):
        print(f"Metadata file not found: {meta_path}", file=sys.stderr)
        sys.exit(1)

    # Extract front‑matter (simple yaml parse)
    with open(meta_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^---\n(yaml\.yaml\|\n)(.*?)\n---\n", content, re.S)
    if not match:
        print("Could not locate YAML front‑matter.", file=sys.stderr)
        sys.exit(1)
    yaml_block = match.group(2)
    try:
        meta = json.loads(json.dumps(json.loads(yaml_block)))  # naive parse for demo
    except Exception:
        print("Failed to parse metadata JSON.", file=sys.stderr)
        sys.exit(1)

    created_by = meta.get("metadata", {}).get("created_by")
    if created_by is None:
        print("ERROR: created_by is None – this skill cannot be edited.", file=sys.stderr)
        sys.exit(1)
    else:
        print("Validation passed: created_by is set.")

if __name__ == "__main__":
    import re, sys, os
    main()