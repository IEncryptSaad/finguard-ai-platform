# Known Limitations

- Header-based auth is intended for demos and free-tier deployments behind trusted hosting controls; production identity providers and SSO are out of scope for v1.
- Mock AI is deterministic and not a real LLM. Optional providers need separate transport plugins and keys.
- RAG is a lightweight foundation, not a vector database.
- Background tasks run in-process; there is no Redis, queue, or Kubernetes dependency.
- Supabase free tier has quota and cold-start constraints.
- Demo seed data is illustrative and not regulated financial advice.
