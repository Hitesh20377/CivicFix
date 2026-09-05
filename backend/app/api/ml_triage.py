from flask import Blueprint, request, jsonify
from . import api_bp
from ..services.ml_service import MLService
from ..models.issue import Issue
import structlog

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')
logger = structlog.get_logger()

@ml_bp.route('/predict-category', methods=['POST'])
def predict_category():
    """Predicts issue category based on title and description."""
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')
    
    if not title and not description:
        return jsonify({"success": False, "error": "Title or description required"}), 400
        
    prediction = MLService.predict_category(title, description)
    logger.info("Category predicted", prediction=prediction)
    return jsonify(prediction), 200

@ml_bp.route('/predict-priority', methods=['POST'])
def predict_priority():
    """Recommends a priority level."""
    data = request.get_json()
    category = data.get('category', '')
    description = data.get('description', '')
    current_priority = data.get('official_priority', 'LOW')
    
    recommendation = MLService.recommend_priority(category, description, current_priority)
    return jsonify(recommendation), 200

@ml_bp.route('/issues/<int:issue_id>/accept-prediction', methods=['PATCH'])
def accept_prediction(issue_id):
    """Staff endpoint to accept the ML recommendation and overwrite official fields."""
    success = MLService.accept_prediction(issue_id)
    if success:
        return jsonify({"success": True, "message": "Prediction accepted and applied"}), 200
    return jsonify({"success": False, "error": "Issue not found"}), 404
