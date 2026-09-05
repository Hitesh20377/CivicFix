from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from ..models.enums import AssignmentStatus

class AssignmentHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    issue_id = fields.Int(required=True)
    previous_assignee = fields.Int(allow_none=True)
    new_assignee = fields.Int(allow_none=True)
    changed_by = fields.Int(required=True)
    reason = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)

class IssueAssignmentSchema(Schema):
    id = fields.Int(dump_only=True)
    issue_id = fields.Int(required=True)
    assigned_to = fields.Int(required=True)
    assigned_by = fields.Int(required=True)
    department_id = fields.Int(allow_none=True)
    ward_id = fields.Int(allow_none=True)
    assignment_status = EnumField(AssignmentStatus, by_value=True)
    assignment_note = fields.String(allow_none=True)
    assigned_at = fields.DateTime(dump_only=True)
    accepted_at = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(allow_none=True)
    
    # Optional nested fields for dump
    history = fields.Nested(AssignmentHistorySchema, many=True, dump_only=True)
    
class WorkerProfileSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    full_name = fields.String(attribute="user.full_name", dump_only=True)
    department_id = fields.Int(dump_only=True)
    ward_id = fields.Int(dump_only=True)
    employee_code = fields.String(dump_only=True)
    designation = fields.String(dump_only=True)
    is_available = fields.Boolean(dump_only=True)
