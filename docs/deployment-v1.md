# Deployment Guide: Vercel + Render + Supabase

This guide keeps the release candidate on free-tier infrastructure.

## 1. Supabase

1. Create a free Supabase project.
2. Run migrations in order from `apps/api/supabase/migrations`.
3. Run `apps/api/supabase/seed.sql` for demo data.
4. Copy the project URL and service role key for the backend only.

## 2. Render backend

Use `render.yaml` or create a free Web Service manually:

- Root directory: `apps/api`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/v1/health`

Environment:

```bash
APP_ENV=production
AUTH_REQUIRED=true
PUBLIC_CUSTOMER_CHAT=false
LLM_PROVIDER=mock
CORS_ORIGINS=https://your-vercel-app.vercel.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
RATE_LIMIT_PER_MINUTE=60
```

## 3. Vercel frontend

Deploy `apps/web` as the frontend app. Set:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
```

## Production-safe defaults

- Mock AI remains enabled unless an optional provider is deliberately configured.
- `AUTH_REQUIRED=true` protects admin and mutation APIs.
- `PUBLIC_CUSTOMER_CHAT=false` keeps anonymous production chat disabled by default.
- CORS must be an explicit Vercel origin in production.
