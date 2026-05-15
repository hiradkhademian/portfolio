from extensions import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(20), unique=True, nullable=False)
    tc_no = db.Column(db.String(11), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    blood_type = db.Column(db.String(5), nullable=True)
    diseases = db.Column(db.Text, nullable=True)
    birth_date = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(20), nullable=True)

    emergency_email_1 = db.Column(db.String(120), nullable=True)
    emergency_email_2 = db.Column(db.String(120), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contacts = db.relationship(
        'Contact',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    emergencies = db.relationship(
        'Emergency',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)