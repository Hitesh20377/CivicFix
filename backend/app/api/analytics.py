from flask import request, jsonify, make_response
from . import api_bp
from ..extensions import cache
from ..models.user import User
from ..services.analytics_service import AnalyticsService

from flask_jwt_extended import jwt_required, get_jwt_identity

# Helper to generate cache keys that depend on both user_id and query filters
def cache_key():
    user_id = request.args.get('user_id') or request.headers.get('X-User-Id')
    return f"{request.path}?{request.query_string.decode('utf-8')}&u={user_id}"

@api_bp.route('/analytics/overview', methods=['GET'])
@cache.cached(timeout=60, key_prefix=cache_key)
@jwt_required()
def get_overview():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    metrics = AnalyticsService.get_overview_metrics(user, filters)
    
    return jsonify({
        "current_total": metrics["total_issues"],
        "previous_total": 0,
        "change_percentage": 0,
        "trend": "down",
        "open_issues": metrics["open_issues"],
        "resolved_issues": metrics["resolved_issues"],
        "critical_issues": metrics["critical_issues"]
    }), 200

@api_bp.route('/analytics/issues-by-status', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_issues_by_status():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_status_breakdown(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/issues-by-priority', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_issues_by_priority():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_priority_breakdown(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/sla-performance', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_sla_performance():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_sla_metrics(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/issue-heatmap', methods=['GET'])
@api_bp.route('/analytics/issue-map', methods=['GET'])
@cache.cached(timeout=600, key_prefix=cache_key)
@jwt_required()
def get_heatmap():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_issue_heatmap(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/issues-by-category', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_issues_by_category():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_category_breakdown(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/issues-by-ward', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_issues_by_ward():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_ward_breakdown(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/issues-by-department', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_issues_by_department():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_department_breakdown(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/resolution-time', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_resolution_time():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_resolution_time(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/worker-workload', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_worker_workload():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_worker_workload(user, filters)
    return jsonify(data), 200

@api_bp.route('/analytics/trends', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key)
@jwt_required()
def get_trends():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    filters = request.args.to_dict()
    data = AnalyticsService.get_trends(user, filters)
    return jsonify(data), 200
