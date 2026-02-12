-- Migration v2 (PostgreSQL 15+)
-- Adds enterprise entities: project RBAC, schedule tasks, contract-cost, document revisions, quality rectification/acceptance.

BEGIN;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status') THEN
    CREATE TYPE task_status AS ENUM ('not_started', 'in_progress', 'completed', 'blocked');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'dependency_type') THEN
    CREATE TYPE dependency_type AS ENUM ('FS', 'SS', 'FF', 'SF');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contract_status') THEN
    CREATE TYPE contract_status AS ENUM ('draft', 'active', 'closed', 'terminated');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'change_order_status') THEN
    CREATE TYPE change_order_status AS ENUM ('draft', 'submitted', 'approved', 'rejected');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_certificate_status') THEN
    CREATE TYPE payment_certificate_status AS ENUM ('draft', 'submitted', 'approved', 'paid', 'rejected');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rectification_status') THEN
    CREATE TYPE rectification_status AS ENUM ('draft', 'in_progress', 'submitted', 'reworked', 'accepted');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'acceptance_result') THEN
    CREATE TYPE acceptance_result AS ENUM ('passed', 'rejected');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS user_project_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  role user_role NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, project_id, role)
);

CREATE TABLE IF NOT EXISTS tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  wbs_code TEXT NOT NULL,
  name TEXT NOT NULL,
  status task_status NOT NULL DEFAULT 'not_started',
  planned_start DATE,
  planned_end DATE,
  actual_start DATE,
  actual_end DATE,
  planned_days INT,
  actual_days INT,
  progress_percent NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (project_id, wbs_code)
);

CREATE TABLE IF NOT EXISTS task_dependencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  predecessor_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  successor_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  dependency_type dependency_type NOT NULL DEFAULT 'FS',
  lag_days INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (predecessor_task_id <> successor_task_id),
  UNIQUE (predecessor_task_id, successor_task_id, dependency_type)
);

CREATE TABLE IF NOT EXISTS contracts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  contract_no TEXT NOT NULL,
  name TEXT NOT NULL,
  contractor_name TEXT NOT NULL,
  currency TEXT NOT NULL DEFAULT 'CNY',
  signed_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
  signed_at DATE,
  status contract_status NOT NULL DEFAULT 'draft',
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (project_id, contract_no)
);

CREATE TABLE IF NOT EXISTS boq_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
  item_code TEXT NOT NULL,
  item_name TEXT NOT NULL,
  unit TEXT NOT NULL,
  quantity NUMERIC(18,4) NOT NULL DEFAULT 0,
  unit_price NUMERIC(18,4) NOT NULL DEFAULT 0,
  total_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (contract_id, item_code)
);

CREATE TABLE IF NOT EXISTS change_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
  change_no TEXT NOT NULL,
  title TEXT NOT NULL,
  amount_delta NUMERIC(18,2) NOT NULL DEFAULT 0,
  approved_at DATE,
  status change_order_status NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (contract_id, change_no)
);

CREATE TABLE IF NOT EXISTS payment_certificates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
  certificate_no TEXT NOT NULL,
  period_start DATE,
  period_end DATE,
  applied_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
  approved_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
  status payment_certificate_status NOT NULL DEFAULT 'draft',
  approved_at DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (contract_id, certificate_no)
);

CREATE TABLE IF NOT EXISTS document_revisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  revision_no INT NOT NULL,
  file_name TEXT NOT NULL,
  file_size BIGINT,
  file_sha256 TEXT,
  storage_path TEXT NOT NULL,
  status document_status NOT NULL DEFAULT 'active',
  change_note TEXT,
  uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (document_id, revision_no)
);

CREATE TABLE IF NOT EXISTS quality_rectifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id UUID NOT NULL REFERENCES quality_issues(id) ON DELETE CASCADE,
  rectification_plan TEXT NOT NULL,
  rectification_result TEXT,
  owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  started_at TIMESTAMPTZ,
  submitted_at TIMESTAMPTZ,
  status rectification_status NOT NULL DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS quality_acceptances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id UUID NOT NULL REFERENCES quality_issues(id) ON DELETE CASCADE,
  rectification_id UUID REFERENCES quality_rectifications(id) ON DELETE SET NULL,
  accepted_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  accepted_at TIMESTAMPTZ,
  result acceptance_result NOT NULL,
  comments TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_indexes WHERE schemaname = current_schema() AND indexname = 'quality_issues_issue_code_key'
  ) THEN
    EXECUTE 'ALTER TABLE quality_issues DROP CONSTRAINT quality_issues_issue_code_key';
  END IF;
EXCEPTION
  WHEN undefined_table THEN NULL;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'uk_quality_issue_project_code'
  ) THEN
    ALTER TABLE quality_issues ADD CONSTRAINT uk_quality_issue_project_code UNIQUE (project_id, issue_code);
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_upr_project ON user_project_roles (project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks (project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks (parent_task_id);
CREATE INDEX IF NOT EXISTS idx_td_project ON task_dependencies (project_id);
CREATE INDEX IF NOT EXISTS idx_contracts_project ON contracts (project_id);
CREATE INDEX IF NOT EXISTS idx_boq_contract ON boq_items (contract_id);
CREATE INDEX IF NOT EXISTS idx_co_contract ON change_orders (contract_id);
CREATE INDEX IF NOT EXISTS idx_pc_contract ON payment_certificates (contract_id);
CREATE INDEX IF NOT EXISTS idx_doc_rev_document ON document_revisions (document_id);
CREATE INDEX IF NOT EXISTS idx_qr_issue ON quality_rectifications (issue_id);
CREATE INDEX IF NOT EXISTS idx_qa_issue ON quality_acceptances (issue_id);

DROP TRIGGER IF EXISTS trg_tasks_updated_at ON tasks;
CREATE TRIGGER trg_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_contracts_updated_at ON contracts;
CREATE TRIGGER trg_contracts_updated_at
BEFORE UPDATE ON contracts
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_boq_items_updated_at ON boq_items;
CREATE TRIGGER trg_boq_items_updated_at
BEFORE UPDATE ON boq_items
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_change_orders_updated_at ON change_orders;
CREATE TRIGGER trg_change_orders_updated_at
BEFORE UPDATE ON change_orders
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_payment_certificates_updated_at ON payment_certificates;
CREATE TRIGGER trg_payment_certificates_updated_at
BEFORE UPDATE ON payment_certificates
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_quality_rectifications_updated_at ON quality_rectifications;
CREATE TRIGGER trg_quality_rectifications_updated_at
BEFORE UPDATE ON quality_rectifications
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;
