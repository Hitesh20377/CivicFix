from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from ..permissions.roles import require_role
from ..schemas.issue_schema import IssueSchema, IssueCategorySchema, IssueAttachmentSchema, IssueStatusHistorySchema
from ..services.issue_service import IssueService

issues_bp = Blueprint('issues', __name__, url_prefix='/api/issues')

issue_schema = IssueSchema()
issues_schema = IssueSchema(many=True)
category_schema = IssueCategorySchema(many=True)
attachment_schema = IssueAttachmentSchema()
history_schema = IssueStatusHistorySchema()

@issues_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = IssueService.get_categories()
    return jsonify({
        'status': 'success',
        'data': category_schema.dump(categories)
    }), 200

@issues_bp.route('', methods=['POST'])
@jwt_required()
def create_issue():
    """Create a new issue (Citizens)"""
    try:
        data = issue_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'status': 'error', 'errors': err.messages}), 400
        
    issue = IssueService.create_issue(current_user.id, data)
    
    return jsonify({
        'status': 'success',
        'message': 'Issue created successfully',
        'data': issue_schema.dump(issue)
    }), 201

@issues_bp.route('', methods=['GET'])
@jwt_required()
def get_issues():
    """Get issues based on role (Citizens see their own, officials see assigned/all)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    
    user_id = current_user.id
    role = current_user.role.name
    
    pagination = IssueService.get_issues(
        user_id=user_id,
        role=role,
        page=page,
        per_page=per_page,
        status=status,
        category_id=category_id
    )
    
    return jsonify({
        'status': 'success',
        'data': issues_schema.dump(pagination.items),
        'meta': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total
        }
    }), 200

@issues_bp.route('/<int:issue_id>', methods=['GET'])
@jwt_required()
def get_issue(issue_id):
    """Get a specific issue by ID"""
    issue = IssueService.get_issue_by_id(
        issue_id, 
        user_id=current_user.id, 
        role=current_user.role.name
    )
    if not issue:
        return jsonify({'status': 'error', 'message': 'Issue not found or unauthorized'}), 404
        
    issue_data = issue_schema.dump(issue)
    
    # If official/admin, attach active assignment
    if current_user.role.name in ['ADMIN', 'MUNICIPAL_OFFICER', 'FIELD_WORKER']:
        from ..models.assignment import IssueAssignment
        from ..models.enums import AssignmentStatus
        from ..schemas.assignment_schema import IssueAssignmentSchema
        
        # Get active assignment (not cancelled/completed) or the latest one
        active_assignment = IssueAssignment.query.filter(
            IssueAssignment.issue_id == issue.id,
            IssueAssignment.assignment_status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.ACCEPTED, AssignmentStatus.IN_PROGRESS])
        ).order_by(IssueAssignment.created_at.desc()).first()
        
        if active_assignment:
            issue_data['current_assignment'] = IssueAssignmentSchema().dump(active_assignment)
        
    return jsonify({
        'status': 'success',
        'data': issue_data
    }), 200

@issues_bp.route('/<int:issue_id>/status', methods=['PATCH'])
@jwt_required()
@require_role(['ADMIN', 'MUNICIPAL_OFFICER', 'FIELD_WORKER'])
def update_issue_status(issue_id):
    """Update issue status (Officials/Admins only)"""
    data = request.json
    new_status = data.get('status')
    comment = data.get('comment')
    
    if not new_status:
        return jsonify({'status': 'error', 'message': 'Status is required'}), 400
        
    issue = IssueService.update_issue_status(
        issue_id=issue_id,
        user_id=current_user.id,
        new_status=new_status,
        comment=comment
    )
    
    if not issue:
        return jsonify({'status': 'error', 'message': 'Issue not found'}), 404
        
    return jsonify({
        'status': 'success',
        'message': 'Issue status updated successfully',
        'data': issue_schema.dump(issue)
    }), 200

@issues_bp.route('/<int:issue_id>/attachments', methods=['POST'])
@jwt_required()
def upload_attachment(issue_id):
    """Upload an attachment for an issue"""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
        
    attachment, error = IssueService.add_attachment(
        issue_id=issue_id,
        user_id=current_user.id,
        file=file,
        filename=file.filename
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'message': 'File uploaded successfully',
        'data': attachment_schema.dump(attachment)
    }), 201

@issues_bp.route('/<int:issue_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(issue_id):
    """Add a comment to an issue"""
    data = request.json
    comment_text = data.get('comment')
    
    if not comment_text:
        return jsonify({'status': 'error', 'message': 'Comment is required'}), 400
        
    history, error = IssueService.add_comment(
        issue_id=issue_id,
        user_id=current_user.id,
        comment=comment_text
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'message': 'Comment added successfully',
        'data': history_schema.dump(history)
    }), 201
