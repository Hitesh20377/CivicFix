from datetime import datetime
from ..models.issue import Issue
from ..models.user import User
from ..models.municipal import EmployeeProfile
from ..models.assignment import IssueAssignment
from ..models.enums import UserRole

class AnalyticsFilters:
    """Service to build SQLAlchemy queries with RBAC and user-defined filters applied."""
    
    @staticmethod
    def get_base_issue_query(user: User, filters: dict):
        """
        Returns a base SQLAlchemy query for Issues, with RBAC constraints applied.
        """
        query = Issue.query

        # 1. Apply RBAC constraints based on user role
        if user.role == UserRole.CITIZEN:
            # Citizens can only see their own issues
            query = query.filter(Issue.created_by == user.id)
            
        elif user.role == UserRole.MUNICIPAL_OFFICER:
            # Officers can see issues in their ward or department
            employee = EmployeeProfile.query.filter_by(user_id=user.id).first()
            if employee:
                query = query.filter(
                    (Issue.ward_id == employee.ward_id)
                    # Issue no longer has department_id directly, would need to map via category_id -> department in real life, but for now we'll just filter by ward if employee is present
                )
                
        elif user.role == UserRole.FIELD_WORKER:
            # Workers can only see issues explicitly assigned to them
            assigned_issue_ids = [
                a.issue_id for a in IssueAssignment.query.filter_by(assigned_to=user.id).all()
            ]
            query = query.filter(Issue.id.in_(assigned_issue_ids))
            
        elif user.role == UserRole.ADMIN:
            # Admins can see everything (no base filter required)
            pass

        # 2. Apply explicit user-defined filters (if permitted)
        
        if 'start_date' in filters and filters['start_date']:
            try:
                start = datetime.fromisoformat(filters['start_date'].replace('Z', '+00:00'))
                query = query.filter(Issue.created_at >= start)
            except ValueError:
                pass
                
        if 'end_date' in filters and filters['end_date']:
            try:
                end = datetime.fromisoformat(filters['end_date'].replace('Z', '+00:00'))
                query = query.filter(Issue.created_at <= end)
            except ValueError:
                pass
                
        if 'ward_id' in filters and filters['ward_id']:
            query = query.filter(Issue.ward_id == int(filters['ward_id']))
            
        if 'category_id' in filters and filters['category_id']:
            query = query.filter(Issue.category_id == int(filters['category_id']))
            
        if 'status' in filters and filters['status']:
            query = query.filter(Issue.status.name == filters['status'].upper())
            
        if 'priority' in filters and filters['priority']:
            query = query.filter(Issue.official_priority.name == filters['priority'].upper())

        return query
