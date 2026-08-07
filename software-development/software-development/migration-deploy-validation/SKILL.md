---
name: migration-deploy-validation
description: >
  Class-level skill for controlled apply/rollback of schema or data migrations,
  post-deploy validation, and lightweight verification harnesses.
  Use when asked to build apply/rollback scripts, deploy-verification pipelines,
  or review post-deploy checks for migrations.
trigger:
  - построить/проверить apply и rollback для миграции
  - post-deploy validation / regression after deploy
  - верификация миграционного контрола без внешних навыков
  - создать контроль deploy и отката
capabilities:
  - apply path with pre-checks and backup
  - auto-rollback on apply failure
  - checksum-based post-deploy validation
  - idempotent re-apply/rollback semantics
  - ad-hoc verification script template for sandbox testing
---

# Migration Deploy Validation

## Steps
1. Identify immutable migration source file in `control/`; never edit it.
2. Implement `apply_migration.sh`:
   - compute pre-apply checksum
   - back up migration source to `.seed_migration.pre_apply.txt`
   - validate SQL text statically (skip comments/blank lines)
   - run live apply if engine is present; otherwise warn and continue
   - on failure, auto-restore from backup and exit non-zero
   - run inline post-deploy validation: checksum stability + marker presence
3. Implement `rollback_migration.sh`:
   - restore source from `.seed_migration.pre_apply.txt`
   - preserve prior checksum snapshot with timestamp
   - validate restored checksum matches pre-deploy state
4. Write `README.md`:
   - define post-deploy validation
   - list typical checks: SQL correctness, smoke tests, SLO/SLA, data migration completion, feature flags
   - explain regression value: containment, confidence, rollback decision basis, data safety, observability
5. Verify with ad-hoc script under `scripts/verify_migration_apply_rollback.sh`:
   - happy apply creates backup+checksum
   - rollback restores file and checksum
   - apply after rollback remains valid
   - apply with bad SQL fails when engine available

## Pitfalls
- Do not edit the seed source file.
- Guard `sqlite3` (or other engine) calls behind `command -v`; host may lack it.
- Avoid `set -e` around engine failure checks; disable temporarily if needed, but ensure rollback.
- Keep scripts stdutils-only for portability unless engine dependency is explicit.
- Avoid hard-coded absolute paths outside the control directory.

## Verification
```bash
# optional; requires engine present for failure-path coverage
bash scripts/verify_migration_apply_rollback.sh
```
