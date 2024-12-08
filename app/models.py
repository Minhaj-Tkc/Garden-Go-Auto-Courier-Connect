from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Customer')
    
    # Common fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Role-specific fields
    address = db.Column(db.String(300))  # Only for Customers
    phone = db.Column(db.String(15))  # Common for all
    pincode = db.Column(db.String(10))  # Only for Customers

    # Courier-specific fields
    vehicle_info = db.Column(db.String(150))  # Vehicle description
    vehicle_number = db.Column(db.String(50))  # Vehicle license plate

    # Password utilities
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
