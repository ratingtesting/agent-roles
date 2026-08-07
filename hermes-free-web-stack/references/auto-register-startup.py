"""
auto-register-startup.py — Запускать при старте Hermes для принудительной
регистрации плагина crawl4ai в реестре веб-провайдеров.

Без этого шага web_extract уходит в fallback на firecrawl даже при
правильной конфигурации web.extract_backend: crawl4ai.

Размещение: положить в ~/.hermes/scripts/auto-register-crawl4ai.py
и добавить вызов в автозагрузку Hermes или в профильный startup-skill.
"""

import sys
import logging

logger = logging.getLogger(__name__)

# Путь к hermes-agent — скорректируй под свою установку
HERMES_AGENT_PATH = r"C:\Users\Unicorn\AppData\Local\hermes\hermes-agent"


def register_crawl4ai() -> bool:
    """Force-register the crawl4ai plugin in Hermes web provider registry.

    Returns True on success, False if plugin not found or registration failed.
    """
    if HERMES_AGENT_PATH not in sys.path:
        sys.path.insert(0, HERMES_AGENT_PATH)

    try:
        from hermes_cli.plugins import discover_plugins, get_plugin_manager, PluginContext

        discover_plugins()
        pm = get_plugin_manager()
        plugin = pm._plugins.get("web/crawl4ai")

        if not plugin:
            logger.warning("crawl4ai plugin not found in Hermes plugin manager")
            return False
        if not plugin.module or not hasattr(plugin.module, "register"):
            logger.warning("crawl4ai plugin has no register() function")
            return False

        ctx = PluginContext(plugin.manifest, pm)
        plugin.module.register(ctx)

        # Verify
        from agent.web_search_registry import get_provider, get_active_extract_provider

        p = get_provider("crawl4ai")
        if p is None or not p.is_available():
            logger.warning("crawl4ai registered but not available")
            return False

        active = get_active_extract_provider()
        if active and active.name == "crawl4ai":
            logger.info("✅ crawl4ai registered and active: %s", active.name)
            return True
        else:
            logger.warning("Active extract provider is %s, not crawl4ai",
                           active.name if active else "None")
            return False

    except Exception as e:
        logger.error("crawl4ai registration failed: %s", e)
        return False


if __name__ == "__main__":
    success = register_crawl4ai()
    sys.exit(0 if success else 1)
