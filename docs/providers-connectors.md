# Provider, Plugin, and Connector Guide

FinGuard v1 keeps all external integrations optional.

## AI providers

Default:

```bash
LLM_PROVIDER=mock
```

Optional providers are registered but disabled until their environment variable is present:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `OLLAMA_BASE_URL`
- `OPENROUTER_API_KEY`

Use `/api/v1/providers`, `/api/v1/providers/{provider}/health`, and `/api/v1/providers/route` to inspect routing without making paid API calls.

## Connectors

Connector endpoints expose catalog, health, and test surfaces. Keep connector secrets blank for the free-tier release candidate. A connector should fail closed as disabled rather than blocking startup.

## Plugins

Plugin metadata should describe capabilities, required environment, and whether the plugin is enabled. Avoid importing paid SDKs in core startup paths; plugin packages can add transports later behind the existing interfaces.
