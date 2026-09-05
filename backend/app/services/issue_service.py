from datetime import datetime
import uuid
from ..extensions import db
from ..models.issue import Issue, IssueCategory, IssueStatusHistory, IssueAttachment
from ..models.enums import IssueStatus, IssuePriority

class IssueService:
    @staticmethod
    def _generate_issue_number():
        """Generates a unique issue number (e.g., ISS-20231015-XYZ123)"""
        date_str = datetime.utcnow().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:6].upper()
        return f"ISS-{date_str}-{unique_id}"

    @staticmethod
    def create_issue(user_id, data):
        """Creates a new issue reported by a citizen."""
        issue = Issue(
            issue_number=IssueService._generate_issue_number(),
            title=data.get('title'),
            description=data.get('description'),
            category_id=data.get('category_id'),
            created_by=user_id,
            ward_id=data.get('ward_id'),
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            citizen_priority=data.get('citizen_priority', IssuePriority.LOW),
            status=IssueStatus.SUBMITTED
        )
        
        db.session.add(issue)
        db.session.commit()
        
        # Add initial status history
        history = IssueStatusHistory(
            issue_id=issue.id,
            new_status=IssueStatus.SUBMITTED,
            changed_by=user_id,
            comment="Issue created"
        )
        db.session.add(history)
        db.session.commit()
        
        # Trigger background tasks
        from ..tasks.sla_tasks import calculate_issue_sla
        from ..tasks.notification_tasks import process_issue_event
        
        calculate_issue_sla.delay(issue.id)
        process_issue_event.delay(issue.id, 'issue_submitted')
        
        return issue

    @staticmethod
    def get_issue_by_id(issue_id, user_id=None, role=None):
        issue = Issue.query.get(issue_id)
        if not issue or not user_id or not role:
            return issue
            
        if role == 'CITIZEN' and issue.created_by != user_id:
            return None
            
        if role == 'MUNICIPAL_OFFICER':
            from ..models.municipal import EmployeeProfile
            employee = EmployeeProfile.query.filter_by(user_id=user_id).first()
            if not employee or employee.ward_id != issue.ward_id:
                return None
                
        if role == 'FIELD_WORKER':
            from ..models.assignment import IssueAssignment
            assignment = IssueAssignment.query.filter_by(issue_id=issue_id, assigned_to=user_id).first()
            if not assignment:
                return None
                
        return issue

    @staticmethod
    def get_issue_by_number(issue_number):
        return Issue.query.filter_by(issue_number=issue_number).first()

    @staticmethod
    def get_issues(user_id=None, role=None, page=1, per_page=20, status=None, category_id=None):
        """Get issues based on role and filters"""
        query = Issue.query

        if role == 'CITIZEN' and user_id:
            query = query.filter_by(created_by=user_id)
        elif role == 'MUNICIPAL_OFFICER' and user_id:
            from ..models.municipal import EmployeeProfile
            employee = EmployeeProfile.query.filter_by(user_id=user_id).first()
            if employee:
                query = query.filter_by(ward_id=employee.ward_id)
            else:
                # If they have no ward, they shouldn't see anything
                query = query.filter(Issue.id == -1) 
        elif role == 'FIELD_WORKER' and user_id:
            from ..models.assignment import IssueAssignment
            assigned_issue_ids = [
                a.issue_id for a in IssueAssignment.query.filter_by(assigned_to=user_id).all()
            ]
            query = query.filter(Issue.id.in_(assigned_issue_ids))
        elif role == 'ADMIN':
            pass
        else:
            # Deny by default if role is not recognized or user_id missing
            query = query.filter(Issue.id == -1)
            
        if status:
            if isinstance(status, str):
                status = IssueStatus[status]
            query = query.filter_by(status=status)
            
        if category_id:
            query = query.filter_by(category_id=category_id)

        from sqlalchemy.orm import joinedload
        
        # Optimize queries by eagerly loading nested relationships used by marshmallow
        query = query.options(
            joinedload(Issue.attachments),
            joinedload(Issue.status_history)
        )
        
        # Order by newest first
        query = query.order_by(Issue.created_at.desc())
        
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def update_issue_status(issue_id, user_id, new_status, comment=None):
        issue = Issue.query.get(issue_id)
        if not issue:
            return None
            
        if isinstance(new_status, str):
            new_status = IssueStatus[new_status]

        old_status = issue.status
        if old_status == new_status:
            return issue

        issue.status = new_status
        issue.updated_at = datetime.utcnow()
        
        if new_status == IssueStatus.RESOLVED:
            issue.resolved_at = datetime.utcnow()
        elif new_status == IssueStatus.CLOSED:
            issue.closed_at = datetime.utcnow()
            
        db.session.add(issue)
        
        history = IssueStatusHistory(
            issue_id=issue.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=user_id,
            comment=comment
        )
        db.session.add(history)
        db.session.commit()
        
        # Trigger background task
        from ..tasks.notification_tasks import process_issue_event
        event_type = 'issue_resolved' if new_status == IssueStatus.RESOLVED else 'status_changed'
        process_issue_event.delay(issue.id, event_type, metadata={'new_status': new_status.name})
        
        return issue

    @staticmethod
    def get_categories():
        return IssueCategory.query.filter_by(is_active=True).all()

    @staticmethod
    def add_attachment(issue_id, user_id, file, filename):
        import os
        import uuid
        from flask import current_app
        from werkzeug.utils import secure_filename
        
        issue = Issue.query.get(issue_id)
        if not issue:
            return None, "Issue not found"
            
        if not file:
            return None, "No file provided"
            
        sec_filename = secure_filename(filename)
        ext = sec_filename.rsplit('.', 1)[1].lower() if '.' in sec_filename else ''
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4'}
        if ext not in allowed_extensions:
            return None, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            
        unique_name = f"{uuid.uuid4().hex}_{sec_filename}"
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, unique_name)
        file.save(filepath)
        
        file_size = os.path.getsize(filepath)
        
        attachment = IssueAttachment(
            issue_id=issue_id,
            uploaded_by=user_id,
            file_name=sec_filename,
            storage_key=unique_name,
            file_type=ext,
            file_size=file_size
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return attachment, None

    @staticmethod
    def add_comment(issue_id, user_id, comment):
        issue = Issue.query.get(issue_id)
        if not issue:
            return None, "Issue not found"
            
        if not comment or not comment.strip():
            return None, "Comment cannot be empty"
            
        history = IssueStatusHistory(
            issue_id=issue_id,
            old_status=issue.status,
            new_status=issue.status,
            changed_by=user_id,
            comment=comment.strip()
        )
        
        db.session.add(history)
        db.session.commit()
        
        return history, None

