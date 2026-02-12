-- Migration v2 (MySQL 8.0+)
-- Adds enterprise entities: project RBAC, schedule tasks, contract-cost, document revisions, quality rectification/acceptance.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1) User-Project Role Mapping (same user can have different roles per project)
CREATE TABLE IF NOT EXISTS user_project_roles (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  project_id CHAR(36) NOT NULL,
  role ENUM('platform_admin', 'project_admin', 'supervisor', 'contractor', 'viewer') NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_project_role (user_id, project_id, role),
  CONSTRAINT fk_upr_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_upr_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2) Schedule/Planning (WBS tasks + dependencies)
CREATE TABLE IF NOT EXISTS tasks (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  parent_task_id CHAR(36) NULL,
  wbs_code VARCHAR(100) NOT NULL,
  name VARCHAR(255) NOT NULL,
  status ENUM('not_started', 'in_progress', 'completed', 'blocked') NOT NULL DEFAULT 'not_started',
  planned_start DATE,
  planned_end DATE,
  actual_start DATE,
  actual_end DATE,
  planned_days INT,
  actual_days INT,
  progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  created_by CHAR(36) NULL,
  updated_by CHAR(36) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT chk_tasks_progress CHECK (progress_percent >= 0 AND progress_percent <= 100),
  CONSTRAINT fk_tasks_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  CONSTRAINT fk_tasks_parent FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL,
  CONSTRAINT fk_tasks_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_tasks_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  UNIQUE KEY uk_tasks_project_wbs (project_id, wbs_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS task_dependencies (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  predecessor_task_id CHAR(36) NOT NULL,
  successor_task_id CHAR(36) NOT NULL,
  dependency_type ENUM('FS', 'SS', 'FF', 'SF') NOT NULL DEFAULT 'FS',
  lag_days INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_td_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  CONSTRAINT fk_td_predecessor FOREIGN KEY (predecessor_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  CONSTRAINT fk_td_successor FOREIGN KEY (successor_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  CONSTRAINT chk_td_no_self CHECK (predecessor_task_id <> successor_task_id),
  UNIQUE KEY uk_td_pair (predecessor_task_id, successor_task_id, dependency_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3) Contract-Cost Domain
CREATE TABLE IF NOT EXISTS contracts (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  contract_no VARCHAR(120) NOT NULL,
  name VARCHAR(255) NOT NULL,
  contractor_name VARCHAR(255) NOT NULL,
  currency VARCHAR(10) NOT NULL DEFAULT 'CNY',
  signed_amount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  signed_at DATE,
  status ENUM('draft', 'active', 'closed', 'terminated') NOT NULL DEFAULT 'draft',
  created_by CHAR(36) NULL,
  updated_by CHAR(36) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_contracts_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  CONSTRAINT fk_contracts_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_contracts_updated_by FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
  UNIQUE KEY uk_contracts_project_no (project_id, contract_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS boq_items (
  id CHAR(36) PRIMARY KEY,
  contract_id CHAR(36) NOT NULL,
  item_code VARCHAR(100) NOT NULL,
  item_name VARCHAR(255) NOT NULL,
  unit VARCHAR(30) NOT NULL,
  quantity DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
  unit_price DECIMAL(18,4) NOT NULL DEFAULT 0.0000,
  total_amount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_boq_contract FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
  UNIQUE KEY uk_boq_contract_item (contract_id, item_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS change_orders (
  id CHAR(36) PRIMARY KEY,
  contract_id CHAR(36) NOT NULL,
  change_no VARCHAR(120) NOT NULL,
  title VARCHAR(255) NOT NULL,
  amount_delta DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  approved_at DATE,
  status ENUM('draft', 'submitted', 'approved', 'rejected') NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_change_orders_contract FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
  UNIQUE KEY uk_change_order (contract_id, change_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS payment_certificates (
  id CHAR(36) PRIMARY KEY,
  contract_id CHAR(36) NOT NULL,
  certificate_no VARCHAR(120) NOT NULL,
  period_start DATE,
  period_end DATE,
  applied_amount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  approved_amount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  status ENUM('draft', 'submitted', 'approved', 'paid', 'rejected') NOT NULL DEFAULT 'draft',
  approved_at DATE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_payment_cert_contract FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
  UNIQUE KEY uk_payment_cert_no (contract_id, certificate_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4) Document revisions (true version history)
CREATE TABLE IF NOT EXISTS document_revisions (
  id CHAR(36) PRIMARY KEY,
  document_id CHAR(36) NOT NULL,
  revision_no INT NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_size BIGINT,
  file_sha256 CHAR(64),
  storage_path VARCHAR(500) NOT NULL,
  status ENUM('draft', 'active', 'archived') NOT NULL DEFAULT 'active',
  change_note TEXT,
  uploaded_by CHAR(36) NULL,
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_doc_revisions_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
  CONSTRAINT fk_doc_revisions_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL,
  UNIQUE KEY uk_doc_revision_no (document_id, revision_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 5) Quality rectification and acceptance entities
CREATE TABLE IF NOT EXISTS quality_rectifications (
  id CHAR(36) PRIMARY KEY,
  issue_id CHAR(36) NOT NULL,
  rectification_plan TEXT NOT NULL,
  rectification_result TEXT,
  owner_user_id CHAR(36) NULL,
  started_at DATETIME,
  submitted_at DATETIME,
  status ENUM('draft', 'in_progress', 'submitted', 'reworked', 'accepted') NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_qr_issue FOREIGN KEY (issue_id) REFERENCES quality_issues(id) ON DELETE CASCADE,
  CONSTRAINT fk_qr_owner FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS quality_acceptances (
  id CHAR(36) PRIMARY KEY,
  issue_id CHAR(36) NOT NULL,
  rectification_id CHAR(36) NULL,
  accepted_by_user_id CHAR(36) NULL,
  accepted_at DATETIME,
  result ENUM('passed', 'rejected') NOT NULL,
  comments TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_qa_issue FOREIGN KEY (issue_id) REFERENCES quality_issues(id) ON DELETE CASCADE,
  CONSTRAINT fk_qa_rectification FOREIGN KEY (rectification_id) REFERENCES quality_rectifications(id) ON DELETE SET NULL,
  CONSTRAINT fk_qa_user FOREIGN KEY (accepted_by_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 6) Practical constraints/compatibility adjustments
ALTER TABLE quality_issues
  DROP INDEX issue_code,
  ADD UNIQUE KEY uk_quality_issue_project_code (project_id, issue_code);

CREATE INDEX idx_upr_project ON user_project_roles (project_id);
CREATE INDEX idx_tasks_project ON tasks (project_id);
CREATE INDEX idx_tasks_parent ON tasks (parent_task_id);
CREATE INDEX idx_td_project ON task_dependencies (project_id);
CREATE INDEX idx_contracts_project ON contracts (project_id);
CREATE INDEX idx_boq_contract ON boq_items (contract_id);
CREATE INDEX idx_co_contract ON change_orders (contract_id);
CREATE INDEX idx_pc_contract ON payment_certificates (contract_id);
CREATE INDEX idx_doc_rev_document ON document_revisions (document_id);
CREATE INDEX idx_qr_issue ON quality_rectifications (issue_id);
CREATE INDEX idx_qa_issue ON quality_acceptances (issue_id);

SET FOREIGN_KEY_CHECKS = 1;
