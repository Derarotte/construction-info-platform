-- Seed data for MySQL local/dev environment
-- Default app users:
--   root / 123456
--   admin / 123456
-- Password hash algorithm in this seed: SHA2-256 hex string.

SET NAMES utf8mb4;

INSERT INTO organizations (id, name, code)
VALUES ('11111111-1111-1111-1111-111111111111', '默认集团', 'ORG-DEFAULT')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO users (id, username, password_hash, display_name, role, organization_id, is_active)
VALUES (
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  'root',
  SHA2('123456', 256),
  'Root Admin',
  'platform_admin',
  '11111111-1111-1111-1111-111111111111',
  1
)
ON DUPLICATE KEY UPDATE display_name = VALUES(display_name), role = VALUES(role), is_active = VALUES(is_active);

INSERT INTO users (id, username, password_hash, display_name, role, organization_id, is_active)
VALUES (
  'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  'admin',
  SHA2('123456', 256),
  'System Admin',
  'platform_admin',
  '11111111-1111-1111-1111-111111111111',
  1
)
ON DUPLICATE KEY UPDATE display_name = VALUES(display_name), role = VALUES(role), is_active = VALUES(is_active);
