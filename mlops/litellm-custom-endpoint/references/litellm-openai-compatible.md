# LiteLLM OpenAI-Compatible Endpoints — condensed reference

Source: https://docs.litellm.ai/docs/providers/openai_compatible (read 2026-07-28)

## Key rule
> Selecting `openai` as the provider routes your request to an OpenAI-compatible endpoint using the
> upstream official OpenAI Python API library. This library REQUIRES an API key (api_key param or
> OPENAI_API_KEY env). If you don't want a fake key per request, use a provider that matches your
> endpoint (e.g. `hosted_vllm`, `llamafile`).

## To call a model behind an openai proxy — 2 changes
1. Put `openai/` in front of the model name (chat/completions) so litellm knows the route.
2. Set `api_base` to your custom endpoint base (include `/v1` postfix if that's the endpoint shape).
3. Do NOT add extra path to base url (e.g. `/v1/embedding`) — the openai client adds endpoints itself.

## Example (from the docs)
```python
import litellm
response = litellm.completion(
    model="openai/google/gemma",        # openai/ prefix -> routes as OpenAI provider
    api_key="sk-1234",                   # api key for your openai-compatible endpoint
    api_base="http://0.0.0.0:4000",      # custom base
    messages=[{"role":"user","content":"what llm are you"}],
)
```
LiteLLM forwards `google/gemma` (the `openai/` is stripped) to `api_base`.

## Proxy server config form (litellm --config)
```yaml
model_list:
  - model_name: my-model
    litellm_params:
      model: openai/<your-model-name>   # openai/ prefix -> route as OpenAI provider
      api_base: <model-api-base>         # custom openai-compatible base
      api_key: api-key
```
Note: if `api_base` 404s, ensure it has the `/v1` postfix.

## Nested prefix pattern (the one this skill exploits)
`openai/<ns>/<model>` → LiteLLM strips ONLY `openai/`, sends `<ns>/<model>` to `api_base`.
Used to reach a gateway (9router) that routes by its own `<ns>/` namespace.
