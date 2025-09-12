from app import db
from sqlalchemy.orm import validates
import re
class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')

    @validates('password_hash')
    def validate_password(self, key, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain atleast one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain atleast one lowercase letter.")
        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain atleast one digit.")
        if not re.search(r"[!#$&*]", password):
            raise ValueError("Password must contain atleast one of these special character.[!#$&*]")
        return password
    
    @validates('email')
    def validate_email(self, key, email):
        if not re.match(r"[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email):
            raise ValueError("Invalid email format.")
        return email


    fines = db.relationship('Fine', back_populates='member')
    loans = db.relationship('Loan', back_populates='member')
    contributions = db.relationship('Contribution', back_populates='member')
    attendances = db.relationship('Attendance', back_populates='member')

    def __repr__(self):
        return f'<Member {self.id} - {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'role': self.role,
            'password': self.password_hash
        }
