#!/usr/bin/env bash
# verify-free-web.sh
# Quick check that Hermes is configured for free web backends only.

set -euo pipefail

CONFIG_FILE="${HOME}/.hermes/config.yaml"

echo "=== Checking Hermes web/backend configuration ==="
if ! grep -q "^web:" "$CONFIG_FILE"; then
  echo "❌ No web section found in $CONFIG_FILE"
  exit 1
fi

# Extract relevant settings
backend=$(grep -A2 "^web:" "$CONFIG_FILE" | grep "backend:" | awk '{print $2}' | tr -d ' ')
search_backend=$(grep -A2 "^web:" "$CONFIG_FILE" | grep "search_backend:" | awk '{print $2}' | tr -d ' ')
extract_backend=$(grep -A2 "^web:" "$CONFIG_FILE" | grep "extract_backend:" | awk '{print $2}' | tr -d ' ')
use_gateway=$(grep -A2 "^web:" "$CONFIG_FILE" | grep "use_gateway:" | awk '{print $2}' | tr -d ' ')

echo "web.backend:           $backend"
echo "web.search_backend:    $search_backend"
echo "web.extract_backend:   $extract_backend"
echo "web.use_gateway:       $use_gateway"

# Check browser settings
echo ""
echo "=== Checking browser configuration ==="
if ! grep -q "^browser:" "$CONFIG_FILE"; then
  echo "❌ No browser section found in $CONFIG_FILE"
  exit 1
fi

cloud_provider=$(grep -A2 "^browser:" "$CONFIG_FILE" | grep "cloud_provider:" | awk '{print $2}' | tr -d ' ')
browser_use_gateway=$(grep -A2 "^browser:" "$CONFIG_FILE" | grep "use_gateway:" | awk '{print $2}' | tr -d ' ')

echo "browser.cloud_provider: $cloud_provider"
echo "browser.use_gateway:    $browser_use_gateway"

# Validate
errors=0
warnings=0

if [[ "$backend" != "crawl4ai" ]]; then
  echo "❌ web.backend should be 'crawl4ai', got '$backend'"
  errors=$((errors+1))
fi

if [[ "$search_backend" != "ddgs" ]]; then
  echo "❌ web.search_backend should be 'ddgs', got '$search_backend'"
  errors=$((errors+1))
fi

if [[ "$extract_backend" != "crawl4ai" ]]; then
  echo "❌ web.extract_backend should be 'crawl4ai', got '$extract_backend'"
  errors=$((errors+1))
fi

if [[ "$use_gateway" != "false" ]]; then
  echo "❌ web.use_gateway should be 'false', got '$use_gateway' (risk of paid fallback)"
  errors=$((errors+1))
fi

if [[ "$cloud_provider" != "local" ]]; then
  echo "❌ browser.cloud_provider should be 'local', got '$cloud_provider'"
  errors=$((errors+1))
fi

if [[ "$browser_use_gateway" != "false" ]]; then
  echo "❌ browser.use_gateway should be 'false', got '$browser_use_gateway' (risk of paid fallback)"
  errors=$((errors+1))
fi

# Check for any remaining paid gateway references in config
if grep -qiE "(firecrawl|browser-use|use_gateway: true)" "$CONFIG_FILE"; then
  echo "⚠️  Found potential paid gateway references in config (may be comments or inactive sections)"
  warnings=$((warnings+1))
fi

# Plugin check
echo ""
echo "=== Checking plugin status ==="
if hermes plugins list 2>/dev/null | grep -q "web-crawl4ai.*enabled"; then
  echo "✅ web-crawl4ai plugin is enabled"
else
  echo "❌ web-crawl4ai plugin not enabled. Run: hermes plugins enable web-crawl4ai"
  errors=$((errors+1))
fi

# Summary
echo ""
if [[ $errors -eq 0 ]]; then
  echo "✅ All checks passed! Hermes is configured for free web backends only."
  if [[ $warnings -gt 0 ]]; then
    echo "   ($warnings warnings - review above)"
  fi
  exit 0
else
  echo "❌ $errors error(s) found. Fix the issues above to ensure zero-cost operation."
  exit 1
fi