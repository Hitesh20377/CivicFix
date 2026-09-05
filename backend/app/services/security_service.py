import secrets
import string
from datetime import datetime
from typing import List, Tuple, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db
from ..models.security import APIKey
from ..models.enums import APIScope

class SecurityService:
    """
    Handles API Key generation, hashing, and scoped validation.
    """
    
    KEY_LENGTH = 32
    PREFIX_LENGTH = 8
    
    @classmethod
    def _generate_secure_token(cls) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(cls.KEY_LENGTH))

    @classmethod
    def generate_api_key(cls, name: str, created_by: int, scopes: List[APIScope], 
                         organization_id: Optional[int] = None, expires_at: Optional[datetime] = None) -> Tuple[APIKey, str]:
        """
        Generates a new API Key.
        Returns a tuple of (APIKey_Model_Instance, Raw_Token).
        The raw token is only returned this one time and never stored.
        """
        raw_token = f"sk-{cls._generate_secure_token()}"
        key_prefix = raw_token[:cls.PREFIX_LENGTH + 3] # 'sk-' + 8 chars
        
        # Hash the token securely (using pbkdf2:sha256 by default in werkzeug)
        key_hash = generate_password_hash(raw_token)
        
        # Format scopes as strings for JSONB storage
        scopes_data = [s.value if isinstance(s, APIScope) else s for s in scopes]
        
        api_key = APIKey(
            organization_id=organization_id,
            created_by=created_by,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=scopes_data,
            expires_at=expires_at
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        # We MUST return the full raw token here so the user can see it once.
        return api_key, raw_token

    @classmethod
    def verify_api_key(cls, raw_key: str, required_scope: APIScope) -> bool:
        """
        Validates the raw key against the database hash and checks the required scope.
        """
        if not raw_key.startswith("sk-") or len(raw_key) != (cls.KEY_LENGTH + 3):
            return False
            
        prefix = raw_key[:cls.PREFIX_LENGTH + 3] # 'sk-' + 8 chars
        
        api_key = APIKey.query.filter_by(key_prefix=prefix).first()
        
        if not api_key:
            return False
            
        # 1. Verify Hash
        if not check_password_hash(api_key.key_hash, raw_key):
            return False
            
        # 2. Check Revocation
        if api_key.revoked_at is not None:
            return False
            
        # 3. Check Expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return False
            
        # 4. Check Scope
        required_scope_val = required_scope.value if isinstance(required_scope, APIScope) else required_scope
        if required_scope_val not in api_key.scopes:
            return False
            
        # Valid! Update last_used_at
        api_key.last_used_at = datetime.utcnow()
        db.session.commit()
        
        return True
