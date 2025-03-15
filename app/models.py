from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(300), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    surname = db.Column(db.String(150), nullable=False)
    tax_id = db.Column(db.String(50), nullable=False)
    tax_class = db.Column(db.String(50), nullable=False)
    family_status = db.Column(db.String(50), nullable=False)
    has_children = db.Column(db.String(10), nullable=False)
    num_children = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('forms', lazy=True))
