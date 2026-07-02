import os, time, re
from app.plugins.base import AIProvider, PluginMetadata

class ProviderConfigurationError(RuntimeError): pass

class LLMProvider(AIProvider): pass

class MockLLMProvider(LLMProvider):
    metadata = PluginMetadata(name="mock", enabled=True, description="Deterministic free mock provider")
    capabilities = ["chat", "completion", "classification", "summarization"]

    _RESPONSES = [
        (("dispute", "chargeback", "unauthorized charge", "card charge"), "I can help with that card dispute. Please confirm the merchant name, transaction date, and amount—do not share your full card number. I will document the dispute details and a specialist may follow up if provisional credit review is needed."),
        (("transfer failed", "failed transfer", "wire failed", "ach failed", "payment failed", "transfer didn't go", "transfer did not go"), "I’m sorry the transfer failed. Please check whether funds were debited, confirm the destination bank nickname and amount, and avoid re-sending until we verify the status. If money left your account, I can help create a ticket for operations review."),
        (("locked", "lockout", "can't log in", "cannot log in", "account locked"), "I can help with a locked account. For your safety, use the password reset and identity verification flow in the app. If you still cannot access the account, I can escalate to an account access specialist."),
        (("refund", "refunded", "refund status", "return"), "I can check refund next steps. Refund timing depends on the merchant and payment rail; card refunds commonly take several business days after the merchant releases funds. Share the merchant, amount, and date—never full card details."),
        (("fraud", "scam", "stolen", "unauthorized", "suspicious", "compromised"), "Fraud concerns are urgent. Please freeze the affected card in the app if available, change your password from a trusted device, and review recent transactions. I can notify a specialist and help capture the suspicious activity details."),
        (("password", "security", "2fa", "mfa", "passcode", "reset login"), "For password or security issues, reset your password from the official FinGuard app or website and enable multi-factor authentication. I will never ask for your password, one-time code, or full account number."),
    ]

    @staticmethod
    def _latest_customer_text(prompt: str) -> str:
        matches = re.findall(r"customer:\s*(.*)", prompt, flags=re.IGNORECASE)
        return (matches[-1] if matches else prompt).lower()

    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        text = self._latest_customer_text(prompt)
        for keywords, response in self._RESPONSES:
            if any(keyword in text for keyword in keywords):
                return response
        return "I can help with that. Please share the issue type, relevant dates, merchant or transfer details, and the outcome you need. For your security, do not send passwords, one-time codes, full card numbers, or full account numbers."

class DisabledHTTPProvider(LLMProvider):
    def __init__(self, name: str, env_key: str, endpoint_env: str | None = None):
        self.metadata = PluginMetadata(name=name, enabled=bool(os.getenv(env_key)), description=f"{name} adapter plugin")
        self.env_key = env_key; self.endpoint_env = endpoint_env; self.capabilities = ["chat", "completion", "streaming"]
        self.timeout_seconds = float(os.getenv(f"{name.upper()}_TIMEOUT_SECONDS", "20")); self.max_retries = int(os.getenv(f"{name.upper()}_MAX_RETRIES", "2"))
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        if not os.getenv(self.env_key):
            raise ProviderConfigurationError(f"{self.metadata.name} provider is disabled. Set {self.env_key} to enable it.")
        # Production boundary: real HTTP clients can be installed by plugin packages without changing orchestrator code.
        return f"{self.metadata.name} provider is configured but no transport plugin is installed."
    async def stream(self, prompt: str, *, system_prompt: str | None = None):
        text = await self.complete(prompt, system_prompt=system_prompt)
        for token in text.split():
            yield token + " "

PROVIDER_FACTORIES = {
    "mock": lambda: MockLLMProvider(),
    "openai": lambda: DisabledHTTPProvider("openai", "OPENAI_API_KEY"),
    "anthropic": lambda: DisabledHTTPProvider("anthropic", "ANTHROPIC_API_KEY"),
    "gemini": lambda: DisabledHTTPProvider("gemini", "GEMINI_API_KEY"),
    "groq": lambda: DisabledHTTPProvider("groq", "GROQ_API_KEY"),
    "ollama": lambda: DisabledHTTPProvider("ollama", "OLLAMA_BASE_URL", "OLLAMA_BASE_URL"),
    "openrouter": lambda: DisabledHTTPProvider("openrouter", "OPENROUTER_API_KEY"),
}

def provider_from_name(name: str) -> LLMProvider:
    key = (name or "mock").lower()
    if key not in PROVIDER_FACTORIES:
        raise ValueError(f"Unknown provider '{name}'. Available: {', '.join(PROVIDER_FACTORIES)}")
    provider = PROVIDER_FACTORIES[key]()
    if key != "mock" and not provider.metadata.enabled:
        raise ProviderConfigurationError(f"Provider '{key}' is installed but disabled; configure its environment variables.")
    return provider

def provider_catalog() -> list[dict]:
    items = []
    for name, factory in PROVIDER_FACTORIES.items():
        p = factory()
        items.append({
            'name': name,
            'enabled': bool(p.metadata.enabled),
            'description': p.metadata.description,
            'capabilities': getattr(p, 'capabilities', ['chat', 'completion']),
            'configuration': {'required_env': getattr(p, 'env_key', None), 'endpoint_env': getattr(p, 'endpoint_env', None)},
            'timeout_seconds': getattr(p, 'timeout_seconds', 0),
            'max_retries': getattr(p, 'max_retries', 0),
            'healthy': name == 'mock' or bool(p.metadata.enabled),
            'estimated_cost_per_1k_tokens': 0,
        })
    return items

def provider_health(name: str) -> dict:
    key=(name or 'mock').lower()
    if key not in PROVIDER_FACTORIES:
        return {'provider': key, 'status': 'unknown', 'healthy': False, 'reason': 'Provider is not registered'}
    p=PROVIDER_FACTORIES[key]()
    healthy = key == 'mock' or bool(p.metadata.enabled)
    started=time.perf_counter()
    return {'provider': key, 'status': 'ok' if healthy else 'disabled', 'healthy': healthy, 'latency_ms': round((time.perf_counter()-started)*1000, 3), 'capabilities': getattr(p, 'capabilities', ['chat','completion'])}

def route_provider(request) -> dict:
    preferred = (getattr(request, 'preferred_provider', None) or '').lower()
    catalog = provider_catalog()
    candidates = [p for p in catalog if getattr(request, 'capability', 'chat') in p['capabilities']]
    if getattr(request, 'require_healthy', True): candidates = [p for p in candidates if p['healthy']]
    if preferred:
        match = next((p for p in candidates if p['name'] == preferred), None)
        if match: return {'provider': match['name'], 'capability': request.capability, 'reason': 'preferred provider matched', 'failover': [p['name'] for p in candidates if p['name'] != match['name']]}
    if not candidates:
        return {'provider': '', 'capability': request.capability, 'reason': 'no route available', 'failover': []}
    selected = next((p for p in candidates if p['name'] == 'mock'), candidates[0])
    return {'provider': selected['name'], 'capability': request.capability, 'reason': 'free-tier healthy failover route', 'failover': [p['name'] for p in candidates if p['name'] != selected['name']]}
