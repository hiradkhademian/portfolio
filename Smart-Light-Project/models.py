from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY, JSON
import sqlalchemy

db = SQLAlchemy()


# ------------------ Core Models ------------------
class Sensor(db.Model):
    __tablename__ = 'sensors'
    id = db.Column(db.Integer, primary_key=True)
    sensor_type = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50))
    location = db.Column(db.String(100))
    last_value = db.Column(db.Float)
    calibration_value = db.Column(db.Float, default=1.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.Index('idx_sensor_location', 'location'),
    )


class Light(db.Model):
    __tablename__ = 'lights'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    state = db.Column(db.Boolean, default=False)
    red = db.Column(db.Integer, default=0)  # 0-255
    green = db.Column(db.Integer, default=0)  # 0-255
    blue = db.Column(db.Integer, default=0)  # 0-255
    brightness = db.Column(db.Integer, default=100)  # 0-100%
    last_command_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Scenario(db.Model):
    __tablename__ = 'scenarios'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    red = db.Column(db.Integer, default=0)
    green = db.Column(db.Integer, default=0)
    blue = db.Column(db.Integer, default=0)
    brightness = db.Column(db.Integer, default=100)


class Automation(db.Model):
    __tablename__ = 'automations'
    id = db.Column(db.Integer, primary_key=True)
    trigger = db.Column(db.String(100))
    action = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    scheduled_time = db.Column(db.Time)
    light_id = db.Column(db.Integer, db.ForeignKey('lights.id'))
    light = db.relationship('Light', backref='automations')
    last_triggered_at = db.Column(db.DateTime, default=None)

    __table_args__ = (
        db.Index('idx_automation_scheduled_time', 'scheduled_time'),
    )


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    preferences = db.Column(JSON)  # {"theme": "dark", "default_brightness": 75}


# ------------------ Advanced Features ------------------
class Mode(db.Model):
    __tablename__ = 'modes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    red = db.Column(db.Integer, default=0)
    green = db.Column(db.Integer, default=0)
    blue = db.Column(db.Integer, default=0)
    brightness = db.Column(db.Integer, default=100)


class ScheduledEvent(db.Model):
    __tablename__ = 'scheduled_events'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time, nullable=False)
    strip_ids = db.Column(ARRAY(db.Integer), nullable=False)  # [1, 2, 3]
    mode_id = db.Column(db.Integer, db.ForeignKey('modes.id'))
    mode = db.relationship('Mode', backref='scheduled_events')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EventLog(db.Model):
    __tablename__ = 'event_logs'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))  # 'sensor_update' | 'automation_trigger'
    details = db.Column(JSON)  # {"sensor_id": 1, "value": 25.5}
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


# ------------------ Utility Functions ------------------
def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)

    with app.app_context():
        db.create_all()