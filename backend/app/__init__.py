import os
import uuid
import time
from flask import Flask, request, g
from flask_talisman import Talisman
import structlog
from config import config_by_name
from .logging import setup_logging

setup_logging()
logger = structlog.get_logger()


def create_app(config_name=None):
    """
    Application factory for creating a Flask app instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    if config_name == 'production' and app.config.get('SECRET_KEY') == 'default-secret-key':
        raise ValueError("A secure SECRET_KEY must be provided in production environments.")

    # Initialize extensions
    from .extensions import db, migrate, jwt, cache, limiter
    from flask_cors import CORS
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Talisman for security headers (disable HTTPS enforcement for local dev)
    if config_name == 'production':
        Talisman(app, content_security_policy=None)
        
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # We use simple cache for dev, but we could use Redis Cache if configured
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
    
    # Initialize Celery
    from .celery_app import celery_app, init_celery
    init_celery(app, celery_app)

    # Register models so they are attached to SQLAlchemy metadata
    with app.app_context():
        from . import models

    # Register blueprints
    from .routes.auth import auth_bp
    from .middleware.auth_middleware import register_auth_middleware
    
    register_auth_middleware(app)
    
    from .routes.issues import issues_bp
    from .routes.ml import ml_bp
    from .routes.assignments import assignments_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(assignments_bp)

    from .api import api_bp
    app.register_blueprint(api_bp)

    from .errors import errors_bp
    app.register_blueprint(errors_bp)

    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Bind request context to structlog
        structlog.contextvars.bind_contextvars(
            request_id=g.request_id,
            path=request.path,
            method=request.method,
            ip=request.remote_addr
        )

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = round(time.time() - g.start_time, 4)
            logger.info("Request completed", status=response.status_code, duration=duration)
            response.headers['X-Request-Id'] = g.request_id
            
        # Security headers fallback just in case
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        structlog.contextvars.clear_contextvars()
        return response

    return app
