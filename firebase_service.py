import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json  # Make sure json is imported

# --- Firebase Initialization ---
# This block of code handles connecting to your Firebase project.

# Get the path to the service account key.
# This assumes 'serviceAccountKey.json' is in the same directory as this script.
basedir = os.path.abspath(os.path.dirname(__file__))
key_path = os.path.join(basedir, 'serviceAccountKey.json')

# Get the platform-specific credentials.
# The __firebase_config_str is automatically provided by the platform.
# We fall back to our local 'serviceAccountKey.json' if it's not found.
try:
    # Try to load the platform's environment credentials
    firebase_config_str = os.environ['__firebase_config']
    firebase_config = json.loads(firebase_config_str)
    cred = credentials.Certificate(firebase_config)
    app_id = os.environ.get('__app_id', 'default-app-id')
except (KeyError, json.JSONDecodeError):
    # Fallback for local development
    if os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
    else:
        # If no key is found, use anonymous auth (limited capabilities)
        cred = None
        print("Warning: 'serviceAccountKey.json' not found. Using anonymous auth.")

    # --- THIS IS THE FIX ---
    # We hardcode the app_id to 'default-app-id' so your local app
    # and deployed app use the SAME database path.
    app_id = "default-app-id"

# Initialize the Firebase Admin SDK
if not firebase_admin._apps:
    if cred:
        firebase_admin.initialize_app(cred)
    else:
        # Initialize without credentials for anonymous/emulator access
        firebase_admin.initialize_app()

db = firestore.client()

# --- MODIFIED: Set the base path for all database operations ---
# This ensures all data is stored in the correct sandboxed path
BASE_COLLECTION = f"artifacts/{app_id}/public/data"


# --- Helper Functions ---

def _get_doc_data(doc):
    """Helper to format a Firestore document into a Python dict."""
    if not doc.exists:
        return None
    data = doc.to_dict()
    data['id'] = doc.id
    return data


# --- PATIENTS ---

def get_patients():
    """Fetches all patients from the 'patients' collection."""
    patients_ref = db.collection(f"{BASE_COLLECTION}/patients")
    docs = patients_ref.stream()
    return [_get_doc_data(doc) for doc in docs]


def get_patient(pid):
    """Gets a single patient by their ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/patients").document(pid)
    return _get_doc_data(doc_ref.get())


def add_patient(name, contact, history, dob, gender):
    """Adds a new patient."""
    patients_ref = db.collection(f"{BASE_COLLECTION}/patients")
    data = {
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,  # Added DOB
        'gender': gender  # Added Gender
    }
    # Add a new doc with a generated ID
    update_time, doc_ref = patients_ref.add(data)
    return doc_ref.id


def update_patient(pid, name, contact, history, dob, gender):
    """Updates an existing patient by ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/patients").document(pid)
    data = {
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,  # Added DOB
        'gender': gender  # Added Gender
    }
    doc_ref.update(data)


def delete_patient(pid):
    """Deletes a patient by ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/patients").document(pid)
    doc_ref.delete()


# --- DOCTORS ---

def get_doctors():
    """Fetches all doctors."""
    docs_ref = db.collection(f"{BASE_COLLECTION}/doctors")
    docs = docs_ref.stream()
    return [_get_doc_data(doc) for doc in docs]


def get_doctor(did):
    """Gets a single doctor by ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/doctors").document(did)
    return _get_doc_data(doc_ref.get())


def add_doctor(name, specialty, schedule, fee):
    """Adds a new doctor."""
    docs_ref = db.collection(f"{BASE_COLLECTION}/doctors")
    data = {
        'name': name,
        'specialty': specialty,
        'schedule': schedule,
        'fee': fee  # Added consultation fee
    }
    update_time, doc_ref = docs_ref.add(data)
    return doc_ref.id


def update_doctor(did, name, specialty, schedule, fee):
    """Updates an existing doctor."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/doctors").document(did)
    data = {
        'name': name,
        'specialty': specialty,
        'schedule': schedule,
        'fee': fee  # Added consultation fee
    }
    doc_ref.update(data)


def delete_doctor(did):
    """Deletes a doctor by ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/doctors").document(did)
    doc_ref.delete()


# --- APPOINTMENTS ---

def get_appointments():
    """Fetches all appointments."""
    appts_ref = db.collection(f"{BASE_COLLECTION}/appointments")
    docs = appts_ref.stream()
    return [_get_doc_data(doc) for doc in docs]


def get_appointment(aid):
    """Gets a single appointment by ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/appointments").document(aid)
    return _get_doc_data(doc_ref.get())


def add_appointment(patient, doctor, datetime):
    """Adds a new appointment."""
    appts_ref = db.collection(f"{BASE_COLLECTION}/appointments")
    data = {
        'patient': patient,  # This is now a Patient ID
        'doctor': doctor,  # This is now a Doctor ID
        'datetime': datetime
    }
    update_time, doc_ref = appts_ref.add(data)
    return doc_ref.id


def update_appointment(aid, patient, doctor, datetime):
    """Updates an existing appointment."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/appointments").document(aid)
    data = {
        'patient': patient,
        'doctor': doctor,
        'datetime': datetime
    }
    doc_ref.update(data)


def delete_appointment(aid):
    """Deletes an appointment."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/appointments").document(aid)
    doc_ref.delete()


# --- BILLING ---

def get_billing():
    """Fetches all bills."""
    bills_ref = db.collection(f"{BASE_COLLECTION}/billing")
    docs = bills_ref.stream()
    return [_get_doc_data(doc) for doc in docs]


def get_bill(bid):
    """Gets a single bill by ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/billing").document(bid)
    return _get_doc_data(doc_ref.get())


def add_bill(patient, items, total, status):
    """Adds a new bill."""
    bills_ref = db.collection(f"{BASE_COLLECTION}/billing")
    data = {
        'patient': patient,  # Patient ID
        'items': items,  # List of item objects
        'total': total,  # Calculated total
        'status': status
    }
    update_time, doc_ref = bills_ref.add(data)
    return doc_ref.id


def update_bill(bid, patient, items, total, status):
    """Updates an existing bill."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/billing").document(bid)
    data = {
        'patient': patient,
        'items': items,
        'total': total,
        'status': status
    }
    doc_ref.update(data)


def delete_bill(bid):
    """Deletes a bill."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/billing").document(bid)
    doc_ref.delete()


# --- NEW: Process Payment and Update Inventory ---
@firestore.transactional
def process_payment_transaction(transaction, bill_ref, inventory_ref, bill):
    """
    This is a transactional function to ensure data integrity.
    It runs "all or nothing":
    1. Updates the bill status to "Paid".
    2. Updates the stock for each item on the bill.
    If any part fails (e.g., not enough stock), the whole operation fails.
    """
    # 1. Update the bill's status
    transaction.update(bill_ref, {'status': 'Paid'})

    # 2. Update inventory stock
    for item in bill.get('items', []):
        item_id = item.get('id')
        quantity_billed = item.get('quantity')

        # 'consult_fee' is a special item and not in the inventory
        if not item_id or item_id == 'consult_fee':
            continue

        item_ref = inventory_ref.document(item_id)
        item_snapshot = item_ref.get(transaction=transaction)

        if not item_snapshot.exists:
            raise ValueError(f"Inventory item not found: {item.get('name')}")

        current_quantity = item_snapshot.to_dict().get('quantity', 0)

        if current_quantity < quantity_billed:
            raise ValueError(f"Not enough stock for {item.get('name')}. Only {current_quantity} available.")

        # Subtract the quantity
        new_quantity = current_quantity - quantity_billed
        transaction.update(item_ref, {'quantity': new_quantity})


def process_payment(bid):
    """Public-facing function to start the payment transaction."""
    bill_ref = db.collection(f"{BASE_COLLECTION}/billing").document(bid)
    inventory_ref = db.collection(f"{BASE_COLLECTION}/inventory")

    bill = _get_doc_data(bill_ref.get())

    if not bill or not bill.get('items'):
        raise ValueError("Bill not found or no items to process.")

    # Run the transaction
    transaction = db.transaction()
    process_payment_transaction(transaction, bill_ref, inventory_ref, bill)


# --- INVENTORY ---

def get_inventory():
    """Fetches all inventory items."""
    inv_ref = db.collection(f"{BASE_COLLECTION}/inventory")
    docs = inv_ref.stream()
    return [_get_doc_data(doc) for doc in docs]


def get_inventory_item(iid):
    """Gets a single inventory item by ID."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/inventory").document(iid)
    return _get_doc_data(doc_ref.get())


def add_inventory(item, quantity, supplier, price):
    """Adds a new item to inventory."""
    inv_ref = db.collection(f"{BASE_COLLECTION}/inventory")
    data = {
        'item': item,
        'quantity': int(quantity),
        'supplier': supplier,
        'price': float(price)  # Added Price
    }
    update_time, doc_ref = inv_ref.add(data)
    return doc_ref.id


def update_inventory(iid, item, quantity, supplier, price):
    """Updates an existing inventory item."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/inventory").document(iid)
    data = {
        'item': item,
        'quantity': int(quantity),
        'supplier': supplier,
        'price': float(price)  # Added Price
    }
    doc_ref.update(data)


def delete_inventory(iid):
    """Deletes an inventory item."""
    doc_ref = db.collection(f"{BASE_COLLECTION}/inventory").document(iid)
    doc_ref.delete()

