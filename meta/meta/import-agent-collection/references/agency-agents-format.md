# agency-agents → Hermes SKILL.md format

## Source frontmatter (agency-agents agent file)
```yaml
---
name: Software Architect
description: Expert software architect specializing in system design, domain-driven design, ...
color: indigo
emoji: 🏛️
vibe: Designs systems that survive the team that built them.
tools: Read, Write, Edit
---
# <Agent title>
<body in markdown>
```

## Target frontmatter (Hermes SKILL.md)
```yaml
---
name: engineering-software-architect
description: <copied verbatim from source>
---
<body copied verbatim>
```
Accepted Hermes fields: `name` (req), `description` (req, ≤1024), optional `license`, `compatibility`, `metadata`, `allowed-tools`. Drop `color/emoji/vibe/tools`.

## Conversion snippet (run via execute_code)
```python
import os, re

def wpath(p):
    # MSYS /c/Users/... -> Windows C:\Users\... for the natively-Windows Hermes python
    if p.startswith('/c/'):
        p = 'C:/' + p[3:]
    return p.replace('/', '\\')

SKILLS = '/c/Users/Unicorn/AppData/Local/hermes/skills'  # MSYS form

# explicit mapping: (source repo-relative path, skill-name)
mapping = [
    ('engineering/engineering-software-architect.md', 'engineering-software-architect'),
    ('engineering/engineering-software-architect.md', 'software-architect'),  # alias collision
    # ...
]

for src_rel, name in mapping:
    src = '/c/Projects/agency-agents/' + src_rel
    with open(wpath(src), encoding='utf-8') as f:
        text = f.read()
    assert text.startswith('---')
    end = text.index('---', 3)
    fm = text[3:end]
    body = text[end+3:].lstrip('\n')
    m = re.search(r'^description:\s*(.+)$', fm, re.M)
    desc = m.group(1).strip()
    skill_md = f"---\nname: {name}\ndescription: {desc}\n---\n\n{body}"
    d = wpath(f"{SKILLS}/{name}")
    os.makedirs(d, exist_ok=True)
    with open(f"{d}/SKILL.md", 'w', encoding='utf-8') as f:
        f.write(skill_md)
```

## Name-collision example handled this session
`software-architect` and `engineering-software-architect.md` resolve to the SAME file. Both skill names were written (alias), so `skill_view(name='software-architect')` and `skill_view(name='engineering-software-architect')` both work.

## Custom skills authored (not in repo) this session
- `unlock-architect` — Unlock Bible, plugin-ready strategies
- `campaign-architect` — Campaign Bible, lifecycle/economy/KPI
- `founder-visionary` — vision-only, no code
- `flutter-architect` — Flutter Clean Architecture + TON/Telegram
- `chief-simplicity-officer` — scope-cutting review
