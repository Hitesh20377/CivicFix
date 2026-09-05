from flask import Blueprint, request, jsonify
from ..services.ml_service import MLService
from ..models.user import User

from flask_jwt_extended import jwt_required, get_jwt_identity

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')

@ml_bp.route('/triage', methods=['POST'])
@jwt_required()
def triage_issue():
    """Returns AI recommendations for category, priority, department, and resolution time."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')
    
    if not title and not description:
        return jsonify({"error": "Missing title and description"}), 400
        
    predictions = MLService.triage_issue(title, description)
    return jsonify(predictions), 200

@ml_bp.route('/duplicates', methods=['POST'])
@jwt_required()
def check_duplicates():
    """Finds potential duplicates or similar historical issues."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')
    threshold = data.get('threshold', 0.5)
    
    if not title and not description:
        return jsonify({"error": "Missing title and description"}), 400
        
    similar_issues = MLService.find_similar_issues(title, description, threshold)
    return jsonify({"similar_issues": similar_issues}), 200

@ml_bp.route('/accept-recommendation', methods=['POST'])
@jwt_required()
def accept_recommendation():
    """Called when an officer accepts the AI suggestion."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    issue_id = data.get('issue_id')
    
    if not issue_id:
        return jsonify({"error": "Missing issue_id"}), 400
        
    success = MLService.accept_prediction(issue_id)
    if success:
        return jsonify({"message": "Recommendation accepted"}), 200
    else:
        return jsonify({"error": "Failed to accept recommendation or issue not found"}), 404
