from flask_jwt_extended import get_jwt
from ..extensions import redis_client, jwt

def register_auth_middleware(app):
    """
    Registers authentication middleware callbacks with the Flask application.
    """
    
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        try:
            token_in_redis = redis_client.get(jti)
            return token_in_redis is not None
        except Exception:
            # If Redis is unavailable (like in testing or if down), assume token is valid
            return False


    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        return str(user_id)
        
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from ..models.user import User
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()
