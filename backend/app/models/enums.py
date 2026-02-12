from enum import StrEnum


class ProjectStatus(StrEnum):
    planning = "planning"
    active = "active"
    paused = "paused"
    completed = "completed"


class WorkAreaStatus(StrEnum):
    normal = "normal"
    attention = "attention"
    warning = "warning"


class QualityLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class QualityIssueStatus(StrEnum):
    reported = "reported"
    rectifying = "rectifying"
    pending_review = "pending_review"
    closed = "closed"
    rejected = "rejected"


class DocumentStatus(StrEnum):
    draft = "draft"
    active = "active"
    archived = "archived"


class UserRole(StrEnum):
    platform_admin = "platform_admin"
    project_admin = "project_admin"
    supervisor = "supervisor"
    contractor = "contractor"
    viewer = "viewer"


class TaskStatus(StrEnum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"


class DependencyType(StrEnum):
    fs = "FS"
    ss = "SS"
    ff = "FF"
    sf = "SF"


class ContractStatus(StrEnum):
    draft = "draft"
    active = "active"
    closed = "closed"
    terminated = "terminated"


class ChangeOrderStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class PaymentCertificateStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    paid = "paid"
    rejected = "rejected"


class RectificationStatus(StrEnum):
    draft = "draft"
    in_progress = "in_progress"
    submitted = "submitted"
    reworked = "reworked"
    accepted = "accepted"


class AcceptanceResult(StrEnum):
    passed = "passed"
    rejected = "rejected"
