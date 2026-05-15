import os
import webbrowser
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from extensions import socketio
from models import db, User, Contact, Emergency
from services.email_service import send_emergency_alerts
from werkzeug.security import generate_password_hash, check_password_hash


api = Blueprint('api', __name__)


def _current_user_id():
    return int(get_jwt_identity())


@api.route('/register', methods=['POST'])
def register_user():
    data = request.get_json(silent=True) or {}

    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    phone = (data.get('phone') or '').strip()
    tc_no = (data.get('tc_no') or '').strip()
    password = data.get('password') or ''

    blood_type = (data.get('blood_type') or '').strip()
    diseases = (data.get('diseases') or '').strip()
    birth_date = (data.get('birth_date') or '').strip()
    gender = (data.get('gender') or '').strip()
    emergency_email_1 = (data.get('emergency_email_1') or '').strip().lower()
    emergency_email_2 = (data.get('emergency_email_2') or '').strip().lower()

    errors = {}

    if not full_name:
        errors['full_name'] = 'Full name is required.'
    if not email:
        errors['email'] = 'Email is required.'
    if not phone:
        errors['phone'] = 'Phone number is required.'
    if not tc_no:
        errors['tc_no'] = 'TC number is required.'
    if not password:
        errors['password'] = 'Password is required.'

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({
            "success": False,
            "message": "Phone number already exists"
        }), 400

    if User.query.filter_by(tc_no=tc_no).first():
        return jsonify({
            "success": False,
            "message": "TC number already exists"
        }), 400

    hashed_password = generate_password_hash(password)

    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        tc_no=tc_no,
        password=hashed_password,
        blood_type=blood_type,
        diseases=diseases,
        birth_date=birth_date,
        gender=gender,
        emergency_email_1=emergency_email_1,
        emergency_email_2=emergency_email_2
    )

    db.session.add(user)
    db.session.commit()

    if emergency_email_1:
        db.session.add(Contact(
            name='Emergency Contact 1',
            phone_number=None,
            email=emergency_email_1,
            user_id=user.id
        ))

    if emergency_email_2:
        db.session.add(Contact(
            name='Emergency Contact 2',
            phone_number=None,
            email=emergency_email_2,
            user_id=user.id
        ))

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User registered successfully"
    }), 201


@api.route('/login', methods=['POST'])
def login_user():
    data = request.get_json(silent=True) or {}

    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    errors = {}
    if not email:
        errors['email'] = 'Email is required.'
    if not password:
        errors['password'] = 'Password is required.'

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    token = create_access_token(identity=str(user.id), expires_delta= False)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone
        }
    }), 200


@api.route('/emergency/trigger', methods=['POST'])
@jwt_required()
def trigger_emergency():
    print('DEBUG /api/emergency/trigger called')
    print('DEBUG request headers:', dict(request.headers))
    print('DEBUG request body:', request.get_data(as_text=True))

    data = request.get_json(silent=True) or {}

    user_id = _current_user_id()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    errors = {}
    if latitude is None:
        errors['latitude'] = 'Latitude is required.'
    if longitude is None:
        errors['longitude'] = 'Longitude is required.'

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    emergency = Emergency(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        status='active'
    )
    db.session.add(emergency)
    db.session.commit()

    tracking_base = os.getenv('TRACKING_URL_BASE')
    if tracking_base:
        tracking_url = f"{tracking_base.rstrip('/')}/?emergency_id={emergency.id}"
    else:
        tracking_url = f"{request.host_url.rstrip('/')}/?emergency_id={emergency.id}"

    user_contacts = Contact.query.filter_by(user_id=user_id).all()
    print(f"DEBUG user_contacts from DB: {[c.email for c in user_contacts]}")

    contact_emails = {contact.email for contact in user_contacts if contact.email}
    if user.emergency_email_1 and user.emergency_email_1 not in contact_emails:
        user_contacts.append(Contact(
            name='Emergency Contact 1',
            email=user.emergency_email_1,
            phone_number=None,
            user_id=user_id
        ))
        contact_emails.add(user.emergency_email_1)
    if user.emergency_email_2 and user.emergency_email_2 not in contact_emails:
        user_contacts.append(Contact(
            name='Emergency Contact 2',
            email=user.emergency_email_2,
            phone_number=None,
            user_id=user_id
        ))
        contact_emails.add(user.emergency_email_2)

    print(f"DEBUG final contacts: {[c.email for c in user_contacts]}")

    send_emergency_alerts(user, user_contacts, emergency)

    # Frontend can listen in real-time with: socket.on("new_emergency", ...)
    socketio.emit('new_emergency', {
        "emergency_id": emergency.id,
        "user": {
            "id": user.id,
            "full_name": user.full_name
        },
        "location": {
            "latitude": emergency.latitude,
            "longitude": emergency.longitude
        },
        "status": emergency.status
    })

    # Open browser to the admin page served by Flask
    try:
        host = request.host_url.rstrip('/')
        admin_url = f"{host}/admin"
        webbrowser.open(admin_url)
    except Exception as e:
        print(f"Failed to open browser: {e}")

    return jsonify({
        "success": True,
        "message": "Emergency triggered successfully",
        "tracking_url": tracking_url,
        "user": {
            "id": user.id,
            "full_name": user.full_name
        },
        "emergency": {
            "id": emergency.id,
            "status": emergency.status,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude
        }
    }), 201


@api.route('/emergency/<int:emergency_id>/status', methods=['PATCH'])
@jwt_required()
def update_emergency_status(emergency_id):
    user_id = _current_user_id()
    data = request.get_json(silent=True) or {}
    status = data.get('status')

    allowed = {'active', 'resolved', 'cancelled'}
    errors = {}
    if not status:
        errors['status'] = 'status is required.'
    elif status not in allowed:
        errors['status'] = 'status must be one of: active, resolved, cancelled.'

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    emergency = Emergency.query.get(emergency_id)
    if not emergency or emergency.user_id != user_id:
        return jsonify({
            "success": False,
            "message": "Emergency not found"
        }), 404

    emergency.status = status
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Emergency status updated successfully",
        "emergency": {
            "id": emergency.id,
            "status": emergency.status
        }
    }), 200


@api.route('/emergency/<int:emergency_id>', methods=['GET'])
def get_emergency(emergency_id):
    emergency = Emergency.query.get(emergency_id)
    if not emergency:
        return jsonify({
            "success": False,
            "message": "Emergency not found"
        }), 404

    user = User.query.get(emergency.user_id)
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "emergency": {
            "id": emergency.id,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude,
            "status": emergency.status,
            "timestamp": emergency.timestamp.isoformat() if emergency.timestamp else None
        },
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "blood_type": user.blood_type,
            "diseases": user.diseases
        }
    }), 200


@api.route('/emergency/<int:emergency_id>/location', methods=['PUT'])
@jwt_required()
def update_emergency_location(emergency_id):
    user_id = _current_user_id()
    data = request.get_json(silent=True) or {}

    latitude = data.get('latitude')
    longitude = data.get('longitude')

    errors = {}
    if latitude is None:
        errors['latitude'] = 'Latitude is required.'
    if longitude is None:
        errors['longitude'] = 'Longitude is required.'

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    emergency = Emergency.query.get(emergency_id)
    if not emergency or emergency.user_id != user_id:
        return jsonify({
            "success": False,
            "message": "Emergency not found"
        }), 404

    emergency.latitude = latitude
    emergency.longitude = longitude
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Emergency location updated successfully",
        "emergency": {
            "id": emergency.id,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude
        }
    }), 200


@api.route('/admin/sharers', methods=['GET'])
def admin_sharers():
    emergencies = Emergency.query.filter_by(status='active').all()

    data = []

    for emergency in emergencies:
        user = User.query.get(emergency.user_id)

        names = user.full_name.split(" ", 1)

        first_name = names[0]
        last_name = names[1] if len(names) > 1 else ""

        # Calculate age if birth_date is available
        age = None
        if user.birth_date:
            from datetime import datetime
            try:
                birth = datetime.strptime(user.birth_date, '%Y-%m-%d')
                age = datetime.now().year - birth.year - ((datetime.now().month, datetime.now().day) < (birth.month, birth.day))
            except:
                pass

        data.append({
            "id": str(user.id),
            "emergency_id": emergency.id,
            "firstName": first_name,
            "lastName": last_name,
            "age": age,
            "bloodType": user.blood_type,
            "conditions": user.diseases,
            "lat": emergency.latitude,
            "lng": emergency.longitude
        })

    return jsonify(data), 200

@api.route('/share/<int:user_id>/profile', methods=['GET'])
def share_profile(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    names = user.full_name.split(" ", 1)

    return jsonify({
        "firstName": names[0],
        "lastName": names[1] if len(names) > 1 else "",
        "age": None,
        "bloodType": None,
        "conditions": None
    }), 200

@api.route('/contacts', methods=['GET', 'POST'])
@jwt_required()
def handle_contacts():
    user_id = _current_user_id()

    if request.method == 'GET':
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        contacts = Contact.query.filter_by(user_id=user_id).all()
        return jsonify({
            "success": True,
            "contacts": [
                {
                    "id": contact.id,
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "email": contact.email
                }
                for contact in contacts
            ]
        }), 200

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    phone_number = (data.get('phone_number') or '').strip()
    email = (data.get('email') or '').strip().lower() or None

    errors = {}
    if not name:
        errors['name'] = 'Name is required.'
    if not phone_number:
        errors['phone_number'] = 'Phone number is required.'

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    existing_contact = Contact.query.filter_by(
        user_id=user_id,
        phone_number=phone_number
    ).first()
    if existing_contact:
        return jsonify({
            "success": False,
            "message": "Contact already exists"
        }), 400

    contact = Contact(
        name=name,
        phone_number=phone_number,
        email=email,
        user_id=user_id
    )
    db.session.add(contact)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Contact added successfully",
        "contact": {
            "id": contact.id,
            "name": contact.name,
            "phone_number": contact.phone_number,
            "email": contact.email
        }
    }), 201

@api.route('/share/<int:user_id>/location', methods=['GET'])
def share_location(user_id):
    emergency = Emergency.query.filter_by(
        user_id=user_id,
        status='active'
    ).order_by(Emergency.id.desc()).first()

    if not emergency:
        return jsonify({"message": "Location not found"}), 404

    return jsonify({
        "lat": emergency.latitude,
        "lng": emergency.longitude,
        "timestamp": emergency.created_at.isoformat()
        if emergency.created_at else None
    }), 200

@api.route('/contacts/<int:contact_id>', methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
    user_id = _current_user_id()

    user = User.query.get(user_id)
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    contact = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
    if not contact:
        return jsonify({
            "success": False,
            "message": "Contact not found"
        }), 404

    db.session.delete(contact)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Contact deleted successfully"
    }), 200

@api.route('/logout', methods=['POST'])
def logot():
        return jsonify({"message":"Logout successful."}),200
