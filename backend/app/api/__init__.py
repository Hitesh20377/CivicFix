from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api')

from . import health
from . import notifications
from . import analytics
from . import reports
from . import tasks

api_bp.register_blueprint(tasks.tasks_bp, url_prefix='/tasks')
