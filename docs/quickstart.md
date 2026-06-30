# FinGuard v1 Quickstart

FinGuard runs locally with no paid APIs, no Docker, no Redis, and no GPU. Mock AI mode is the default.

## Requirements

- Node.js 20+
- Python 3.11+
- i5 8th gen class CPU, 16 GB RAM, less than 100 GB free SSD space

## Start locally

```bash
npm install
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
pip install -r apps/api/requirements.txt
npm run dev:api
npm run dev:web
```

Open:

- Customer chat: `http://localhost:3000`
- Admin shell: `http://localhost:3000/admin`
- API health: `http://localhost:8000/api/v1/health`
- API docs: `http://localhost:8000/api/v1/docs`

## Smoke check

```bash
curl http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/chat -H 'Content-Type: application/json' -d '{"message":"I need help disputing a card charge"}'
```

Expected: health returns `ok` with provider `mock`; chat returns a deterministic support response.
