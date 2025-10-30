import firebase_service
from flask import Flask, render_template, request, jsonify, abort
import os  # <-- ADDED THIS LINE

# --- START OF FIX ---
# Get the absolute path of the directory where this script (web_app.py) is
basedir = os.path.abspath(os.path.dirname(__file__))
# Create the absolute path to the 'templates' folder
template_dir = os.path.join(basedir, 'templates')
# --- END OF FIX ---


# Initialize Flask app, telling it the absolute path
# MODIFIED THIS LINE
app = Flask(__name__, template_folder=template_dir)

# --- HTML Page ---
@app.route('/')
def index():
    """Serves the main (and only) HTML page."""
    return render_template('index.html')

# --- API Endpoints ---
# These are what the HTML page will call to get/save data.

# --- PATIENTS API ---
@app.route('/api/patients', methods=['GET'])
def get_patients():
    patients = firebase_service.get_patients()
    return jsonify(patients)

@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.json
    try:
        doc_id = firebase_service.add_patient(data['name'], data['contact'], data['history'])
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/patients/<string:pid>', methods=['PUT'])
def update_patient(pid):
    data = request.json
    try:
        firebase_service.update_patient(pid, data['name'], data['contact'], data['history'])
        return jsonify({"success": True, "id": pid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/patients/<string:pid>', methods=['DELETE'])
def delete_patient(pid):
    try:
        firebase_service.delete_patient(pid)
        return jsonify({"success": True, "id": pid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# --- DOCTORS API ---
@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    doctors = firebase_service.get_doctors()
    return jsonify(doctors)

@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    data = request.json
    try:
        doc_id = firebase_service.add_doctor(data['name'], data['specialty'], data['schedule'])
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/doctors/<string:did>', methods=['PUT'])
def update_doctor(did):
    data = request.json
    try:
        firebase_service.update_doctor(did, data['name'], data['specialty'], data['schedule'])
        return jsonify({"success": True, "id": did})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/doctors/<string:did>', methods=['DELETE'])
def delete_doctor(did):
    try:
        firebase_service.delete_doctor(did)
        return jsonify({"success": True, "id": did})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# --- APPOINTMENTS API ---
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    appointments = firebase_service.get_appointments()
    return jsonify(appointments)

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    data = request.json
    try:
        doc_id = firebase_service.add_appointment(data['patient'], data['doctor'], data['datetime'])
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/appointments/<string:aid>', methods=['PUT'])
def update_appointment(aid):
    data = request.json
    try:
        firebase_service.update_appointment(aid, data['patient'], data['doctor'], data['datetime'])
        return jsonify({"success": True, "id": aid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/appointments/<string:aid>', methods=['DELETE'])
def delete_appointment(aid):
    try:
        firebase_service.delete_appointment(aid)
        return jsonify({"success": True, "id": aid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# --- BILLING API ---
@app.route('/api/billing', methods=['GET'])
def get_bills():
    bills = firebase_service.get_bills()
    return jsonify(bills)

@app.route('/api/billing', methods=['POST'])
def add_bill():
    data = request.json
    try:
        doc_id = firebase_service.add_bill(data['patient'], data['amount'], data['status'])
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/billing/<string:bid>', methods=['PUT'])
def update_bill(bid):
    data = request.json
    try:
        firebase_service.update_bill(bid, data['patient'], data['amount'], data['status'])
        return jsonify({"success": True, "id": bid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/billing/<string:bid>', methods=['DELETE'])
def delete_bill(bid):
    try:
        firebase_service.delete_bill(bid)
        return jsonify({"success": True, "id": bid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# --- INVENTORY API ---
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    inventory = firebase_service.get_inventory()
    return jsonify(inventory)

@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    data = request.json
    try:
        doc_id = firebase_service.add_inventory(data['item'], data['quantity'], data['supplier'])
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/inventory/<string:iid>', methods=['PUT'])
def update_inventory(iid):
    data = request.json
    try:
        firebase_service.update_inventory(iid, data['item'], data['quantity'], data['supplier'])
        return jsonify({"success": True, "id": iid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/inventory/<string:iid>', methods=['DELETE'])
def delete_inventory(iid):
    try:
        firebase_service.delete_inventory(iid)
        return jsonify({"success": True, "id": iid})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

