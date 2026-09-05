from flask import jsonify, g
from .exceptions import CivicFixException
import structlog
from werkzeug.exceptions import HTTPException

logger = structlog.get_logger()

def build_error_response(message, error_code, status_code, errors=None):
    """Helper to standardize error responses."""
    response = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "errors": errors or {},
        "request_id": getattr(g, 'request_id', 'unknown')
    }
    return jsonify(response), status_code

def register_handlers(bp):
    @bp.app_errorhandler(CivicFixException)
    def handle_civicfix_exception(error):
        logger.warning("CivicFix exception", error_code=error.error_code, message=error.message, status=error.status_code)
        return build_error_response(error.message, error.error_code, error.status_code, error.payload)

    @bp.app_errorhandler(HTTPException)
    def handle_http_exception(error):
        logger.warning("HTTP exception", status=error.code, message=error.description)
        return build_error_response(error.description, error.name.upper().replace(' ', '_'), error.code)

    @bp.app_errorhandler(Exception)
    def handle_generic_exception(error):
        logger.error("Unhandled exception", exc_info=True)
        # Never expose the real error traceback to the client
        return build_error_response("An unexpected error has occurred", "INTERNAL_SERVER_ERROR", 500)
