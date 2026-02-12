-- Seed data for local/dev environment only.
-- Default users:
--   root / 123456
--   admin / 123456

BEGIN;

INSERT INTO organizations (id, name, code)
VALUES ('11111111-1111-1111-1111-111111111111', '默认集团', 'ORG-DEFAULT')
ON CONFLICT (code) DO NOTHING;

INSERT INTO users (username, password_hash, display_name, role, organization_id)
SELECT
  'root',
  crypt('123456', gen_salt('bf', 10)),
  'Root Admin',
  'platform_admin',
  '11111111-1111-1111-1111-111111111111'::uuid
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'root');

INSERT INTO users (username, password_hash, display_name, role, organization_id)
SELECT
  'admin',
  crypt('123456', gen_salt('bf', 10)),
  'System Admin',
  'platform_admin',
  '11111111-1111-1111-1111-111111111111'::uuid
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

COMMIT;
