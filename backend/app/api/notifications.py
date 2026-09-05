from flask import request, jsonify
from datetime import datetime
from . import api_bp
from ..extensions import db
from ..models.notifications import Notification

from flask_jwt_extended import jwt_required, get_jwt_identity

@api_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    
    return jsonify([{
        "id": n.id,
        "issue_id": n.issue_id,
        "type": n.notification_type.value,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "action_url": n.action_url,
        "created_at": n.created_at.isoformat(),
        "read_at": n.read_at.isoformat() if n.read_at else None
    } for n in notifications]), 200

@api_bp.route('/notifications/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    user_id = get_jwt_identity()
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({"unread_count": count}), 200

@api_bp.route('/notifications/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_read(notification_id):
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        return jsonify({"error": "Not Found"}), 404

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()

    return jsonify({"message": "Marked as read"}), 200

@api_bp.route('/notifications/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    now = datetime.utcnow()
    
    for n in notifications:
        n.is_read = True
        n.read_at = now
        
    db.session.commit()
    return jsonify({"message": f"Marked {len(notifications)} notifications as read"}), 200

@api_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if not notification:
        return jsonify({"error": "Not Found"}), 404

    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({"message": "Notification deleted"}), 200
