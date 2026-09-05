from flask import Blueprint
from .handlers import register_handlers

errors_bp = Blueprint('errors', __name__)
register_handlers(errors_bp)
