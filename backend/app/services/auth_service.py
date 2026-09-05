from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..models.user import User
from ..models.enums import UserRole
from ..extensions import db
from datetime import timedelta

class AuthService:
    @staticmethod
    def register_user(data):
        email = data.get('email')
        
        if User.query.filter_by(email=email).first():
            return {"error": "User with this email already exists"}, 409
            
        try:
            # Map string to enum
            role_enum = UserRole(data.get('role', 'citizen'))
            
            new_user = User(
                email=email,
                full_name=data.get('full_name'),
                password_hash=generate_password_hash(data.get('password')),
                role=role_enum,
                phone_number=data.get('phone_number')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role.value
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def authenticate_user(data):
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.is_active:
            return {"error": "Invalid email or password"}, 401
            
        if not check_password_hash(user.password_hash, password):
            return {"error": "Invalid email or password"}, 401
            
        # Create token (expires in 1 day)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role.value},
            expires_delta=timedelta(days=1)
        )
        
        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value
            }
        }, 200
