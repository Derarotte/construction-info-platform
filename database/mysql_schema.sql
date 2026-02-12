-- Construction Informatization Integrated Platform
-- Phase 1 schema for MySQL 8.0+

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS organizations (
  id CHAR(36) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  code VARCHAR(100) UNIQUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS projects (
  id CHAR(36) PRIMARY KEY,
  organization_id CHAR(36) NOT NULL,
  name VARCHAR(200) NOT NULL,
  code VARCHAR(100) NOT NULL UNIQUE,
  location_text VARCHAR(255),
  status ENUM('planning', 'active', 'paused', 'completed') NOT NULL DEFAULT 'planning',
  start_date DATE,
  end_date DATE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_projects_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sections (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(200) NOT NULL,
  manager_name VARCHAR(100),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_sections_project_code (project_id, code),
  CONSTRAINT fk_sections_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS work_areas (
  id CHAR(36) PRIMARY KEY,
  section_id CHAR(36) NOT NULL,
  name VARCHAR(200) NOT NULL,
  manager_name VARCHAR(100),
  status ENUM('normal', 'attention', 'warning') NOT NULL DEFAULT 'normal',
  progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  geom POINT SRID 4326 NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_work_areas_section_name (section_id, name),
  CONSTRAINT chk_work_areas_progress CHECK (progress_percent >= 0 AND progress_percent <= 100),
  CONSTRAINT fk_work_areas_section FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE,
  SPATIAL INDEX sp_idx_work_areas_geom (geom)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS quality_issues (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  section_id CHAR(36) NULL,
  work_area_id CHAR(36) NULL,
  issue_code VARCHAR(100) NOT NULL UNIQUE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  level ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium',
  status ENUM('reported', 'rectifying', 'pending_review', 'closed', 'rejected') NOT NULL DEFAULT 'reported',
  owner_name VARCHAR(100),
  reporter_name VARCHAR(100),
  reported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  due_at DATETIME,
  closed_at DATETIME,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_quality_issues_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  CONSTRAINT fk_quality_issues_section FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
  CONSTRAINT fk_quality_issues_work_area FOREIGN KEY (work_area_id) REFERENCES work_areas(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS quality_issue_events (
  id CHAR(36) PRIMARY KEY,
  issue_id CHAR(36) NOT NULL,
  from_status ENUM('reported', 'rectifying', 'pending_review', 'closed', 'rejected'),
  to_status ENUM('reported', 'rectifying', 'pending_review', 'closed', 'rejected') NOT NULL,
  action_by VARCHAR(100),
  action_note TEXT,
  action_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_quality_issue_events_issue FOREIGN KEY (issue_id) REFERENCES quality_issues(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS documents (
  id CHAR(36) PRIMARY KEY,
  project_id CHAR(36) NOT NULL,
  section_id CHAR(36) NULL,
  work_area_id CHAR(36) NULL,
  category VARCHAR(100) NOT NULL,
  title VARCHAR(255) NOT NULL,
  version VARCHAR(50) NOT NULL DEFAULT 'v1.0',
  file_name VARCHAR(255) NOT NULL,
  file_size BIGINT,
  file_sha256 CHAR(64),
  storage_path VARCHAR(500) NOT NULL,
  status ENUM('draft', 'active', 'archived') NOT NULL DEFAULT 'active',
  uploaded_by VARCHAR(100),
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_documents_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
  CONSTRAINT fk_documents_section FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL,
  CONSTRAINT fk_documents_work_area FOREIGN KEY (work_area_id) REFERENCES work_areas(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) PRIMARY KEY,
  username VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(120) NOT NULL,
  role ENUM('platform_admin', 'project_admin', 'supervisor', 'contractor', 'viewer') NOT NULL DEFAULT 'viewer',
  organization_id CHAR(36),
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  last_login_at DATETIME,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_users_org FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX idx_projects_org ON projects (organization_id);
CREATE INDEX idx_sections_project ON sections (project_id);
CREATE INDEX idx_work_areas_section ON work_areas (section_id);
CREATE INDEX idx_quality_issues_project ON quality_issues (project_id);
CREATE INDEX idx_quality_issues_status ON quality_issues (status);
CREATE INDEX idx_quality_issues_due_at ON quality_issues (due_at);
CREATE INDEX idx_quality_events_issue ON quality_issue_events (issue_id);
CREATE INDEX idx_documents_project ON documents (project_id);
CREATE INDEX idx_documents_category ON documents (category);
CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_users_org ON users (organization_id);

SET FOREIGN_KEY_CHECKS = 1;
