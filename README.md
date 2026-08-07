# Hermes Agent Skills — Local Versioned Repository

**Source:** `C:\Users\Unicorn\AppData\Local\hermes\profiles\app\skills` (synced to `default` and `marketplace` profiles)

**Total skills:** 378 (22 critical roles + 356 others)

**Last sync:** 2026-08-08

---

## Structure

```
hermes-skills-repo/
├── .gitignore
├── README.md
├── <skill-name>/
│   └── SKILL.md          # agent-authoring 6-slot structure
│   └── references/       # optional reference files
│   └── templates/        # optional templates
│   └── scripts/          # optional scripts
```

---

## 22 Critical Roles (6/6 slots, verified 2026)

| Role | Profile | Lines | Slots |
|------|---------|-------|-------|
| mobile-app-builder | app/default/marketplace | 71 | 6/6 |
| app-store-optimizer | app/default/marketplace | 71 | 6/6 |
| rapid-prototyper | app/default/marketplace | 75 | 6/6 |
| wechat-mini-program-developer | app/default/marketplace | 74 | 6/6 |
| seo-specialist | app/default/marketplace | 72 | 6/6 |
| growth-hacker | app/default/marketplace | 71 | 6/6 |
| reddit-community-builder | app/default/marketplace | 70 | 6/6 |
| twitter-engager | app/default/marketplace | 70 | 6/6 |
| content-creator | app/default/marketplace | 72 | 6/6 |
| tiktok-strategist | app/default/marketplace | 73 | 6/6 |
| social-media-strategist | app/default/marketplace | 80 | 6/6 |
| email-strategist | app/default/marketplace | 73 | 6/6 |
| founder-visionary | app/default/marketplace | 72 | 6/6 |
| economy-designer | app/default/marketplace | 72 | 6/6 |
| software-architect | app/default/marketplace | 72 | 6/6 |
| code-reviewer | app/default/marketplace | 68 | 6/6 |
| minimal-change-engineer | app/default/marketplace | 68 | 6/6 |
| technical-writer | app/default/marketplace | 72 | 6/6 |
| mobile-release-engineer | app/default/marketplace | 73 | 6/6 |
| i18n-engineer | app/default/marketplace | 73 | 6/6 |
| multi-platform-publisher | app/default/marketplace | 83 | 6/6 |
| short-video-editing-coach | app/default/marketplace | 73 | 6/6 |

---

## Sync Script

```bash
# Sync from Hermes profile to repo
rsync -av --delete "$LOCALAPPDATA/hermes/profiles/app/skills/" /c/Projects/hermes-skills-repo/

# Sync from repo to all profiles
for profile in app default marketplace; do
  rsync -av --delete /c/Projects/hermes-skills-repo/ "$LOCALAPPDATA/hermes/profiles/$profile/skills/"
done
```

---

## Agent-Authoring Structure (6 Slots)

Every `SKILL.md` follows:

```markdown
---
name: skill-name
description: Use when <trigger>. <one-line behavior>.
---

# Skill Title

## Role — «Ты <эксперт> уровня ведущего, <core responsibility>»

## Context — <what to read/know before acting>

## Task — контракт вывода (4 подслота)
### 1. <Output Artifact 1>
### 2. <Output Artifact 2>
### 3. <Output Artifact 3>
### 4. <Output Artifact 4>

## Hard Rules — жёсткие с red-flags
- Rule 1
- Rule 2
- **Cross-profile запись — файл в профиле `app`, агент может работать под `default` → `cross_profile=True`**

## Output Example — один реальный кусок
```markdown
<concrete example>
```

## Dependencies
- <role1> — <purpose>
- <role2> — <purpose>

## Sources (verified 2026)
- <source1> — <what verified>
- <source2> — <what verified>
```

---

## Versioning

- **Git history** = all changes
- **Tags** = major milestones (e.g., `v1.0-critical-roles`, `v1.1-full-repo`)
- **Branches** = experimental variants

```bash
cd /c/Projects/hermes-skills-repo
git add -A && git commit -m "sync: <description>"
git tag -a v1.0-critical-roles -m "22 critical roles at 6/6 slots"
```

---

## Profiles

| Profile | Purpose | Skills Count |
|---------|---------|--------------|
| `app` | Telegram Mini App + Ai Company OS | 378 |
| `default` | General Hermes usage | 378 |
| `marketplace` | Marketplace-specific agents | 380 (+2) |