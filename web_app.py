import firebase_service
from flask import Flask, render_template, request, jsonify, abort
import os

# Get the absolute path of the directory where this script (web_app.py) is
basedir = os.path.abspath(os.path.dirname(__file__))
# Create the absolute path to the 'templates' folder
template_dir = os.path.join(basedir, 'templates')

# Initialize Flask app, telling it the absolute path to the templates folder
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
    if not data or not data.get('name'):
        abort(400, description="Missing patient name")
    try:
        # Get all fields from the form
        doc_id = firebase_service.add_patient(
            name=data.get('name'),
            contact=data.get('contact'),
            history=data.get('history'),
            dob=data.get('dob'), # Added DOB
            gender=data.get('gender') # Added Gender
        )
        # Return the newly created patient object
        new_patient = firebase_service.get_patient(doc_id)
        return jsonify(new_patient), 201
    except Exception as e:
        print(f"Error adding patient: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/patients/<string:pid>', methods=['PUT'])
def update_patient(pid):
    data = request.json
    if not data:
        abort(400, description="Missing data")
    try:
        # Update with all fields
        firebase_service.update_patient(
            pid,
            name=data.get('name'),
            contact=data.get('contact'),
            history=data.get('history'),
            dob=data.get('dob'), # Added DOB
            gender=data.get('gender') # Added Gender
        )
        updated_patient = firebase_service.get_patient(pid)
        return jsonify(updated_patient)
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
    if not data or not data.get('name'):
        abort(400, description="Missing doctor name")
    try:
        doc_id = firebase_service.add_doctor(
            name=data.get('name'),
            specialty=data.get('specialty'),
            schedule=data.get('schedule'),
            fee=data.get('fee') # Added Fee
        )
        new_doctor = firebase_service.get_doctor(doc_id)
        return jsonify(new_doctor), 201
    except Exception as e:
        print(f"Error adding doctor: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/doctors/<string:did>', methods=['PUT'])
def update_doctor(did):
    data = request.json
    if not data:
        abort(400, description="Missing data")
    try:
        firebase_service.update_doctor(
            did,
            name=data.get('name'),
            specialty=data.get('specialty'),
            schedule=data.get('schedule'),
            fee=data.get('fee') # Added Fee
        )
        updated_doctor = firebase_service.get_doctor(did)
        return jsonify(updated_doctor)
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
    if not data or not data.get('patient') or not data.get('doctor'):
        abort(400, description="Missing patient or doctor ID")
    try:
        doc_id = firebase_service.add_appointment(
            patient=data.get('patient'), # Now sends Patient ID
            doctor=data.get('doctor'),   # Now sends Doctor ID
            datetime=data.get('datetime')
        )
        new_appt = firebase_service.get_appointment(doc_id)
        return jsonify(new_appt), 201
    except Exception as e:
        print(f"Error adding appointment: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/appointments/<string:aid>', methods=['PUT'])
def update_appointment(aid):
    data = request.json
    if not data:
        abort(400, description="Missing data")
    try:
        firebase_service.update_appointment(
            aid,
            patient=data.get('patient'), # Now sends Patient ID
            doctor=data.get('doctor'),   # Now sends Doctor ID
            datetime=data.get('datetime')
        )
        updated_appt = firebase_service.get_appointment(aid)
        return jsonify(updated_appt)
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

# --- BILLING API ---
@app.route('/api/billing', methods=['GET'])
def get_billing():
    try:
        bills = firebase_service.get_billing()
        return jsonify(bills)
    except Exception as e:
        print(f"Error getting billing: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/billing', methods=['POST'])
def add_bill():
    data = request.json
    if not data or not data.get('patient'):
        abort(400, description="Missing patient ID")
    try:
        doc_id = firebase_service.add_bill(
            patient=data.get('patient'), # Patient ID
            items=data.get('items', []), # List of items
            total=data.get('total', 0),  # Calculated total
            status=data.get('status', 'Pending')
        )
        new_bill = firebase_service.get_bill(doc_id)
        return jsonify(new_bill), 201
    except Exception as e:
        print(f"Error adding bill: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/billing/<string:bid>', methods=['PUT'])
def update_bill(bid):
    data = request.json
    if not data:
        abort(400, description="Missing data")
    try:
        firebase_service.update_bill(
            bid,
            patient=data.get('patient'),
            items=data.get('items', []),
            total=data.get('total', 0),
            status=data.get('status', 'Pending')
        )
        updated_bill = firebase_service.get_bill(bid)
        return jsonify(updated_bill)
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

# --- NEW: Route for processing payment ---
@app.route('/api/billing/pay/<string:bid>', methods=['POST'])
def pay_bill(bid):
    try:
        # This function handles marking as 'Paid' AND updating inventory
        firebase_service.process_payment(bid)
        return jsonify({"success": True, "id": bid})
    except Exception as e:
        print(f"Error processing payment: {e}")
        # Check for our custom ValueError
        if "Bill not found or no items to process" in str(e) or "Not enough stock" in str(e):
             return jsonify({"success": False, "error": str(e)}), 400
        return jsonify({"success": False, "error": "An internal error occurred"}), 500

# --- INVENTORY API ---
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        inventory = firebase_service.get_inventory()
        return jsonify(inventory)
    except Exception as e:
        print(f"Error getting inventory: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    data = request.json
    if not data or not data.get('item'):
        abort(400, description="Missing item name")
    try:
        doc_id = firebase_service.add_inventory(
            item=data.get('item'),
            quantity=data.get('quantity', 0),
            supplier=data.get('supplier'),
            price=data.get('price', 0.0) # Added Price
        )
        new_item = firebase_service.get_inventory_item(doc_id)
        return jsonify(new_item), 201
    except Exception as e:
        print(f"Error adding inventory: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/inventory/<string:iid>', methods=['PUT'])
def update_inventory(iid):
    data = request.json
    if not data:
        abort(400, description="Missing data")
    try:
        firebase_service.update_inventory(
            iid,
            item=data.get('item'),
            quantity=data.get('quantity', 0),
            supplier=data.get('supplier'),
            price=data.get('price', 0.0) # Added Price
        )
        updated_item = firebase_service.get_inventory_item(iid)
        return jsonify(updated_item)
    except Exception as e:
        print(f"Error updating inventory: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/inventory/<string:iid>', methods=['DELETE'])
def delete_inventory(iid):
    try:
        firebase_service.delete_inventory(iid)
        return jsonify({"success": True, "id": iid})
    except Exception as e:
        print(f"Error deleting inventory: {e}")
        return jsonify({"success": False, "error": str(e)}), 400

