from fastapi.testclient import TestClient

from app.main import app


def test_release_health_and_admin_core_smoke():
    client = TestClient(app)
    health = client.get('/api/v1/health')
    assert health.status_code == 200
    assert health.json()['provider'] == 'mock'

    admin = client.get('/api/v1/admin/summary')
    assert admin.status_code == 200
    assert {'open_tickets', 'conversations', 'audit_events', 'knowledge_articles'}.issubset(admin.json())


def test_release_chat_mock_stream_and_audit_smoke():
    client = TestClient(app)
    chat = client.post('/api/v1/chat', json={'message': 'Please help with a suspicious card charge.'})
    assert chat.status_code == 200
    assert 'I can help with that' in chat.json()['message']

    with client.stream('POST', '/api/v1/chat/stream', json={'message': 'Stream a safe support answer.'}) as response:
        body = ''.join(response.iter_text())
    assert response.status_code == 200
    assert 'event: metadata' in body
    assert 'event: message.done' in body

    audit = client.get('/api/v1/audit')
    assert audit.status_code == 200
    assert len(audit.json()) >= 1


def test_release_provider_prompt_action_knowledge_rag_smoke():
    client = TestClient(app)
    route = client.post('/api/v1/providers/route', json={'capability': 'chat'})
    assert route.status_code == 200
    assert route.json()['provider'] == 'mock'

    prompt = client.post('/api/v1/prompts', json={
        'name': 'release.smoke',
        'category': 'support',
        'template': 'Answer safely: {{input}}',
        'status': 'active',
    })
    assert prompt.status_code == 200
    prompt_id = prompt.json()['id']
    assert client.patch(f'/api/v1/prompts/{prompt_id}/status', json={'status': 'retired'}).status_code == 200

    action = client.post('/api/v1/actions/notify_admin/run', json={'payload': {'message': 'release smoke'}})
    assert action.status_code == 200
    assert action.json()['status'] == 'succeeded'

    article = client.post('/api/v1/knowledge', json={
        'title': 'Release smoke article',
        'body': 'Release candidate knowledge article for card dispute support.',
        'tags': ['release', 'smoke'],
    })
    assert article.status_code == 200
    assert client.post('/api/v1/rag/index').status_code == 200
    rag = client.post('/api/v1/rag/query', json={'query': 'card dispute support', 'top_k': 3})
    assert rag.status_code == 200
    assert 'citations' in rag.json()


def test_release_knowledge_ingestion_and_connector_smoke():
    client = TestClient(app)
    ingest = client.post(
        '/api/v1/knowledge/ingest',
        files={'file': ('release-smoke.md', b'# Release Smoke\nKnowledge ingestion works in mock mode.', 'text/markdown')},
    )
    assert ingest.status_code == 200
    assert ingest.json()['title'] == 'release-smoke'

    connectors = client.get('/api/v1/connectors')
    assert connectors.status_code == 200
    names = {connector['name'] for connector in connectors.json()}
    assert {'webhook', 'email', 'slack'}.issubset(names)
