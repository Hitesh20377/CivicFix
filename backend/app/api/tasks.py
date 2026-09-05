from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.task_service import TaskService
from app.models.user import User

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """
    Get the status of a specific background task.
    """
    status = TaskService.get_task_status(task_id)
    return jsonify(status), 200

@tasks_bp.route('/<task_id>/revoke', methods=['POST'])
@jwt_required()
def revoke_task(task_id):
    """
    Revoke a specific background task.
    Only admins can revoke tasks.
    """
    # Simple check for admin role
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role.value not in ['admin', 'system_admin']:
        return jsonify({"error": "Forbidden"}), 403

    terminate = request.json.get('terminate', False) if request.is_json else False
    result = TaskService.revoke_task(task_id, terminate=terminate)
    return jsonify(result), 200
