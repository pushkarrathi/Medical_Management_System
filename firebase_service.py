import firebase_admin
from firebase_admin import credentials, firestore, auth
import json
import os

# --- Firebase Initialization ---

# Define the required path for the sandboxed environment
# We hardcode this ID to ensure the app uses the same database path
# whether it's run locally or on the platform.
app_id = "default-app-id"

# Construct the required base path for all database operations
BASE_PATH = f"artifacts/{app_id}/public/data"

# Initialize Firebase
try:
    # 1. Try to load the service account key file
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    print("Firebase initialized with serviceAccountKey.json")

except Exception as e1:
    try:
        # 2. If file fails, try to use environment variables (for the platform)
        firebase_config_str = os.environ.get('__firebase_config')
        firebase_config = json.loads(firebase_config_str)

        # Get the auth token
        custom_token = os.environ.get('__initial_auth_token')

        # Initialize the app without credentials for client-side auth
        firebase_admin.initialize_app(firebase_config)

        # Authenticate using the custom token
        auth_client = auth.Client(firebase_admin.get_app())
        # Note: This auth is for verifying tokens. The 'db' client will be
        # authenticated by the platform's environment.
        print(f"Firebase initialized with environment config. Auth client ready.")

    except Exception as e2:
        print(f"CRITICAL: Failed to initialize Firebase. App will not work.")
        print(f"Service Account Key Error: {e1}")
        print(f"Environment Variable Error: {e2}")

# Get the Firestore client
db = firestore.client()

# --- Collection References ---
# All database paths are now prefixed with the required BASE_PATH
patient_ref = db.collection(f"{BASE_PATH}/patients")
doctor_ref = db.collection(f"{BASE_PATH}/doctors")
appointment_ref = db.collection(f"{BASE_PATH}/appointments")
billing_ref = db.collection(f"{BASE_PATH}/billing")
inventory_ref = db.collection(f"{BASE_PATH}/inventory")


# --- Helper Function ---
def _doc_to_dict(doc):
    """Converts a Firestore document to a dictionary, adding the ID."""
    if not doc.exists:
        return None
    data = doc.to_dict()
    data['id'] = doc.id
    return data


# --- PATIENTS ---
def get_patients():
    docs = patient_ref.stream()
    return [_doc_to_dict(doc) for doc in docs]


def add_patient(name, contact, history, dob, gender):
    data = {
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,
        'gender': gender
    }
    _, doc_ref = patient_ref.add(data)
    return doc_ref.id


def update_patient(pid, name, contact, history, dob, gender):
    data = {
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,
        'gender': gender
    }
    patient_ref.document(pid).set(data, merge=True)


def delete_patient(pid):
    patient_ref.document(pid).delete()


# --- DOCTORS ---
def get_doctors():
    docs = doctor_ref.stream()
    return [_doc_to_dict(doc) for doc in docs]


def add_doctor(name, specialty, schedule):
    data = {'name': name, 'specialty': specialty, 'schedule': schedule}
    _, doc_ref = doctor_ref.add(data)
    return doc_ref.id


def update_doctor(did, name, specialty, schedule):
    data = {'name': name, 'specialty': specialty, 'schedule': schedule}
    doctor_ref.document(did).set(data, merge=True)


def delete_doctor(did):
    doctor_ref.document(did).delete()


# --- APPOINTMENTS ---
def get_appointments():
    docs = appointment_ref.stream()
    return [_doc_to_dict(doc) for doc in docs]


def add_appointment(patient_id, doctor_id, datetime):
    data = {'patient': patient_id, 'doctor': doctor_id, 'datetime': datetime}
    _, doc_ref = appointment_ref.add(data)
    return doc_ref.id


def update_appointment(aid, patient_id, doctor_id, datetime):
    data = {'patient': patient_id, 'doctor': doctor_id, 'datetime': datetime}
    appointment_ref.document(aid).set(data, merge=True)


def delete_appointment(aid):
    appointment_ref.document(aid).delete()


# --- BILLING (Updated for Feature #4) ---
def get_billing():
    docs = billing_ref.stream()
    return [_doc_to_dict(doc) for doc in docs]


def add_bill(patient_id, items, total, status):
    data = {
        'patient': patient_id,
        'items': items,  # List of item objects
        'total': total,
        'status': status
    }
    _, doc_ref = billing_ref.add(data)
    return doc_ref.id


def update_bill(bid, patient_id, items, total, status):
    data = {
        'patient': patient_id,
        'items': items,
        'total': total,
        'status': status
    }
    billing_ref.document(bid).set(data, merge=True)


def delete_bill(bid):
    billing_ref.document(bid).delete()


# --- INVENTORY (Updated for Feature #4) ---
def get_inventory():
    docs = inventory_ref.stream()
    return [_doc_to_dict(doc) for doc in docs]


def add_inventory(item, quantity, supplier, price):
    data = {
        'item': item,
        'quantity': int(quantity),
        'supplier': supplier,
        'price': float(price)
    }
    _, doc_ref = inventory_ref.add(data)
    return doc_ref.id


def update_inventory(iid, item, quantity, supplier, price):
    data = {
        'item': item,
        'quantity': int(quantity),
        'supplier': supplier,
        'price': float(price)
    }
    inventory_ref.document(iid).set(data, merge=True)


def delete_inventory(iid):
    inventory_ref.document(iid).delete()


# --- Transactional Logic for Feature #4 ---

@firestore.transactional
def _process_payment_transaction(transaction, bill_doc_ref):
    """
    This function runs as an atomic transaction.
    It reads the bill, updates inventory, and marks the bill as paid.
    """
    # 1. Get the bill document
    bill_snapshot = bill_doc_ref.get(transaction=transaction)
    if not bill_snapshot.exists:
        raise Exception("Bill not found.")

    bill_data = bill_snapshot.to_dict()

    if bill_data.get('status') == 'Paid':
        raise Exception("This bill has already been paid.")

    # 2. Loop through items on the bill and update inventory
    items_on_bill = bill_data.get('items', [])
    if not items_on_bill:
        raise Exception("This bill has no items to process.")

    for item in items_on_bill:
        item_id = item.get('id')
        quantity_to_deduct = int(item.get('quantity'))

        if not item_id:
            continue  # Skip items with no ID

        item_doc_ref = inventory_ref.document(item_id)
        item_snapshot = item_doc_ref.get(transaction=transaction)

        if not item_snapshot.exists:
            raise Exception(f"Inventory item '{item.get('name')}' not found.")

        current_quantity = int(item_snapshot.to_dict().get('quantity', 0))

        if current_quantity < quantity_to_deduct:
            raise Exception(f"Not enough stock for '{item.get('name')}'. "
                            f"Need: {quantity_to_deduct}, Have: {current_quantity}")

        # Update the inventory item's quantity
        new_quantity = current_quantity - quantity_to_deduct
        transaction.update(item_doc_ref, {
            'quantity': new_quantity
        })

    # 3. If all inventory updates succeed, mark the bill as 'Paid'
    transaction.update(bill_doc_ref, {
        'status': 'Paid'
    })

    return {"success": True, "message": "Payment processed and inventory updated."}


def process_payment(bid):
    """
    Public function to initiate the payment transaction.
    """
    try:
        bill_doc_ref = billing_ref.document(bid)
        transaction = db.transaction()
        result = _process_payment_transaction(transaction, bill_doc_ref)
        return result
    except Exception as e:
        print(f"Transaction failed for bill {bid}: {e}")
        # Return a dictionary with the error message
        return {"success": False, "error": str(e)}

