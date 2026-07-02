from fastapi.testclient import TestClient
from app.main import app
from app.agent.llm import MockLLMProvider


def test_mock_keyword_responses_are_deterministic():
    import asyncio
    provider = MockLLMProvider()
    cases = {
        'customer: I need to dispute a card charge': 'card dispute',
        'customer: my transfer failed yesterday': 'transfer failed',
        'customer: account locked cannot log in': 'locked account',
        'customer: where is my refund': 'refund',
        'customer: I think this is fraud': 'Fraud concerns',
        'customer: password and 2FA problem': 'password or security',
        'customer: I need help': 'issue type',
    }
    for prompt, expected in cases.items():
        assert expected in asyncio.run(provider.complete(prompt))


def test_ticket_creation_from_chat_persists_and_appears_in_admin():
    client = TestClient(app)
    chat = client.post('/api/v1/chat', json={'message': 'My transfer failed and I need support'}).json()
    created = client.post('/api/v1/chat/tickets', json={
        'conversation_id': chat['conversation_id'],
        'summary': 'Customer requested review of failed transfer',
        'priority': 'high',
    })
    assert created.status_code == 200
    ticket = created.json()
    assert ticket['status'] == 'open'
    assert ticket['conversation_id'] == chat['conversation_id']

    tickets = client.get('/api/v1/tickets').json()
    assert any(item['id'] == ticket['id'] for item in tickets)
    summary = client.get('/api/v1/admin/summary').json()
    assert summary['open_tickets'] >= 1
    assert summary['conversations'] >= 1


def test_dashboard_read_only_access_and_sensitive_settings_not_exposed(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setenv('DEMO_ADMIN_READ_ACCESS', 'true')
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        assert client.get('/api/v1/admin/summary').status_code == 200
        assert client.get('/api/v1/tickets').status_code == 200
        assert client.get('/api/v1/knowledge').status_code == 200
        settings_response = client.get('/api/v1/settings')
        assert settings_response.status_code == 401
        assert 'active_ai_provider' not in settings_response.text
        assert client.post('/api/v1/tickets', json={'conversation_id':'x','summary':'protected'}).status_code == 401
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        monkeypatch.delenv('APP_ENV', raising=False)
        monkeypatch.delenv('DEMO_ADMIN_READ_ACCESS', raising=False)
        get_settings.cache_clear()
