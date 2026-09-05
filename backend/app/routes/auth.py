from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from ..services.auth_service import AuthService
from ..schemas.auth_schema import register_schema, login_schema
from ..extensions import redis_client, limiter
import structlog
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = structlog.get_logger()

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """
    Register a new user.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
        
    # Validate and deserialize input
    errors = register_schema.validate(json_data)
    if errors:
        return jsonify(errors), 422
        
    result, status_code = AuthService.register_user(json_data)
    
    if status_code == 201:
        logger.info("User registered successfully", email=json_data.get('email'))
    else:
        logger.warning("User registration failed", email=json_data.get('email'), error=result)
        
    return jsonify(result), status_code

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Authenticate a user and return a JWT.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400
        
    # Validate and deserialize input
    errors = login_schema.validate(json_data)
    if errors:
        return jsonify(errors), 422
        
    result, status_code = AuthService.authenticate_user(json_data)
    
    if status_code == 200:
        logger.info("User logged in successfully", email=json_data.get('email'))
    else:
        logger.warning("User login failed", email=json_data.get('email'))
        
    return jsonify(result), status_code

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def logout():
    """
    Revokes the current user's JWT token by adding its JTI to the Redis blocklist.
    """
    jti = get_jwt()["jti"]
    
    # Store the JTI in Redis with a TTL of 1 day (or whatever max token lifespan is)
    redis_client.setex(jti, timedelta(days=1), "revoked")
    
    logger.info("User logged out, token revoked", jti=jti)
    return jsonify({"success": True, "message": "Successfully logged out"}), 200
