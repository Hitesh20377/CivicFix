from marshmallow import Schema, fields, validate, EXCLUDE
from ..models.enums import IssuePriority, IssueStatus

class IssueCategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()
    icon = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class IssueAttachmentSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        
    id = fields.Int(dump_only=True)
    issue_id = fields.Int(required=True)
    uploaded_by = fields.Int(dump_only=True)
    file_name = fields.Str(required=True)
    file_type = fields.Str()
    file_size = fields.Int()
    storage_key = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)

class IssueStatusHistorySchema(Schema):
    class Meta:
        unknown = EXCLUDE
        
    id = fields.Int(dump_only=True)
    old_status = fields.Enum(IssueStatus, dump_only=True)
    new_status = fields.Enum(IssueStatus, required=True)
    changed_by = fields.Int(dump_only=True)
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class IssueSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    id = fields.Int(dump_only=True)
    issue_number = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    description = fields.Str(required=True, validate=validate.Length(min=10))
    
    category_id = fields.Int(allow_none=True)
    created_by = fields.Int(dump_only=True)
    ward_id = fields.Int(allow_none=True)
    
    address = fields.Str(allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    
    citizen_priority = fields.Enum(IssuePriority, load_default=IssuePriority.LOW)
    official_priority = fields.Enum(IssuePriority, dump_only=True)
    status = fields.Enum(IssueStatus, dump_only=True)
    
    # ML Tracking Fields
    suggested_category = fields.Str(dump_only=True)
    category_confidence = fields.Float(dump_only=True)
    suggested_priority = fields.Str(dump_only=True)
    priority_reason = fields.Str(dump_only=True)
    priority_confidence = fields.Float(dump_only=True)
    model_version = fields.Str(dump_only=True)
    is_prediction_accepted = fields.Bool(dump_only=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    resolved_at = fields.DateTime(dump_only=True)
    closed_at = fields.DateTime(dump_only=True)
    
    # Relationships
    attachments = fields.Nested(IssueAttachmentSchema, many=True, dump_only=True)
    status_history = fields.Nested(IssueStatusHistorySchema, many=True, dump_only=True)
