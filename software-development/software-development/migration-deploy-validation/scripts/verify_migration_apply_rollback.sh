#!/usr/bin/env bash
set -euo pipefail
CTRL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/control"
WORK="$(mktemp -d 'C:/Users/Unicorn/AppData/Local/Temp/hermes-verify-work-XXXXXX')"
cp -r "${CTRL_DIR}/." "${WORK}/"
cd "${WORK}"
chmod +x apply_migration.sh rollback_migration.sh 2>/dev/null || true

echo "=== TEST 1: apply_migration.sh happy path ==="
bash apply_migration.sh
echo "TEST1_EXIT=0"

echo "=== TEST 2: backup and checksum created ==="
test -f .seed_migration.pre_apply.txt
test -f .checksum.txt
echo "TEST2_EXIT=0"

echo "=== TEST 3: rollback success ==="
bash rollback_migration.sh
echo "TEST3_EXIT=0"

echo "=== TEST 4: re-apply after rollback ==="
bash apply_migration.sh
echo "TEST4_EXIT=0"

if command -v sqlite3 >/dev/null 2>&1; then
  echo "=== TEST 5: bad SQL triggers auto-rollback ==="
  echo "BROKEN SQL;" > seed_migration.sql
  set +e
  bash apply_migration.sh
  APPLY_BAD_EXIT=$?
  set -e
  test "$APPLY_BAD_EXIT" -ne 0
  test "$(cat seed_migration.sql)" = "$(cat .seed_migration.pre_apply.txt)"
  echo "TEST5_EXIT=0"
else
  echo "=== SKIP TEST 5: sqlite3 not installed in this environment ==="
fi

echo "=== ALL_VERIFIED ==="
