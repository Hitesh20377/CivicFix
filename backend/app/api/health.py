from flask import jsonify
from . import api_bp
from ..extensions import db, redis_client
from sqlalchemy import text
import os
import psutil

@api_bp.route('/health', methods=['GET'])
def health_check():
    """General health check."""
    return jsonify({"status": "ok"}), 200

@api_bp.route('/health/database', methods=['GET'])
def health_check_database():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"database": "ok"}), 200
    except Exception as e:
        return jsonify({"database": "error", "error": str(e)}), 503

@api_bp.route('/health/redis', methods=['GET'])
def health_check_redis():
    try:
        if redis_client.ping():
            return jsonify({"redis": "ok"}), 200
    except Exception as e:
        return jsonify({"redis": "error", "error": str(e)}), 503

@api_bp.route('/health/celery', methods=['GET'])
def health_check_celery():
    try:
        from ..celery_app import celery_app
        with celery_app.connection_for_read() as conn:
            conn.ensure_connection(max_retries=1)
        return jsonify({"celery": "ok"}), 200
    except Exception:
        return jsonify({"celery": "error", "error": "Celery service unavailable"}), 503


@api_bp.route('/health/storage', methods=['GET'])
def health_check_storage():
    from flask import current_app
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'instance/uploads')
    if os.access(upload_folder, os.W_OK) or (not os.path.exists(upload_folder) and os.access(os.path.dirname(os.path.abspath(upload_folder)), os.W_OK)):
        return jsonify({"storage": "ok"}), 200
    return jsonify({"storage": "error", "error": "Storage directory not writable"}), 503

@api_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Basic application metrics."""
    process = psutil.Process(os.getpid())
    return jsonify({
        "memory_usage_mb": round(process.memory_info().rss / (1024 * 1024), 2),
        "cpu_percent": process.cpu_percent(),
        "active_threads": process.num_threads()
    }), 200
