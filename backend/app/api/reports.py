from flask import request, jsonify, make_response
from . import api_bp
from ..models.user import User
from ..services.reporting_service import ReportingService

def get_current_user():
    user_id = request.args.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return None
    return User.query.get(user_id)

@api_bp.route('/reports/issues.csv', methods=['GET'])
def download_issues_csv():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    filters = request.args.to_dict()
    csv_data = ReportingService.generate_csv(user, filters)
    
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=issues_report.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@api_bp.route('/reports/issues.pdf', methods=['GET'])
def download_issues_pdf():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    filters = request.args.to_dict()
    pdf_data = ReportingService.generate_pdf(user, filters)
    
    response = make_response(pdf_data)
    response.headers["Content-Disposition"] = "attachment; filename=issues_report.pdf"
    response.headers["Content-type"] = "application/pdf"
    return response
