from . import db
from datetime import datetime

# -----------------------------
# USERS
# -----------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# -----------------------------
# FARMS
# -----------------------------
class Farm(db.Model):
    __tablename__ = "farms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -----------------------------
# ZONES
# -----------------------------
class Zone(db.Model):
    __tablename__ = "zones"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    farm_id = db.Column(
        db.Integer,
        db.ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False
    )
    twin_state = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -----------------------------
# DEVICES
# -----------------------------
class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    device_uid = db.Column(db.String(200), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)

    zone_id = db.Column(
        db.Integer,
        db.ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=False
    )

    # RELATIONSHIP EKLENDİ
    zone = db.relationship("Zone", backref="devices")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime)


# -----------------------------
# TELEMETRY
# -----------------------------
class Telemetry(db.Model):
    __tablename__ = "telemetry"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False
    )

    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    ph = db.Column(db.Float)
    ec = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def payload(self):
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "soil_moisture": self.soil_moisture,
            "ph": self.ph,
            "ec": self.ec,
        }


# -----------------------------
# ALERTS
# -----------------------------
class Rule(db.Model):
    __tablename__ = "rules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.Text, nullable=False)  # JSON string
    action = db.Column(db.String(200), default="alert")
    zone_id = db.Column(
        db.Integer,
        db.ForeignKey("zones.id", ondelete="SET NULL"),
        nullable=True
    )
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "condition": self.condition,
            "action": self.action,
            "zone_id": self.zone_id,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat()
        }

class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    # optional link back to a triggering rule
    rule_id = db.Column(
        db.Integer,
        db.ForeignKey("rules.id", ondelete="SET NULL"),
        nullable=True
    )

    zone_id = db.Column(
        db.Integer,
        db.ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=False
    )

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=True
    )

    farm_id = db.Column(
        db.Integer,
        db.ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=True
    )

    alert_type = db.Column(db.String(100))
    message = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    severity = db.Column(db.String(50), default="warning")
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "device_id": self.device_id,
            "farm_id": self.farm_id,
            "alert_type": self.alert_type,
            "message": self.message,
            "severity": self.severity,
            "read": self.read,
            "timestamp": self.timestamp.isoformat(),
        }


# -----------------------------
# COMMANDS
# -----------------------------
class CommandLog(db.Model):
    __tablename__ = "commands"

    id = db.Column(db.Integer, primary_key=True)

    device_id = db.Column(
        db.Integer,
        db.ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False
    )

    command = db.Column(db.String(100))
    status = db.Column(db.String(50), default="sent")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
