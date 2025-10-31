import firebase_service
from flask import Flask, render_template, request, jsonify, abort
import os
import json

# --- Flask App Initialization ---

# Get the absolute path of the directory where this script (web_app.py) is
basedir = os.path.abspath(os.path.dirname(__file__))
# Create the absolute path to the 'templates' folder
template_dir = os.path.join(basedir, 'templates')

# Initialize Flask app, telling it the absolute path
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
    try:
        patients = firebase_service.get_patients()
        return jsonify(patients)
    except Exception as e:
        print(f"Error getting patients: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.json
    try:
        # Updated to handle DOB and Gender
        doc_id = firebase_service.add_patient(
            data.get('name'),
            data.get('contact'),
            data.get('history'),
            data.get('dob'), # Changed from age
            data.get('gender')
        )
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        print(f"Error adding patient: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/patients/<string:pid>', methods=['PUT'])
def update_patient(pid):
    data = request.json
    try:
        # Updated to handle DOB and Gender
        firebase_service.update_patient(
            pid,
            data.get('name'),
            data.get('contact'),
            data.get('history'),
            data.get('dob'), # Changed from age
            data.get('gender')
        )
        return jsonify({"success": True, "id": pid})
    except Exception as e:
        print(f"Error updating patient: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/patients/<string:pid>', methods=['DELETE'])
def delete_patient(pid):
    try:
        firebase_service.delete_patient(pid)
        return jsonify({"success": True, "id": pid})
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# --- DOCTORS API ---
@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    try:
        doctors = firebase_service.get_doctors()
        return jsonify(doctors)
    except Exception as e:
        print(f"Error getting doctors: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/doctors', methods=['POST'])
def add_doctor():
    data = request.json
    try:
        doc_id = firebase_service.add_doctor(data.get('name'), data.get('specialty'), data.get('schedule'))
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        print(f"Error adding doctor: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/doctors/<string:did>', methods=['PUT'])
def update_doctor(did):
    data = request.json
    try:
        firebase_service.update_doctor(did, data.get('name'), data.get('specialty'), data.get('schedule'))
        return jsonify({"success": True, "id": did})
    except Exception as e:
        print(f"Error updating doctor: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/doctors/<string:did>', methods=['DELETE'])
def delete_doctor(did):
    try:
        firebase_service.delete_doctor(did)
        return jsonify({"success": True, "id": did})
    except Exception as e:
        print(f"Error deleting doctor: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# --- APPOINTMENTS API ---
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        appointments = firebase_service.get_appointments()
        return jsonify(appointments)
    except Exception as e:
        print(f"Error getting appointments: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    data = request.json
    try:
        # Now storing patient/doctor IDs
        doc_id = firebase_service.add_appointment(data.get('patient'), data.get('doctor'), data.get('datetime'))
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        print(f"Error adding appointment: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/appointments/<string:aid>', methods=['PUT'])
def update_appointment(aid):
    data = request.json
    try:
        # Now storing patient/doctor IDs
        firebase_service.update_appointment(aid, data.get('patient'), data.get('doctor'), data.get('datetime'))
        return jsonify({"success": True, "id": aid})
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/appointments/<string:aid>', methods=['DELETE'])
def delete_appointment(aid):
    try:
        firebase_service.delete_appointment(aid)
        return jsonify({"success": True, "id": aid})
    except Exception as e:
        print(f"Error deleting appointment: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# --- BILLING API (Updated for Feature #4) ---
@app.route('/api/billing', methods=['GET'])
def get_billing():
    try:
        bills = firebase_service.get_billing()
        return jsonify(bills)
    except Exception as e:
        print(f"Error getting bills: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/billing', methods=['POST'])
def add_bill():
    data = request.json
    try:
        # Updated to handle items list and total
        doc_id = firebase_service.add_bill(
            data.get('patient'),
            data.get('items', []),
            data.get('total', 0),
            data.get('status', 'Pending')
        )
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        print(f"Error adding bill: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/billing/<string:bid>', methods=['PUT'])
def update_bill(bid):
    data = request.json
    try:
        # Updated to handle items list and total
        firebase_service.update_bill(
            bid,
            data.get('patient'),
            data.get('items', []),
            data.get('total', 0),
            data.get('status', 'Pending')
        )
        return jsonify({"success": True, "id": bid})
    except Exception as e:
        print(f"Error updating bill: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/billing/<string:bid>', methods=['DELETE'])
def delete_bill(bid):
    try:
        firebase_service.delete_bill(bid)
        return jsonify({"success": True, "id": bid})
    except Exception as e:
        print(f"Error deleting bill: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

# --- NEW API Endpoint for Feature #4 ---
@app.route('/api/billing/pay/<string:bid>', methods=['POST'])
def pay_bill(bid):
    """
    Handles marking a bill as 'Paid' and updating inventory stock.
    This is a transactional operation defined in firebase_service.
    """
    try:
        result = firebase_service.process_payment(bid)
        if result.get("success"):
            return jsonify(result)
        else:
            # If the transaction failed, return a 400 error
            return jsonify(result), 400
    except Exception as e:
        print(f"Error processing payment for bill {bid}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# --- INVENTORY API (Updated for Feature #4) ---
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        items = firebase_service.get_inventory()
        return jsonify(items)
    except Exception as e:
        print(f"Error getting inventory: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    data = request.json
    try:
        # Added 'price' field
        doc_id = firebase_service.add_inventory(
            data.get('item'),
            data.get('quantity'),
            data.get('supplier'),
            data.get('price', 0.0) # Add price
        )
        return jsonify({"success": True, "id": doc_id}), 201
    except Exception as e:
        print(f"Error adding inventory item: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/inventory/<string:iid>', methods=['PUT'])
def update_inventory_item(iid):
    data = request.json
    try:
        # Added 'price' field
        firebase_service.update_inventory(
            iid,
            data.get('item'),
            data.get('quantity'),
            data.get('supplier'),
            data.get('price', 0.0) # Add price
        )
        return jsonify({"success": True, "id": iid})
    except Exception as e:
        print(f"Error updating inventory item: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/inventory/<string:iid>', methods=['DELETE'])
def delete_inventory_item(iid):
    try:
        firebase_service.delete_inventory(iid)
        return jsonify({"success": True, "id": iid})
    except Exception as e:
        print(f"Error deleting inventory item: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

