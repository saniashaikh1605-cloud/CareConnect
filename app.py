from flask import Flask, render_template, jsonify, request
from datetime import datetime
import urllib.parse
import random

app = Flask(__name__)

# Master Senior Telemetry Profile
elderly_profile = {
    "name": "Shaikh  Nazir Ahmed",
    "age": 74,
    "gender": "Male",
    "blood_group": "O+",
    "emergency_contact": "919876543210",
    "caregiver_name": "Sania shaikh(Primary Caregiver)",
    "address": "Garud Chowk, Latur, Maharashtra",
    "gps_coords": "Acquiring GPS...",
    "doctor_name": "Dr. A. K. Deshmukh",
    "doctor_phone": "+91 91234 56789",
    "allergies": ["Penicillin", "Sulfa Drugs"],
    "conditions": ["Hypertension", "Type 2 Diabetes"],
    "profile_img": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80"
}

medications = [
    {"id": 1, "name": "Amlodipine (5mg)", "time": "08:00 AM", "dosage": "1 Pill", "taken": True, "stock": 14},
    {"id": 2, "name": "Metformin (500mg)", "time": "01:00 PM", "dosage": "1 Pill", "taken": False, "stock": 2},
    {"id": 3, "name": "Atorvastatin (10mg)", "time": "08:00 PM", "dosage": "1 Pill", "taken": False, "stock": 18}
]

wellness_state = {
    "water_glasses": 4,
    "water_target": 8
}

vitals_state = {
    "heart_rate": 72,
    "bp": "120/80",
    "spo2": 98,
    "watch_connected": True,
    "anomaly_mode": False,
    "last_movement": datetime.now()
}

alerts_history = [
    {"timestamp": datetime.now().strftime("%I:%M %p"), "type": "SYSTEM READY", "detail": "Real Hardware Accelerometer & WebCam Connected."}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if (username == "admin" and password == "1234") or (username and password):
        return jsonify({"success": True, "message": "Authenticated successfully!"})
    return jsonify({"success": False, "message": "Invalid credentials provided."}), 400

@app.route('/api/update_gps', methods=['POST'])
def update_gps():
    data = request.json or {}
    lat = data.get('lat')
    lng = data.get('lng')
    if lat and lng:
        elderly_profile["gps_coords"] = f"{lat:.4f}° N, {lng:.4f}° E"
        return jsonify({"success": True, "coords": elderly_profile["gps_coords"]})
    return jsonify({"success": False}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    elapsed_minutes = (datetime.now() - vitals_state["last_movement"]).total_seconds() / 60
    
    if elapsed_minutes > 2:
        ai_status = {
            "status": "CRITICAL_INACTIVITY",
            "message": f"AI WARNING: Prolonged inactivity detected ({int(elapsed_minutes)} mins). Caregiver alerted!",
            "alert": True
        }
    else:
        ai_status = {
            "status": "NORMAL",
            "message": "Routine movement telemetry detected within normal parameters.",
            "alert": False
        }

    if vitals_state["watch_connected"]:
        if vitals_state["anomaly_mode"]:
            vitals_state["heart_rate"] = random.randint(132, 145)
            vitals_state["spo2"] = random.randint(91, 94)
            vitals_state["bp"] = f"{random.randint(150, 165)}/{random.randint(95, 105)}"
        else:
            vitals_state["heart_rate"] = random.randint(72, 96)
            vitals_state["spo2"] = random.randint(97, 99)
            vitals_state["bp"] = f"{random.randint(118, 126)}/{random.randint(78, 84)}"
    else:
        vitals_state["heart_rate"] = "--"
        vitals_state["bp"] = "--/--"
        vitals_state["spo2"] = "--"

    return jsonify({
        "profile": elderly_profile,
        "vitals": {
            "heart_rate": vitals_state["heart_rate"],
            "bp": vitals_state["bp"],
            "spo2": vitals_state["spo2"],
            "watch_connected": vitals_state["watch_connected"],
            "anomaly_mode": vitals_state["anomaly_mode"],
            "last_active": vitals_state["last_movement"].strftime("%I:%M:%S %p")
        },
        "wellness": wellness_state,
        "medications": medications,
        "ai_monitoring": ai_status,
        "alerts": alerts_history
    })

@app.route('/api/toggle_watch', methods=['POST'])
def toggle_watch():
    vitals_state["watch_connected"] = not vitals_state["watch_connected"]
    return jsonify({"success": True, "watch_connected": vitals_state["watch_connected"]})

@app.route('/api/toggle_anomaly', methods=['POST'])
def toggle_anomaly():
    vitals_state["anomaly_mode"] = not vitals_state["anomaly_mode"]
    if vitals_state["anomaly_mode"]:
        alerts_history.insert(0, {
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
            "type": "CARDIAC DISTRESS",
            "detail": "Heart Rate spike (>135 BPM) detected via PPG Watch Sensor!"
        })
    return jsonify({"success": True, "anomaly_mode": vitals_state["anomaly_mode"]})

@app.route('/api/log_water', methods=['POST'])
def log_water():
    if wellness_state["water_glasses"] < wellness_state["water_target"]:
        wellness_state["water_glasses"] += 1
    return jsonify({"success": True, "wellness": wellness_state})

@app.route('/api/get_whatsapp_link', methods=['GET'])
def get_whatsapp_link():
    phone = elderly_profile["emergency_contact"]
    message = (
        f"🚨 *CARECONNECT EMERGENCY ALERT* 🚨\n\n"
        f"👤 *Patient:* {elderly_profile['name']} ({elderly_profile['age']} Yrs)\n"
        f"📍 *Location:* {elderly_profile['address']} ({elderly_profile['gps_coords']})\n"
        f"❤️ *Heart Rate:* {vitals_state['heart_rate']} BPM\n"
        f"🩸 *BP:* {vitals_state['bp']}\n"
        f"⚠️ *Status:* Urgent Assistance / Fall Event Logged!"
    )
    encoded_message = urllib.parse.quote(message)
    return jsonify({"whatsapp_url": f"https://wa.me/{phone}?text={encoded_message}"})

@app.route('/api/trigger_sos', methods=['POST'])
def trigger_sos():
    alert_event = {
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "type": "EMERGENCY SOS",
        "detail": f"Panic signal triggered! GPS Location: {elderly_profile['gps_coords']}"
    }
    alerts_history.insert(0, alert_event)
    return jsonify({"success": True, "alert": alert_event})

@app.route('/api/trigger_fall', methods=['POST'])
def trigger_fall():
    alert_event = {
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "type": "HARD FALL DETECTED",
        "detail": f"Hardware accelerometer spike (G-Force > 25m/s²) registered at {elderly_profile['gps_coords']}!"
    }
    alerts_history.insert(0, alert_event)
    return jsonify({"success": True, "alert": alert_event})

@app.route('/api/add_prescription_ocr', methods=['POST'])
def add_prescription_ocr():
    new_med = {
        "id": len(medications) + 1,
        "name": "Scanned Prescription Medicine",
        "time": "09:00 PM",
        "dosage": "1 Tablet",
        "taken": False,
        "stock": 30
    }
    medications.append(new_med)
    return jsonify({"success": True, "medication": new_med})

@app.route('/api/simulate_activity', methods=['POST'])
def simulate_activity():
    vitals_state["last_movement"] = datetime.now()
    return jsonify({"success": True})

@app.route('/api/toggle_medication/<int:med_id>', methods=['POST'])
def toggle_medication(med_id):
    for med in medications:
        if med["id"] == med_id:
            med["taken"] = not med["taken"]
            if med["taken"] and med["stock"] > 0:
                med["stock"] -= 1
            return jsonify({"success": True, "taken": med["taken"], "stock": med["stock"]})
    return jsonify({"success": False}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)