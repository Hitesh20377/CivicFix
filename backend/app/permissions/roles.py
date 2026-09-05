from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..models.user import User
from ..errors.exceptions import AuthorizationError, AuthenticationError

def require_role(*allowed_roles):
    """
    Decorator to enforce Role-Based Access Control (RBAC).
    Must be used after @jwt_required() or call verify_jwt_in_request() internally.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            user = User.query.get(user_id)
            if not user:
                raise AuthenticationError("User not found")
                
            if user.role.name not in [r.name for r in allowed_roles] and user.role not in allowed_roles:
                raise AuthorizationError(f"Role {user.role.name} is not authorized to access this resource.")
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper
