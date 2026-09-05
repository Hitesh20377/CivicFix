from datetime import datetime
from ..extensions import db

class Ward(db.Model):
    __tablename__ = 'wards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    boundary_geojson = db.Column(db.JSON, nullable=True) # Using JSON for GeoJSON data
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employee_profiles = db.relationship('EmployeeProfile', backref='ward', lazy='dynamic')
    issue_assignments = db.relationship('IssueAssignment', backref='ward', lazy='dynamic')


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employee_profiles = db.relationship('EmployeeProfile', backref='department', lazy='dynamic')
    issue_assignments = db.relationship('IssueAssignment', backref='department', lazy='dynamic')


class EmployeeProfile(db.Model):
    __tablename__ = 'employee_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey('wards.id'), nullable=False)
    employee_code = db.Column(db.String(50), unique=True, nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('employee_profile', uselist=False))
