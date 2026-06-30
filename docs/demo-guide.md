# Product Demo Guide

## Demo roles

Use header auth in API demos:

- Admin: `X-FinGuard-Role: admin`
- Agent: `X-FinGuard-Role: agent`
- Customer: `X-FinGuard-Role: customer`

## Seeded demo data

Run `apps/api/supabase/seed.sql` after migrations. It adds roles, security/support knowledge, audit events, and example tickets.

## Walkthrough

1. Open the customer chat and ask: "I need to dispute a suspicious card charge."
2. Show mock AI response and explain no paid model key is required.
3. Open the admin shell and review conversations, tickets, audit logs, knowledge, settings, providers, prompts, actions, connectors, and RAG status.
4. Ingest a small text knowledge file and query `/api/v1/rag/query`.
5. Run `/api/v1/providers/route` for `chat` and show mock provider selection.
6. Run a safe action such as `notify_admin` and show the audit trail.

## Screenshot placeholders

Place demo screenshots in `docs/assets/demo/` when capturing release media:

- `01-chat.png`
- `02-admin-summary.png`
- `03-ticket-detail.png`
- `04-provider-health.png`
- `05-rag-query.png`
