"""init v2 schema

Revision ID: 20260212_0001
Revises:
Create Date: 2026-02-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260212_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=100)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("location_text", sa.String(length=255)),
        sa.Column(
            "status",
            sa.Enum("planning", "active", "paused", "completed", name="projectstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "platform_admin", "project_admin", "supervisor", "contractor", "viewer", name="userrole", native_enum=False
            ),
            nullable=False,
        ),
        sa.Column("organization_id", sa.String(length=36)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "sections",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("manager_name", sa.String(length=100)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("project_id", "code", name="uk_sections_project_code"),
    )

    op.create_table(
        "work_areas",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("section_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("manager_name", sa.String(length=100)),
        sa.Column(
            "status",
            sa.Enum("normal", "attention", "warning", name="workareastatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("progress_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("section_id", "name", name="uk_work_areas_section_name"),
    )

    op.create_table(
        "user_project_roles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column(
            "role",
            sa.Enum(
                "platform_admin", "project_admin", "supervisor", "contractor", "viewer", name="userrole2", native_enum=False
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "project_id", "role", name="uk_user_project_role"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("parent_task_id", sa.String(length=36)),
        sa.Column("wbs_code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("not_started", "in_progress", "completed", "blocked", name="taskstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("planned_start", sa.Date()),
        sa.Column("planned_end", sa.Date()),
        sa.Column("actual_start", sa.Date()),
        sa.Column("actual_end", sa.Date()),
        sa.Column("planned_days", sa.Integer()),
        sa.Column("actual_days", sa.Integer()),
        sa.Column("progress_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_by", sa.String(length=36)),
        sa.Column("updated_by", sa.String(length=36)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_task_id"], ["tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("project_id", "wbs_code", name="uk_tasks_project_wbs"),
    )

    op.create_table(
        "task_dependencies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("predecessor_task_id", sa.String(length=36), nullable=False),
        sa.Column("successor_task_id", sa.String(length=36), nullable=False),
        sa.Column("dependency_type", sa.Enum("FS", "SS", "FF", "SF", name="dependencytype", native_enum=False), nullable=False),
        sa.Column("lag_days", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["predecessor_task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["successor_task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("predecessor_task_id", "successor_task_id", "dependency_type", name="uk_td_pair"),
    )

    op.create_table(
        "quality_issues",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("section_id", sa.String(length=36)),
        sa.Column("work_area_id", sa.String(length=36)),
        sa.Column("issue_code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("level", sa.Enum("low", "medium", "high", "critical", name="qualitylevel", native_enum=False), nullable=False),
        sa.Column(
            "status",
            sa.Enum("reported", "rectifying", "pending_review", "closed", "rejected", name="qualityissuestatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("owner_name", sa.String(length=100)),
        sa.Column("reporter_name", sa.String(length=100)),
        sa.Column("reported_at", sa.DateTime(), nullable=False),
        sa.Column("due_at", sa.DateTime()),
        sa.Column("closed_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["work_area_id"], ["work_areas.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("project_id", "issue_code", name="uk_quality_issue_project_code"),
    )

    op.create_table(
        "quality_issue_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("issue_id", sa.String(length=36), nullable=False),
        sa.Column(
            "from_status",
            sa.Enum("reported", "rectifying", "pending_review", "closed", "rejected", name="qualityissuestatus2", native_enum=False),
        ),
        sa.Column(
            "to_status",
            sa.Enum("reported", "rectifying", "pending_review", "closed", "rejected", name="qualityissuestatus3", native_enum=False),
            nullable=False,
        ),
        sa.Column("action_by", sa.String(length=100)),
        sa.Column("action_note", sa.Text()),
        sa.Column("action_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["quality_issues.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "quality_rectifications",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("issue_id", sa.String(length=36), nullable=False),
        sa.Column("rectification_plan", sa.Text(), nullable=False),
        sa.Column("rectification_result", sa.Text()),
        sa.Column("owner_user_id", sa.String(length=36)),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("submitted_at", sa.DateTime()),
        sa.Column(
            "status",
            sa.Enum("draft", "in_progress", "submitted", "reworked", "accepted", name="rectificationstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["quality_issues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "quality_acceptances",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("issue_id", sa.String(length=36), nullable=False),
        sa.Column("rectification_id", sa.String(length=36)),
        sa.Column("accepted_by_user_id", sa.String(length=36)),
        sa.Column("accepted_at", sa.DateTime()),
        sa.Column("result", sa.Enum("passed", "rejected", name="acceptanceresult", native_enum=False), nullable=False),
        sa.Column("comments", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["quality_issues.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rectification_id"], ["quality_rectifications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["accepted_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("section_id", sa.String(length=36)),
        sa.Column("work_area_id", sa.String(length=36)),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.BigInteger()),
        sa.Column("file_sha256", sa.String(length=64)),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "active", "archived", name="documentstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("uploaded_by", sa.String(length=100)),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["work_area_id"], ["work_areas.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "document_revisions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.BigInteger()),
        sa.Column("file_sha256", sa.String(length=64)),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "active", "archived", name="documentstatus2", native_enum=False),
            nullable=False,
        ),
        sa.Column("change_note", sa.Text()),
        sa.Column("uploaded_by", sa.String(length=36)),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("document_id", "revision_no", name="uk_doc_revision_no"),
    )

    op.create_table(
        "contracts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("contract_no", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contractor_name", sa.String(length=255), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("signed_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("signed_at", sa.Date()),
        sa.Column(
            "status",
            sa.Enum("draft", "active", "closed", "terminated", name="contractstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_by", sa.String(length=36)),
        sa.Column("updated_by", sa.String(length=36)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("project_id", "contract_no", name="uk_contracts_project_no"),
    )

    op.create_table(
        "boq_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=36), nullable=False),
        sa.Column("item_code", sa.String(length=100), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=False),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("contract_id", "item_code", name="uk_boq_contract_item"),
    )

    op.create_table(
        "change_orders",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=36), nullable=False),
        sa.Column("change_no", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("amount_delta", sa.Numeric(18, 2), nullable=False),
        sa.Column("approved_at", sa.Date()),
        sa.Column(
            "status",
            sa.Enum("draft", "submitted", "approved", "rejected", name="changeorderstatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("contract_id", "change_no", name="uk_change_order"),
    )

    op.create_table(
        "payment_certificates",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("contract_id", sa.String(length=36), nullable=False),
        sa.Column("certificate_no", sa.String(length=120), nullable=False),
        sa.Column("period_start", sa.Date()),
        sa.Column("period_end", sa.Date()),
        sa.Column("applied_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("approved_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "submitted", "approved", "paid", "rejected", name="paymentcertificatestatus", native_enum=False),
            nullable=False,
        ),
        sa.Column("approved_at", sa.Date()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("contract_id", "certificate_no", name="uk_payment_cert_no"),
    )

    op.create_index("idx_projects_org", "projects", ["organization_id"])
    op.create_index("idx_sections_project", "sections", ["project_id"])
    op.create_index("idx_work_areas_section", "work_areas", ["section_id"])
    op.create_index("idx_users_org", "users", ["organization_id"])
    op.create_index("idx_upr_project", "user_project_roles", ["project_id"])
    op.create_index("idx_tasks_project", "tasks", ["project_id"])
    op.create_index("idx_td_project", "task_dependencies", ["project_id"])
    op.create_index("idx_quality_issues_project", "quality_issues", ["project_id"])
    op.create_index("idx_quality_events_issue", "quality_issue_events", ["issue_id"])
    op.create_index("idx_doc_rev_document", "document_revisions", ["document_id"])
    op.create_index("idx_contracts_project", "contracts", ["project_id"])
    op.create_index("idx_boq_contract", "boq_items", ["contract_id"])


def downgrade() -> None:
    op.drop_index("idx_boq_contract", table_name="boq_items")
    op.drop_index("idx_contracts_project", table_name="contracts")
    op.drop_index("idx_doc_rev_document", table_name="document_revisions")
    op.drop_index("idx_quality_events_issue", table_name="quality_issue_events")
    op.drop_index("idx_quality_issues_project", table_name="quality_issues")
    op.drop_index("idx_td_project", table_name="task_dependencies")
    op.drop_index("idx_tasks_project", table_name="tasks")
    op.drop_index("idx_upr_project", table_name="user_project_roles")
    op.drop_index("idx_users_org", table_name="users")
    op.drop_index("idx_work_areas_section", table_name="work_areas")
    op.drop_index("idx_sections_project", table_name="sections")
    op.drop_index("idx_projects_org", table_name="projects")

    op.drop_table("payment_certificates")
    op.drop_table("change_orders")
    op.drop_table("boq_items")
    op.drop_table("contracts")
    op.drop_table("document_revisions")
    op.drop_table("documents")
    op.drop_table("quality_acceptances")
    op.drop_table("quality_rectifications")
    op.drop_table("quality_issue_events")
    op.drop_table("quality_issues")
    op.drop_table("task_dependencies")
    op.drop_table("tasks")
    op.drop_table("user_project_roles")
    op.drop_table("work_areas")
    op.drop_table("sections")
    op.drop_table("users")
    op.drop_table("projects")
    op.drop_table("organizations")
