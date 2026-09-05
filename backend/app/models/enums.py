import enum

class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    MUNICIPAL_OFFICER = "municipal_officer"
    FIELD_WORKER = "field_worker"
    ADMIN = "admin"

class AssignmentStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class IssueStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"
    REOPENED = "reopened"

class IssuePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ParticipantRole(str, enum.Enum):
    ORGANIZER = "organizer"
    HOST = "host"
    PARTICIPANT = "participant"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class ParticipationStatus(str, enum.Enum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"

class TargetEntityType(str, enum.Enum):
    MEETING_SUMMARY = "meeting_summary"
    ACTION_ITEM = "action_item"
    DECISION = "decision"
    RISK = "risk"
    TRANSCRIPT_SEGMENT = "transcript_segment"

class APIScope(str, enum.Enum):
    MEETINGS_READ = "meetings:read"
    MEETINGS_WRITE = "meetings:write"
    TRANSCRIPTS_READ = "transcripts:read"
    SUMMARIES_READ = "summaries:read"
    ACTION_ITEMS_READ = "action_items:read"
    WEBHOOKS_MANAGE = "webhooks:manage"

class NotificationType(str, enum.Enum):
    ISSUE_SUBMITTED = "issue_submitted"
    ISSUE_MOVED_REVIEW = "issue_moved_review"
    ISSUE_ASSIGNED = "issue_assigned"
    ASSIGNMENT_ACCEPTED = "assignment_accepted"
    ASSIGNMENT_REJECTED = "assignment_rejected"
    ISSUE_IN_PROGRESS = "issue_in_progress"
    ISSUE_RESOLVED = "issue_resolved"
    ISSUE_CLOSED = "issue_closed"
    ISSUE_REOPENED = "issue_reopened"
    NEW_COMMENT = "new_comment"
    APPROVAL_REQUIRED = "approval_required"
    SLA_APPROACHING = "sla_approaching"
    SLA_BREACHED = "sla_breached"
    ISSUE_ESCALATED = "issue_escalated"
