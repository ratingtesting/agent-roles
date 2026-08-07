# Python Model-Provider Plugin Structure

Full reference for the Python plugin format used by Hermes model-provider plugins.

---

## Directory Layout

```
~/.hermes/plugins/model-providers/<name>/
├── __init__.py       # Required: calls register_provider(profile)
└── plugin.yaml       # Recommended: metadata for hermes plugins list
```

## `__init__.py` — Full Example

```python
from providers import register_provider
from providers.base import ProviderProfile

my_provider = ProviderProfile(
    name="my-provider",
    aliases=("my",),
    display_name="My Provider",
    description="Description for /model menu",
    signup_url="https://example.com/keys",
    env_vars=("MY_API_KEY",),
    base_url="https://api.example.com/v1",
    api_mode="chat_completions",     # or anthropic_messages, codex_responses
    auth_type="api_key",             # or oauth_device_code, oauth_external, etc.
    default_aux_model="my-fast-model",
    fallback_models=(
        "my-large-model",
        "my-medium-model",
        "my-fast-model",
    ),
)

register_provider(my_provider)
```

## `plugin.yaml`

```yaml
name: my-provider
kind: model-provider
version: 1.0.0
description: My custom inference provider
author: Your Name
```

## ProviderProfile Fields

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `name` | str | ✅ | Canonical id — matches `model.provider` and `--provider` flag |
| `aliases` | tuple[str] | ❌ | Alternative names resolved by `get_provider_profile()` |
| `display_name` | str | ❌ | Human label in `/model` picker |
| `description` | str | ❌ | Picker subtitle |
| `signup_url` | str | ❌ | Link for first-run setup |
| `env_vars` | tuple[str] | ✅ | API-key env vars in priority order; last `*_BASE_URL` entry overrides base_url |
| `base_url` | str | ✅ | Default inference endpoint |
| `models_url` | str | ❌ | Explicit catalog URL (default: `{base_url}/models`) |
| `auth_type` | str | ❌ | `api_key` (default), `oauth_device_code`, `oauth_external`, `copilot`, `aws_sdk` |
| `fallback_models` | tuple[str] | ❌ | Curated model list when live catalog fetch fails |
| `default_headers` | dict | ❌ | Headers sent on every request |
| `default_aux_model` | str | ❌ | Cheap model for auxiliary tasks |
| `api_mode` | str | ❌ | `chat_completions` (default) |
| `fixed_temperature` | Any | ❌ | `None` (use caller's value) or `OMIT_TEMPERATURE` sentinel |
| `default_max_tokens` | int | ❌ | Provider-level max_tokens cap |

## Custom Hooks (Override via Subclass)

```python
from typing import Any
from providers.base import ProviderProfile

class MyProfile(ProviderProfile):
    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Provider-specific message preprocessing"""
        return messages

    def build_extra_body(self, *, session_id=None, **context) -> dict:
        """Extra body fields merged into API call"""
        return {}

    def build_api_kwargs_extras(self, **context):
        """Returns (extra_body_additions, top_level_kwargs)"""
        return {}, {}

    def fetch_models(self, *, api_key=None, timeout=8.0) -> list[str] | None:
        """Custom model catalog fetch"""
        return super().fetch_models(api_key=api_key, timeout=timeout)
```

## When to Use Python Plugins vs YAML

| Need | Use |
|------|-----|
| Simple endpoint, no code | `custom_providers:` YAML |
| Custom message preprocessing | Python plugin with `prepare_messages` hook |
| Provider-specific request headers | Python plugin |
| Custom auth flow | Python plugin |
| No REST /models endpoint (Bedrock) | Python plugin with `fetch_models` returning None |
| Multiple endpoints same format | YAML is simpler |
| Need reasoning_effort translation | Python plugin with `build_extra_body` |

## How Hermes Discovers Plugins

1. **Bundled** — `<repo>/plugins/model-providers/<name>/`
2. **User** — `$HERMES_HOME/plugins/model-providers/<name>/` (user overrides bundled)
3. **Legacy** — `<repo>/providers/<name>.py`

Discovery runs lazily on first `get_provider_profile()` or `list_providers()` call.

## TypeScript Plugin Reference (DEPRECATED)

Prior versions of this skill documented `.ts` files in `~/.hermes/plugins/<name>/extension.ts`. That format is **from AgentRouter documentation, not Hermes**. Hermes model-provider plugins use **Python** in `plugins/model-providers/<name>/`. See SKILL.md for the correct approaches.
