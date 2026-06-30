# Architecture Overview: v1 Release Candidate

FinGuard is a small monorepo with a Next.js frontend, FastAPI backend, shared contracts, and Supabase-compatible persistence.

## Request flow

1. The web app calls `/api/v1/*` endpoints through `apps/web/lib/api.ts`.
2. FastAPI routes validate payloads and enforce header-based RBAC.
3. Chat requests enter `AgentOrchestrator` for redaction, guardrails, prompt rendering, provider selection, audit logging, and ticket handoff.
4. Services persist through the repository boundary, using local fallback for development or Supabase for production.

## Runtime boundaries

- Providers: mock-first AI adapter with disabled-by-default optional providers.
- Tools/actions: registered in the action runtime and auditable.
- Prompts: versioned templates with lifecycle status and rollback endpoints.
- Knowledge/RAG: article ingestion plus lightweight local chunk/query foundation.
- Connectors: catalog and health checks; no external connector runs unless configured.

## Release guardrails

- No Redis or background worker is required.
- No paid APIs are required.
- Supabase is optional locally but recommended for deployed persistence.
- Production CORS cannot be wildcarded.
