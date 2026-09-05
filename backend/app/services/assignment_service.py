from datetime import datetime
from ..models.assignment import IssueAssignment, AssignmentHistory
from ..models.user import User
from ..models.issue import Issue
from ..models.municipal import EmployeeProfile
from ..models.enums import AssignmentStatus, UserRole
from ..extensions import db

class AuthorizationError(Exception):
    pass

class StateTransitionError(Exception):
    pass

class AssignmentError(Exception):
    pass

class AssignmentService:
    @staticmethod
    def get_assignment(assignment_id):
        return IssueAssignment.query.get(assignment_id)

    @staticmethod
    def _validate_role(user: User, allowed_roles: list[UserRole]):
        if user.role not in allowed_roles:
            raise AuthorizationError(f"User role {user.role} is not authorized for this action.")

    @staticmethod
    def get_eligible_field_workers(issue_id: int, user: User):
        """Get eligible field workers for an issue (same ward and dept)."""
        AssignmentService._validate_role(user, [UserRole.MUNICIPAL_OFFICER, UserRole.ADMIN])
        
        issue = Issue.query.get(issue_id)
        if not issue:
            raise ValueError("Issue not found")
            
        # Query employee profiles linked to users with role FIELD_WORKER
        # who are active, available, and match ward & department.
        eligible_workers = EmployeeProfile.query.join(User).filter(
            User.role == UserRole.FIELD_WORKER,
            User.is_active == True,
            EmployeeProfile.is_available == True,
            EmployeeProfile.ward_id == issue.ward_id
        ).all()
        
        return eligible_workers

    @staticmethod
    def create_assignment(issue_id: int, assigned_to_id: int, assigner: User, department_id: int = None, ward_id: int = None, note: str = None) -> IssueAssignment:
        """Create a new assignment for an issue."""
        AssignmentService._validate_role(assigner, [UserRole.MUNICIPAL_OFFICER, UserRole.ADMIN])
        
        issue = Issue.query.get(issue_id)
        if not issue:
            raise ValueError("Issue not found")
            
        # Prevent duplicate active assignments
        existing_assignment = IssueAssignment.query.filter_by(
            issue_id=issue_id, 
            assignment_status=AssignmentStatus.ASSIGNED
        ).first()
        
        existing_in_progress = IssueAssignment.query.filter_by(
            issue_id=issue_id, 
            assignment_status=AssignmentStatus.IN_PROGRESS
        ).first()
        
        if existing_assignment or existing_in_progress:
            raise AssignmentError("Issue already has an active assignment.")
            
        # Validate worker eligibility
        worker_profile = EmployeeProfile.query.filter_by(user_id=assigned_to_id).first()
        worker_user = User.query.get(assigned_to_id)
        
        if not worker_profile or not worker_user:
            raise ValueError("Worker not found")
            
        if worker_user.role != UserRole.FIELD_WORKER or not worker_user.is_active or not worker_profile.is_available:
            raise AssignmentError("Worker is not eligible (inactive or unavailable or not a field worker).")
            
        # Enforce cross-ward/dept rules (Admin can bypass)
        if assigner.role != UserRole.ADMIN:
            if worker_profile.ward_id != issue.ward_id:
                raise AssignmentError("Cross-ward assignment is only allowed by Admins.")
        
        try:
            assignment = IssueAssignment(
                issue_id=issue_id,
                assigned_to=assigned_to_id,
                assigned_by=assigner.id,
                department_id=department_id or worker_profile.department_id,
                ward_id=ward_id or worker_profile.ward_id,
                assignment_status=AssignmentStatus.ASSIGNED,
                assignment_note=note
            )
            
            db.session.add(assignment)
            db.session.flush() # Flush to get assignment ID if needed, though not strictly required here
            
            # Record history
            history = AssignmentHistory(
                issue_id=issue_id,
                new_assignee=assigned_to_id,
                changed_by=assigner.id,
                reason="Initial assignment" if not note else note
            )
            db.session.add(history)
            
            db.session.commit()
            
            # Trigger notification
            from ..tasks.notification_tasks import process_issue_event
            process_issue_event.delay(issue_id, 'issue_assigned', metadata={'assigned_to': assigned_to_id})
            
            return assignment
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def reassign_issue(assignment_id: int, new_assignee_id: int, changer: User, reason: str) -> IssueAssignment:
        """Reassign an existing issue assignment."""
        AssignmentService._validate_role(changer, [UserRole.MUNICIPAL_OFFICER, UserRole.ADMIN])
        
        assignment = AssignmentService.get_assignment(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
            
        issue = Issue.query.get(assignment.issue_id)
            
        if assignment.assignment_status in [AssignmentStatus.COMPLETED, AssignmentStatus.CANCELLED]:
            raise StateTransitionError("Cannot reassign a completed or cancelled assignment.")
            
        # Prevent reassigning to the same person
        if assignment.assigned_to == new_assignee_id:
            raise AssignmentError("New assignee must be different from current assignee.")
            
        # Validate new worker eligibility
        worker_profile = EmployeeProfile.query.filter_by(user_id=new_assignee_id).first()
        worker_user = User.query.get(new_assignee_id)
        
        if not worker_profile or not worker_user:
            raise ValueError("New worker not found")
            
        if worker_user.role != UserRole.FIELD_WORKER or not worker_user.is_active or not worker_profile.is_available:
            raise AssignmentError("New worker is not eligible (inactive or unavailable or not a field worker).")
            
        # Enforce cross-ward/dept rules (Admin can bypass)
        if changer.role != UserRole.ADMIN:
            if worker_profile.ward_id != issue.ward_id:
                raise AssignmentError("Cross-ward assignment is only allowed by Admins.")
        
        try:
            previous_assignee = assignment.assigned_to
            
            assignment.assigned_to = new_assignee_id
            assignment.assignment_status = AssignmentStatus.ASSIGNED
            assignment.assigned_by = changer.id
            assignment.accepted_at = None
            assignment.assignment_note = reason
            
            history = AssignmentHistory(
                issue_id=assignment.issue_id,
                previous_assignee=previous_assignee,
                new_assignee=new_assignee_id,
                changed_by=changer.id,
                reason=reason
            )
            db.session.add(history)
            
            db.session.commit()
            
            # Trigger notification
            from ..tasks.notification_tasks import process_issue_event
            process_issue_event.delay(assignment.issue_id, 'issue_assigned', metadata={'assigned_to': new_assignee_id, 'reassignment': True})
            
            return assignment
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def transition_status(assignment_id: int, user: User, new_status: AssignmentStatus, reason: str = None) -> IssueAssignment:
        """Update assignment status based on valid state transitions."""
        assignment = AssignmentService.get_assignment(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
            
        current_status = assignment.assignment_status
        
        # Only the assignee or Admin can change the status (and Officer can CANCEL)
        if user.id != assignment.assigned_to and user.role not in [UserRole.ADMIN, UserRole.MUNICIPAL_OFFICER]:
             raise AuthorizationError("Not authorized to transition this assignment.")
             
        if user.role == UserRole.MUNICIPAL_OFFICER and new_status != AssignmentStatus.CANCELLED:
             if user.id != assignment.assigned_to:
                 raise AuthorizationError("Officers can only cancel assignments they did not receive.")
        
        if new_status == AssignmentStatus.REJECTED and not reason:
            raise AssignmentError("A reason is required when rejecting an assignment.")
        
        # Validate transitions
        valid_transitions = {
            AssignmentStatus.ASSIGNED: [AssignmentStatus.ACCEPTED, AssignmentStatus.REJECTED, AssignmentStatus.CANCELLED],
            AssignmentStatus.ACCEPTED: [AssignmentStatus.IN_PROGRESS, AssignmentStatus.CANCELLED],
            AssignmentStatus.IN_PROGRESS: [AssignmentStatus.COMPLETED, AssignmentStatus.CANCELLED],
        }
        
        allowed_next_states = valid_transitions.get(current_status, [])
        
        if new_status not in allowed_next_states:
            raise StateTransitionError(f"Invalid transition from {current_status} to {new_status}")
            
        try:
            assignment.assignment_status = new_status
            
            # Update timestamps based on transition
            if new_status == AssignmentStatus.ACCEPTED:
                assignment.accepted_at = datetime.utcnow()
            elif new_status == AssignmentStatus.COMPLETED:
                assignment.completed_at = datetime.utcnow()
                
            # Log history
            history = AssignmentHistory(
                issue_id=assignment.issue_id,
                previous_assignee=assignment.assigned_to,
                new_assignee=assignment.assigned_to,
                changed_by=user.id,
                reason=reason or f"Status changed to {new_status.name}"
            )
            db.session.add(history)
                
            db.session.commit()
            
            # Trigger notification
            from ..tasks.notification_tasks import process_issue_event
            process_issue_event.delay(assignment.issue_id, 'assignment_updated', metadata={'new_status': new_status.name})
            
            return assignment
        except Exception as e:
            db.session.rollback()
            raise e
