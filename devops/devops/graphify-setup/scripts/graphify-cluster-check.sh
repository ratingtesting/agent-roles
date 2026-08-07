#!/usr/bin/env bash
# graphify-cluster-check.sh
# Runs daily 10:00 via cronjob (job_id: 08661501e2db)
# Checks all projects under /c/Projects/, excludes foreign/vendor subdirs,
# prints reminder when project crosses 80 code files and lacks .cluster_done flag.

THRESHOLD=80
BASE="/c/Projects"
ANY=false
OUTPUT=""

for dir in "$BASE"/*/; do
  PROJECT=$(basename "$dir")
  CLUSTER_FLAG="${dir}graphify-out/.cluster_done"
  [ -f "$CLUSTER_FLAG" ] && continue

  # Build find exclusions
  EXCLUDES=(
    ! -path "$dir/.git/*"
    ! -path "*/.venv/*"
    ! -path "*/node_modules/*"
    ! -path "*/build/*"
    ! -path "*/.dart_tool/*"
    ! -path "*/target/*"
  )
  if [ "$PROJECT" = "lazy-unicorn" ]; then
    EXCLUDES+=(
      ! -path "$dir/openhands/*"
      ! -path "$dir/ai-company/*"
      ! -path "$dir/desloppify/*"
      ! -path "$dir/9router-proxy/*"
      ! -path "$dir/agency-agents/*"
      ! -path "$dir/graphify-out/*"
      ! -path "$dir/scripts/*"
    )
  fi

  COUNT=$(find "$dir" -type f \
    \( -name '*.dart' -o -name '*.py' -o -name '*.ts' -o -name '*.tsx' \
       -o -name '*.go' -o -name '*.rs' -o -name '*.kt' -o -name '*.swift' \) \
    "${EXCLUDES[@]}" 2>/dev/null | wc -l)

  if [ "$COUNT" -ge "$THRESHOLD" ]; then
    OUTPUT+="📊 В проекте $PROJECT уже $COUNT файлов кода. Пора запустить кластеризацию:
  cd ${dir%/} && source ~/.bash_profile && graphify-nemo . --cluster --max-concurrency 1 --api-timeout 600
После первого запуска поставь флаг:
  touch ${dir}graphify-out/.cluster_done

"
    ANY=true
  fi
done

[ "$ANY" = true ] && echo "$OUTPUT"
exit 0