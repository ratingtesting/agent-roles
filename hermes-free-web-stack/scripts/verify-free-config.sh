#!/bin/bash
# Verify that Hermes is configured for free web search/extraction only
# Returns 0 if all checks pass, 1 if any paid gateway/settings detected

echo "🔍 Verifying Hermes free web stack configuration..."

# Check config file
CONFIG="$HOME/.hermes/config.yaml"
if [ ! -f "$CONFIG" ]; then
    echo "❌ Config file not found: $CONFIG"
    exit 1
fi

# Check for paid gateway settings
echo "Checking for paid gateway settings..."
if grep -qi "use_gateway: true" "$CONFIG"; then
    echo "❌ Found use_gateway: true (enables paid gateways)"
    exit 1
fi

if grep -qi "cloud_provider: browser-use" "$CONFIG"; then
    echo "❌ Found cloud_provider: browser-use (paid Browser-Use backend)"
    exit 1
fi

if grep -qi "backend: firecrawl" "$CONFIG"; then
    echo "❌ Found backend: firecrawl (paid backend)"
    exit 1
fi

if grep -qi "search_backend: firecrawl\|extract_backend: firecrawl" "$CONFIG"; then
    echo "❌ Found firecrawl as search or extract backend"
    exit 1
fi

# Check for free backend settings
echo "Checking for free backend settings..."
if ! grep -qi "backend: crawl4ai" "$CONFIG"; then
    echo "❌ Missing backend: crawl4ai"
    exit 1
fi

if ! grep -qi "search_backend: ddgs" "$CONFIG"; then
    echo "❌ Missing search_backend: ddgs"
    exit 1
fi

if ! grep -qi "extract_backend: crawl4ai" "$CONFIG"; then
    echo "❌ Missing extract_backend: crawl4ai"
    exit 1
fi

if ! grep -qi "cloud_provider: local" "$CONFIG"; then
    echo "❌ Missing cloud_provider: local"
    exit 1
fi

# Check plugin status
echo "Checking plugin status..."
if ! hermes plugins list 2>/dev/null | grep -q "web-crawl4ai.*enabled"; then
    echo "❌ Plugin web-crawl4ai is not enabled"
    exit 1
fi

echo "✅ All checks passed - Hermes is configured for free web stack only"
exit 0