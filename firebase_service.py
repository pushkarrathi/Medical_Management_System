import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import mysql_service

# --- Firebase Initialization ---
db = None
app_id = "default-app-id"  # Hardcoded to unify local and deployed DB

try:
    # 1. Try to initialize using the serviceAccountKey.json
    cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    else:
        # 2. Fallback for environments where __app_id is defined (like the platform)
        # We must load credentials from the environment string
        firebase_config_str = os.environ.get('__firebase_config')
        if firebase_config_str:
            firebase_config = json.loads(firebase_config_str)
            cred = credentials.Certificate(firebase_config)
            app_name = f"app-{app_id}"

            # Check if app is already initialized
            try:
                app = firebase_admin.get_app(name=app_name)
            except ValueError:
                app = firebase_admin.initialize_app(cred, name=app_name)

            db = firestore.client(app=app)
        else:
            raise FileNotFoundError("serviceAccountKey.json not found and __firebase_config is not set.")

except Exception as e:
    print(f"Error initializing Firebase: {e}")
    # Handle the case where db is not initialized, e.g., set db to None
    # and functions below will handle the 'db is None' case.
    if db is None:
        print("CRITICAL: Firestore database (db) is None. App will not function.")


def get_collection(name):
    """Helper to get a collection from the sandboxed path."""
    if db is None:
        raise ConnectionError("Firestore is not initialized. Check your serviceAccountKey.json or credentials.")
    return db.collection('artifacts', app_id, 'public', 'data', name)


# --- Patients ---
def get_patients():
    """Fetches all patient documents."""
    patients_ref = get_collection('patients')
    docs = patients_ref.stream()
    patients = []
    for doc in docs:
        patient = doc.to_dict()
        patient['id'] = doc.id
        patients.append(patient)
    return patients


def add_patient(name, contact, history, dob, gender):
    """Adds a new patient."""
    patients_ref = get_collection('patients')
    doc_ref = patients_ref.document()
    doc_ref.set({
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,
        'gender': gender
    })
    pid = doc_ref.id
    mysql_service.add_patient_mysql(pid, name, contact, history, dob, gender)
    return pid


def update_patient(pid, name, contact, history, dob, gender):
    """Updates an existing patient."""
    patients_ref = get_collection('patients')
    patients_ref.document(pid).update({
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,
        'gender': gender
    })
    mysql_service.update_patient_mysql(pid, name, contact, history, dob, gender)


def delete_patient(pid):
    patients_ref = get_collection('patients')
    patients_ref.document(pid).delete()
    mysql_service.delete_patient_mysql(pid)


def get_patient(pid):
    """Fetches a single patient by their ID."""
    doc_ref = get_collection('patients').document(pid)
    doc = doc_ref.get()
    if doc.exists:
        patient = doc.to_dict()
        patient['id'] = doc.id
        return patient
    else:
        raise Exception("Patient not found")


# --- Doctors ---
def get_doctors():
    """Fetches all doctor documents."""
    doctors_ref = get_collection('doctors')
    docs = doctors_ref.stream()
    doctors = []
    for doc in docs:
        doctor = doc.to_dict()
        doctor['id'] = doc.id
        doctors.append(doctor)
    return doctors


def add_doctor(name, specialty, schedule, fee):
    """Adds a new doctor."""
    doctors_ref = get_collection('doctors')
    doc_ref = doctors_ref.document()
    doc_ref.set({
        'name': name,
        'specialty': specialty,
        'schedule': schedule,
        'fee': fee
    })
    did = doc_ref.id
    mysql_service.add_doctor_mysql(did, name, specialty, schedule, fee)
    return did


def update_doctor(did, name, specialty, schedule, fee):
    """Updates an existing doctor."""
    doctors_ref = get_collection('doctors')
    doctors_ref.document(did).update({
        'name': name,
        'specialty': specialty,
        'schedule': schedule,
        'fee': fee
    })
    mysql_service.update_doctor_mysql(did, name, specialty, schedule, fee)


def delete_doctor(did):
    doctors_ref = get_collection('doctors')
    doctors_ref.document(did).delete()
    mysql_service.delete_doctor_mysql(did)


def get_doctor(did):
    """Fetches a single doctor by their ID."""
    doc_ref = get_collection('doctors').document(did)
    doc = doc_ref.get()
    if doc.exists:
        doctor = doc.to_dict()
        doctor['id'] = doc.id
        return doctor
    else:
        raise Exception("Doctor not found")


# --- Appointments ---
def get_appointments():
    """Fetches all appointment documents."""
    appts_ref = get_collection('appointments')
    docs = appts_ref.stream()
    appointments = []
    for doc in docs:
        appt = doc.to_dict()
        appt['id'] = doc.id
        appointments.append(appt)
    return appointments


def add_appointment(patient_id, doctor_id, datetime):
    """Adds a new appointment."""
    appts_ref = get_collection('appointments')
    doc_ref = appts_ref.document()
    doc_ref.set({
        'patient': patient_id,  # Storing the ID
        'doctor': doctor_id,  # Storing the ID
        'datetime': datetime
    })
    aid = doc_ref.id
    mysql_service.add_appointment_mysql(aid, patient_id, doctor_id, datetime)
    return aid


def update_appointment(aid, patient_id, doctor_id, datetime):
    """Updates an existing appointment."""
    appts_ref = get_collection('appointments')
    appts_ref.document(aid).update({
        'patient': patient_id,
        'doctor': doctor_id,
        'datetime': datetime
    })
    mysql_service.update_appointment_mysql(aid, patient_id, doctor_id, datetime)


def delete_appointment(aid):
    appts_ref = get_collection('appointments')
    appts_ref.document(aid).delete()
    mysql_service.delete_appointment_mysql(aid)


def get_appointment(aid):
    """Fetches a single appointment by its ID."""
    doc_ref = get_collection('appointments').document(aid)
    doc = doc_ref.get()
    if doc.exists:
        appt = doc.to_dict()
        appt['id'] = doc.id
        return appt
    else:
        raise Exception("Appointment not found")


# --- Billing ---
def get_billing():
    """Fetches all bill documents."""
    billing_ref = get_collection('billing')
    docs = billing_ref.stream()
    bills = []
    for doc in docs:
        bill = doc.to_dict()
        bill['id'] = doc.id
        bills.append(bill)
    return bills


def add_bill(patient_id, items, total, status):
    """Adds a new bill."""
    billing_ref = get_collection('billing')
    doc_ref = billing_ref.document()
    doc_ref.set({
        'patient': patient_id,  # Storing the ID
        'items': items,
        'total': total,
        'status': status
    })
    bid = doc_ref.id
    mysql_service.add_bill_mysql(bid, patient_id, items, total, status)
    return bid


def update_bill(bid, patient_id, items, total, status):
    """Updates an existing bill."""
    billing_ref = get_collection('billing')
    billing_ref.document(bid).update({
        'patient': patient_id,
        'items': items,
        'total': total,
        'status': status
    })
    mysql_service.update_bill_mysql(bid, patient_id, items, total, status)


def delete_bill(bid):
    billing_ref = get_collection('billing')
    billing_ref.document(bid).delete()
    mysql_service.delete_bill_mysql(bid)


def get_bill(bid):
    """Fetches a single bill by its ID."""
    doc_ref = get_collection('billing').document(bid)
    doc = doc_ref.get()
    if doc.exists:
        bill = doc.to_dict()
        bill['id'] = doc.id
        return bill
    else:
        raise Exception("Bill not found")


# --- Inventory ---
def get_inventory():
    """Fetches all inventory documents."""
    inventory_ref = get_collection('inventory')
    docs = inventory_ref.stream()
    items = []
    for doc in docs:
        item = doc.to_dict()
        item['id'] = doc.id
        items.append(item)
    return items


def add_inventory(item, quantity, supplier, price):
    """Adds a new inventory item."""
    inventory_ref = get_collection('inventory')
    doc_ref = inventory_ref.document()
    doc_ref.set({
        'item': item,
        'quantity': quantity,
        'supplier': supplier,
        'price': price
    })
    iid = doc_ref.id
    mysql_service.add_inventory_mysql(iid, item, quantity, supplier, price)
    return iid


def update_inventory(iid, item, quantity, supplier, price):
    """Updates an existing inventory item."""
    inventory_ref = get_collection('inventory')
    inventory_ref.document(iid).update({
        'item': item,
        'quantity': quantity,
        'supplier': supplier,
        'price': price
    })
    mysql_service.update_inventory_mysql(iid, item, quantity, supplier, price)


def delete_inventory(iid):
    inventory_ref = get_collection('inventory')
    inventory_ref.document(iid).delete()
    mysql_service.delete_inventory_mysql(iid)


def get_inventory_item(iid):
    """Fetches a single inventory item by its ID."""
    doc_ref = get_collection('inventory').document(iid)
    doc = doc_ref.get()
    if doc.exists:
        item = doc.to_dict()
        item['id'] = doc.id
        return item
    else:
        raise Exception("Inventory item not found")


# --- Transactional Logic ---

@firestore.transactional
def process_payment_transaction(transaction, bid):
    """
    Handles the payment in a transaction:
    1. Reads all required docs (bill, inventory items).
    2. Checks stock.
    3. Writes all updates (bill status, inventory quantities).
    """
    billing_ref = get_collection('billing')
    inventory_ref = get_collection('inventory')
    bill_doc_ref = billing_ref.document(bid)

    # --- 1. READ PHASE ---

    # Get the bill
    bill_snapshot = bill_doc_ref.get(transaction=transaction)
    if not bill_snapshot.exists:
        raise Exception("Bill not found.")

    bill_data = bill_snapshot.to_dict()

    # Check if bill is already paid
    if bill_data.get('status') == 'Paid':
        raise Exception("This bill has already been paid.")

    items_to_update = bill_data.get('items', [])
    inventory_snapshots = {}

    # Get all inventory items that are part of this bill
    for item in items_to_update:
        # We only care about items that are *not* consultations
        if item.get('isConsultation', False) == False:
            item_id = item.get('id')
            if not item_id:
                raise Exception(f"Bill contains an item with no ID: {item.get('name')}")

            item_doc_ref = inventory_ref.document(item_id)
            item_snapshot = item_doc_ref.get(transaction=transaction)

            if not item_snapshot.exists:
                raise Exception(f"Inventory item not found: {item.get('name')}")

            inventory_snapshots[item_id] = item_snapshot

    # --- 2. VALIDATION/CALCULATION PHASE (No DB calls) ---

    for item in items_to_update:
        if item.get('isConsultation', False) == False:
            item_id = item.get('id')
            item_snapshot = inventory_snapshots[item_id]

            current_quantity = item_snapshot.to_dict().get('quantity', 0)
            requested_quantity = item.get('quantity', 0)

            if current_quantity < requested_quantity:
                raise Exception(
                    f"Not enough stock for item: {item.get('name')}. Requested: {requested_quantity}, Available: {current_quantity}")

    # --- 3. WRITE PHASE ---

    # All checks passed, update the bill
    transaction.update(bill_doc_ref, {
        'status': 'Paid'
    })

    # Update all inventory items
    for item in items_to_update:
        if item.get('isConsultation', False) == False:
            item_id = item.get('id')
            item_snapshot = inventory_snapshots[item_id]
            item_doc_ref = inventory_ref.document(item_id)  # Get ref again for writing

            current_quantity = item_snapshot.to_dict().get('quantity', 0)
            requested_quantity = item.get('quantity', 0)
            new_quantity = current_quantity - requested_quantity

            transaction.update(item_doc_ref, {
                'quantity': new_quantity
            })


def process_payment(bid):
    """
    Public-facing function to run the payment transaction.
    """
    if db is None:
        raise ConnectionError("Firestore is not initialized.")

    transaction = db.transaction()
    process_payment_transaction(transaction, bid)

