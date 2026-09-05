from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.assignment_service import AssignmentService, AuthorizationError, StateTransitionError, AssignmentError
from ..schemas.assignment_schema import IssueAssignmentSchema, WorkerProfileSchema
from ..models.user import User
from ..models.enums import AssignmentStatus

assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

@assignments_bp.route('/eligible-workers/<int:issue_id>', methods=['GET'])
@jwt_required()
def get_eligible_workers(issue_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    try:
        workers = AssignmentService.get_eligible_field_workers(issue_id, user)
        schema = WorkerProfileSchema(many=True)
        return jsonify(schema.dump(workers)), 200
    except AuthorizationError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@assignments_bp.route('', methods=['POST'])
@jwt_required()
def create_assignment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    data = request.get_json()
    issue_id = data.get('issue_id')
    assigned_to_id = data.get('assigned_to')
    note = data.get('note')
    
    if not issue_id or not assigned_to_id:
        return jsonify({"error": "issue_id and assigned_to are required"}), 400
        
    try:
        assignment = AssignmentService.create_assignment(
            issue_id=issue_id,
            assigned_to_id=assigned_to_id,
            assigner=user,
            note=note
        )
        schema = IssueAssignmentSchema()
        return jsonify(schema.dump(assignment)), 201
    except AuthorizationError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except AssignmentError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@assignments_bp.route('/<int:assignment_id>/reassign', methods=['POST'])
@jwt_required()
def reassign_issue(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    data = request.get_json()
    new_assignee_id = data.get('new_assignee')
    reason = data.get('reason')
    
    if not new_assignee_id or not reason:
        return jsonify({"error": "new_assignee and reason are required"}), 400
        
    try:
        assignment = AssignmentService.reassign_issue(
            assignment_id=assignment_id,
            new_assignee_id=new_assignee_id,
            changer=user,
            reason=reason
        )
        schema = IssueAssignmentSchema()
        return jsonify(schema.dump(assignment)), 200
    except AuthorizationError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except (AssignmentError, StateTransitionError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@assignments_bp.route('/<int:assignment_id>/status', methods=['PATCH'])
@jwt_required()
def transition_status(assignment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    data = request.get_json()
    status_str = data.get('status')
    reason = data.get('reason')
    
    if not status_str:
        return jsonify({"error": "status is required"}), 400
        
    try:
        new_status = AssignmentStatus[status_str]
    except KeyError:
        return jsonify({"error": "Invalid status value"}), 400
        
    try:
        assignment = AssignmentService.transition_status(
            assignment_id=assignment_id,
            user=user,
            new_status=new_status,
            reason=reason
        )
        schema = IssueAssignmentSchema()
        return jsonify(schema.dump(assignment)), 200
    except AuthorizationError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except (AssignmentError, StateTransitionError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
