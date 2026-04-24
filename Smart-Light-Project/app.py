from gc import get_stats
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from models import db, Sensor, Light, Scenario, Automation, User
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# ------------------ Flask App Initialization ------------------
app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_secret_key"

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

# ------------------ Dashboard and CRUD Routes ------------------
@app.route('/dashboard')
def dashboard():
    sensors = Sensor.query.all()
    lights = Light.query.all()
    scenarios = Scenario.query.all()
    automations = Automation.query.all()
    return render_template('dashboard.html', sensors=sensors, lights=lights,
                           scenarios=scenarios, automations=automations)

@app.route('/sensors', methods=['GET'])
def sensors_list():
    sensors = Sensor.query.all()
    return render_template('sensors.html', sensors=sensors)

@app.route('/sensors/<int:id>', methods=['GET', 'POST'])
def sensor_detail(id):
    sensor = Sensor.query.get_or_404(id)
    if request.method == 'POST':
        sensor.sensor_type = request.form.get('sensor_type', sensor.sensor_type)
        sensor.model = request.form.get('model', sensor.model)
        sensor.location = request.form.get('location', sensor.location)
        sensor.last_value = float(request.form.get('last_value', sensor.last_value))
        sensor.calibration_value = float(request.form.get('calibration_value', sensor.calibration_value))
        sensor.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Sensor updated successfully!', 'success')
        return redirect(url_for('sensors_list'))
    return render_template('sensor_detail.html', sensor=sensor)

# ------------------ API Routes ------------------
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success", "message": "Server is reachable"}), 200

@app.route('/api/led/color/ping', methods=['GET'])
def led_color_ping():
    return jsonify({"status": "success", "message": "LED color endpoint reachable"}), 200

@app.route('/api/sensors/all', methods=['GET'])
def get_all_sensors():
    sensors = Sensor.query.all()
    sensor_list = [{
        "id": sensor.id,
        "last_value": sensor.last_value,
        "updated_at": sensor.updated_at.isoformat() if sensor.updated_at else None
    } for sensor in sensors]
    return jsonify({"status": "success", "sensors": sensor_list}), 200

@app.route('/api/led/color', methods=['POST'])
def update_led_color():
    data = request.get_json()
    if not data or "state" not in data or "room" not in data:
        return jsonify({"status": "error", "message": "Invalid data, missing 'state' or 'room'"}), 400

    state = data.get("state")
    red = data.get("red", 0)
    green = data.get("green", 0)
    blue = data.get("blue", 0)
    brightness = data.get("brightness", 1.0)
    room = data.get("room")

    print(f"LED updated - State: {state}, Color: ({red}, {green}, {blue}), Brightness: {brightness}, Room: {room}")

    return jsonify({
        "status": "success",
        "message": "LED state updated",
        "data": {
            "state": state,
            "red": red,
            "green": green,
            "blue": blue,
            "brightness": brightness,
            "room": room
        }
    }), 200

@app.route('/api/mode/update', methods=['POST'])  # ✅ Changed from GET to POST
def handle_mode_update():
    data = request.get_json()
    if not data or "red" not in data or "green" not in data or "blue" not in data:
        return jsonify({"status": "error", "message": "Missing color data"}), 400

    print(f"Mode update received: {data}")
    return jsonify({
        "status": "success",
        "message": "Mode updated successfully",
        "received_data": data
    }), 200

@app.route('/api/automations/trigger', methods=['GET', 'POST'])
def trigger_automation():
    # Using UTC for consistency
    now = datetime.utcnow().isoformat()
    automations = Automation.query.all()
    triggered = [{"id": a.id, "action": a.action, "triggered_at": now} for a in automations]
    return jsonify({"status": "success", "automations": triggered}), 200

# ------------------ Scheduled Tasks for Automations ------------------
def check_scheduled_automations():
    with app.app_context():
        # Use UTC for fetching current time
        now = datetime.utcnow()
        # Define a window of 30 seconds before and after the current time.
        # This helps match the scheduled times even if they are not set with microsecond precision.
        lower_bound = (now - timedelta(seconds=30)).time()
        upper_bound = (now + timedelta(seconds=30)).time()
        
        automations = Automation.query.filter(
            Automation.scheduled_time >= lower_bound,
            Automation.scheduled_time <= upper_bound
        ).all()
        
        for automation in automations:
            print(f"Executing automation ID: {automation.id}, Action: {automation.action}")

# Start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_scheduled_automations, trigger="interval", minutes=1)
scheduler.start()


@app.route('/api/led/command', methods=['GET'])
def get_led_command():
    """ ESP fetches the latest RGB values. """
    led_data = get_stats()  # Call the function correctly
    return jsonify({"status": "success", "led_data": led_data}), 200
# ------------------ Main Entry Point ------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # ✅ Added host='0.0.0.0' for LAN access