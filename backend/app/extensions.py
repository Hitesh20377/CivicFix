from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cache = Cache()
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_url,
    strategy="fixed-window"
)

# Redis connection for JWT blocklisting
try:
    redis_client = redis.from_url(redis_url, decode_responses=True)
except ValueError:
    redis_client = None
