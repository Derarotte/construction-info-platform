import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    AcceptanceResult,
    ChangeOrderStatus,
    ContractStatus,
    DependencyType,
    DocumentStatus,
    PaymentCertificateStatus,
    ProjectStatus,
    QualityIssueStatus,
    QualityLevel,
    RectificationStatus,
    TaskStatus,
    UserRole,
    WorkAreaStatus,
)


def uuid_str() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str | None] = mapped_column(String(100), unique=True)


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location_text: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus, native_enum=False), default=ProjectStatus.planning)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)


class Section(Base, TimestampMixin):
    __tablename__ = "sections"
    __table_args__ = (UniqueConstraint("project_id", "code", name="uk_sections_project_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    manager_name: Mapped[str | None] = mapped_column(String(100))


class WorkArea(Base, TimestampMixin):
    __tablename__ = "work_areas"
    __table_args__ = (UniqueConstraint("section_id", "name", name="uk_work_areas_section_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    section_id: Mapped[str] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    manager_name: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[WorkAreaStatus] = mapped_column(
        Enum(WorkAreaStatus, native_enum=False), default=WorkAreaStatus.normal, nullable=False
    )
    progress_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), default=UserRole.viewer, nullable=False)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)


class UserProjectRole(Base):
    __tablename__ = "user_project_roles"
    __table_args__ = (UniqueConstraint("user_id", "project_id", "role", name="uk_user_project_role"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    __table_args__ = (UniqueConstraint("project_id", "wbs_code", name="uk_tasks_project_wbs"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_task_id: Mapped[str | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"))
    wbs_code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False), default=TaskStatus.not_started)
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_end: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_end: Mapped[date | None] = mapped_column(Date)
    planned_days: Mapped[int | None] = mapped_column(Integer)
    actual_days: Mapped[int | None] = mapped_column(Integer)
    progress_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    parent: Mapped["Task | None"] = relationship(remote_side="Task.id")


class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    __table_args__ = (
        UniqueConstraint(
            "predecessor_task_id",
            "successor_task_id",
            "dependency_type",
            name="uk_td_pair",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    predecessor_task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    successor_task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    dependency_type: Mapped[DependencyType] = mapped_column(
        Enum(DependencyType, native_enum=False), default=DependencyType.fs, nullable=False
    )
    lag_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class QualityIssue(Base, TimestampMixin):
    __tablename__ = "quality_issues"
    __table_args__ = (UniqueConstraint("project_id", "issue_code", name="uk_quality_issue_project_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_id: Mapped[str | None] = mapped_column(ForeignKey("sections.id", ondelete="SET NULL"))
    work_area_id: Mapped[str | None] = mapped_column(ForeignKey("work_areas.id", ondelete="SET NULL"))
    issue_code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    level: Mapped[QualityLevel] = mapped_column(Enum(QualityLevel, native_enum=False), default=QualityLevel.medium)
    status: Mapped[QualityIssueStatus] = mapped_column(
        Enum(QualityIssueStatus, native_enum=False), default=QualityIssueStatus.reported, nullable=False
    )
    owner_name: Mapped[str | None] = mapped_column(String(100))
    reporter_name: Mapped[str | None] = mapped_column(String(100))
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)


class QualityIssueEvent(Base):
    __tablename__ = "quality_issue_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    issue_id: Mapped[str] = mapped_column(ForeignKey("quality_issues.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[QualityIssueStatus | None] = mapped_column(Enum(QualityIssueStatus, native_enum=False))
    to_status: Mapped[QualityIssueStatus] = mapped_column(Enum(QualityIssueStatus, native_enum=False), nullable=False)
    action_by: Mapped[str | None] = mapped_column(String(100))
    action_note: Mapped[str | None] = mapped_column(Text)
    action_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class QualityRectification(Base, TimestampMixin):
    __tablename__ = "quality_rectifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    issue_id: Mapped[str] = mapped_column(ForeignKey("quality_issues.id", ondelete="CASCADE"), nullable=False)
    rectification_plan: Mapped[str] = mapped_column(Text, nullable=False)
    rectification_result: Mapped[str | None] = mapped_column(Text)
    owner_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[RectificationStatus] = mapped_column(
        Enum(RectificationStatus, native_enum=False), default=RectificationStatus.draft, nullable=False
    )


class QualityAcceptance(Base):
    __tablename__ = "quality_acceptances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    issue_id: Mapped[str] = mapped_column(ForeignKey("quality_issues.id", ondelete="CASCADE"), nullable=False)
    rectification_id: Mapped[str | None] = mapped_column(
        ForeignKey("quality_rectifications.id", ondelete="SET NULL")
    )
    accepted_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime)
    result: Mapped[AcceptanceResult] = mapped_column(Enum(AcceptanceResult, native_enum=False), nullable=False)
    comments: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_id: Mapped[str | None] = mapped_column(ForeignKey("sections.id", ondelete="SET NULL"))
    work_area_id: Mapped[str | None] = mapped_column(ForeignKey("work_areas.id", ondelete="SET NULL"))
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="v1.0", nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    file_sha256: Mapped[str | None] = mapped_column(String(64))
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, native_enum=False), default=DocumentStatus.active, nullable=False
    )
    uploaded_by: Mapped[str | None] = mapped_column(String(100))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class DocumentRevision(Base):
    __tablename__ = "document_revisions"
    __table_args__ = (UniqueConstraint("document_id", "revision_no", name="uk_doc_revision_no"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    revision_no: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    file_sha256: Mapped[str | None] = mapped_column(String(64))
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, native_enum=False), default=DocumentStatus.active, nullable=False
    )
    change_note: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"
    __table_args__ = (UniqueConstraint("project_id", "contract_no", name="uk_contracts_project_no"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    contract_no: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contractor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="CNY", nullable=False)
    signed_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    signed_at: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, native_enum=False), default=ContractStatus.draft, nullable=False
    )
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class BoqItem(Base, TimestampMixin):
    __tablename__ = "boq_items"
    __table_args__ = (UniqueConstraint("contract_id", "item_code", name="uk_boq_contract_item"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    item_code: Mapped[str] = mapped_column(String(100), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=0, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)


class ChangeOrder(Base, TimestampMixin):
    __tablename__ = "change_orders"
    __table_args__ = (UniqueConstraint("contract_id", "change_no", name="uk_change_order"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    change_no: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_delta: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    approved_at: Mapped[date | None] = mapped_column(Date)
    status: Mapped[ChangeOrderStatus] = mapped_column(
        Enum(ChangeOrderStatus, native_enum=False), default=ChangeOrderStatus.draft, nullable=False
    )


class PaymentCertificate(Base, TimestampMixin):
    __tablename__ = "payment_certificates"
    __table_args__ = (UniqueConstraint("contract_id", "certificate_no", name="uk_payment_cert_no"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    contract_id: Mapped[str] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    certificate_no: Mapped[str] = mapped_column(String(120), nullable=False)
    period_start: Mapped[date | None] = mapped_column(Date)
    period_end: Mapped[date | None] = mapped_column(Date)
    applied_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    approved_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    status: Mapped[PaymentCertificateStatus] = mapped_column(
        Enum(PaymentCertificateStatus, native_enum=False),
        default=PaymentCertificateStatus.draft,
        nullable=False,
    )
    approved_at: Mapped[date | None] = mapped_column(Date)
