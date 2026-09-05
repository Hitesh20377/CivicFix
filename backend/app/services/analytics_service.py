from sqlalchemy import func, extract, case
from ..extensions import db
from ..models.issue import Issue, IssueCategory
from ..models.sla import IssueSLA
from ..models.enums import IssueStatus, IssuePriority, AssignmentStatus
from ..models.municipal import Ward, Department
from ..models.assignment import IssueAssignment
from ..models.user import User
from .analytics_filters import AnalyticsFilters

class AnalyticsService:
    """Service to execute fast aggregate queries for dashboard metrics."""

    @staticmethod
    def get_overview_metrics(user, filters):
        """Returns KPI counts (Total, Open, Resolved, Critical)."""
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        
        total = base_query.count()
        open_count = base_query.filter(Issue.status.in_([
            IssueStatus.SUBMITTED, IssueStatus.UNDER_REVIEW, IssueStatus.ASSIGNED, IssueStatus.IN_PROGRESS
        ])).count()
        resolved_count = base_query.filter(Issue.status == IssueStatus.RESOLVED).count()
        closed_count = base_query.filter(Issue.status == IssueStatus.CLOSED).count()
        critical_count = base_query.filter(Issue.official_priority == IssuePriority.CRITICAL).count()
        
        return {
            "total_issues": total,
            "open_issues": open_count,
            "resolved_issues": resolved_count,
            "closed_issues": closed_count,
            "critical_issues": critical_count
        }

    @staticmethod
    def get_status_breakdown(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        result = db.session.query(
            Issue.status, func.count(Issue.id)
        ).select_from(base_query.subquery()).group_by(Issue.status).all()
        
        return [{"status": status.name, "count": count} for status, count in result]

    @staticmethod
    def get_priority_breakdown(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        result = db.session.query(
            Issue.official_priority, func.count(Issue.id)
        ).select_from(base_query.subquery()).group_by(Issue.official_priority).all()
        
        return [{"priority": p.name if p else "UNASSIGNED", "count": count} for p, count in result]

    @staticmethod
    def get_sla_metrics(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        
        # Subquery to only get SLAs for the allowed issues
        issue_subquery = base_query.with_entities(Issue.id).subquery()
        
        sla_query = db.session.query(IssueSLA).filter(IssueSLA.issue_id.in_(issue_subquery))
        
        total_slas = sla_query.count()
        if total_slas == 0:
            return {"compliance_percentage": 100, "breaches": 0, "total": 0}
            
        breaches = sla_query.filter(
            (IssueSLA.response_breached == True) | 
            (IssueSLA.resolution_breached == True)
        ).count()
        
        compliance = ((total_slas - breaches) / total_slas) * 100
        
        return {
            "compliance_percentage": round(compliance, 2),
            "breaches": breaches,
            "total": total_slas
        }

    @staticmethod
    def get_issue_heatmap(user, filters):
        """Returns geospatial data for mapping."""
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        
        # Exclude issues without coordinates
        query = base_query.filter(Issue.latitude.isnot(None), Issue.longitude.isnot(None))
        
        # Limit to 1000 points to prevent massive payload sizes for the heatmap
        issues = query.limit(1000).all()
        
        return [{
            "id": i.id,
            "latitude": i.latitude,
            "longitude": i.longitude,
            "category_id": i.category_id,
            "priority": i.official_priority.name if i.official_priority else "UNASSIGNED",
            "status": i.status.name
        } for i in issues]

    @staticmethod
    def get_category_breakdown(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        issue_subq = base_query.subquery()
        result = db.session.query(
            IssueCategory.name, func.count(issue_subq.c.id)
        ).select_from(issue_subq)\
         .outerjoin(IssueCategory, issue_subq.c.category_id == IssueCategory.id)\
         .group_by(IssueCategory.name).all()
        
        return [{"category": cat or "UNASSIGNED", "count": count} for cat, count in result]

    @staticmethod
    def get_ward_breakdown(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        issue_subq = base_query.subquery()
        result = db.session.query(
            Ward.name, func.count(issue_subq.c.id)
        ).select_from(issue_subq)\
         .outerjoin(Ward, issue_subq.c.ward_id == Ward.id)\
         .group_by(Ward.name).all()
        
        return [{"ward": ward or "UNASSIGNED", "count": count} for ward, count in result]

    @staticmethod
    def get_department_breakdown(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        issue_subq = base_query.subquery()
        
        result = db.session.query(
            Department.name, func.count(issue_subq.c.id.distinct())
        ).select_from(issue_subq)\
         .outerjoin(IssueAssignment, issue_subq.c.id == IssueAssignment.issue_id)\
         .outerjoin(Department, IssueAssignment.department_id == Department.id)\
         .group_by(Department.name).all()
         
        return [{"department": dept or "UNASSIGNED", "count": count} for dept, count in result]

    @staticmethod
    def get_resolution_time(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        resolved_issues = base_query.filter(Issue.status.in_([IssueStatus.RESOLVED, IssueStatus.CLOSED]), Issue.resolved_at.isnot(None))
        
        avg_time = db.session.query(
            func.avg(
                extract('epoch', Issue.resolved_at) - extract('epoch', Issue.created_at)
            )
        ).select_from(resolved_issues.subquery()).scalar()
        
        avg_hours = (avg_time / 3600.0) if avg_time else 0
        return {"average_resolution_time_hours": round(avg_hours, 2)}

    @staticmethod
    def get_worker_workload(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        issue_subq = base_query.with_entities(Issue.id).subquery()
        
        result = db.session.query(
            User.full_name,
            func.count(IssueAssignment.id).label('total_assigned'),
            func.sum(
                case(
                    (IssueAssignment.assignment_status == AssignmentStatus.COMPLETED, 1),
                    else_=0
                )
            ).label('completed')
        ).join(IssueAssignment, IssueAssignment.assigned_to == User.id)\
         .filter(IssueAssignment.issue_id.in_(issue_subq))\
         .group_by(User.id).all()
         
        return [{
            "worker": row.full_name,
            "assigned": row.total_assigned,
            "completed": row.completed
        } for row in result]

    @staticmethod
    def get_trends(user, filters):
        base_query = AnalyticsFilters.get_base_issue_query(user, filters)
        issue_subq = base_query.subquery()
        
        result = db.session.query(
            func.date(issue_subq.c.created_at).label('date'),
            func.count(issue_subq.c.id).label('count')
        ).select_from(issue_subq)\
         .group_by(func.date(issue_subq.c.created_at))\
         .order_by(func.date(issue_subq.c.created_at)).all()
         
        return [{"date": str(row.date), "count": row.count} for row in result]
