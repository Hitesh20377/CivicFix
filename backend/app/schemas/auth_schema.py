from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    role = fields.String(required=True, validate=validate.OneOf(
        ["citizen", "municipal_officer", "field_worker", "admin"]
    ))
    phone_number = fields.String(required=False, allow_none=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

register_schema = RegisterSchema()
login_schema = LoginSchema()
