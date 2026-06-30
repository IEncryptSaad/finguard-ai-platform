-- FinGuard v1 release-candidate demo seed data. Safe for repeated Supabase SQL editor runs.
insert into roles (id, description) values
  ('admin','Administrator'),
  ('agent','Support agent'),
  ('customer','Customer')
on conflict do nothing;

insert into knowledge_articles (title, body, tags) values
  ('Card dispute basics','We can help file a card dispute. Collect merchant, date, amount, and a short description. Never request or store a full card number in chat.', array['card','dispute','demo']),
  ('Account access troubleshooting','For login issues, verify identity through approved channels, suggest password reset, and escalate if account takeover is suspected.', array['login','security','demo']),
  ('Transfer delay explanation','ACH transfers can take several business days. Ask for transfer date and destination bank, then create a ticket for delayed or high-value transfers.', array['transfer','ach','demo']),
  ('PII handling reminder','Redact emails, phone numbers, card numbers, API keys, and passwords from memory, audit details, and internal notes.', array['security','pii','demo'])
on conflict do nothing;

insert into audit_logs (event_type, payload) values
  ('demo.seeded', '{"actor":"system","note":"v1 release candidate demo data loaded"}'::jsonb),
  ('demo.workflow.ready', '{"workflow":"card_dispute_triage","roles":["customer","agent","admin"]}'::jsonb)
on conflict do nothing;

insert into tickets (conversation_id, summary, status, priority, assignee, internal_notes) values
  ('demo-conv-card-dispute','Demo card dispute needs agent review','open','high','agent-demo','Seeded for product demo walkthrough'),
  ('demo-conv-transfer-delay','Demo ACH transfer delay follow-up','open','medium','agent-demo','Use to demonstrate ticket filtering and audit trail')
on conflict do nothing;
