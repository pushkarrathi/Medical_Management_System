import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json

# --- Firebase Initialization ---

# Define the app_id. We hardcode 'default-app-id' to ensure local and deployed
# apps use the SAME database path, solving the "default" vs "default-app-id" issue.
APP_ID = "default-app-id"

# Construct the full, required database path
BASE_DB_PATH = f"artifacts/{APP_ID}/public/data"

db = None
try:
    # 1. Check for the service account key file
    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
    else:
        # 2. If not found, try to load from environment variable (for deployment)
        firebase_config_str = os.environ.get("__FIREBASE_CONFIG__")
        if firebase_config_str:
            # We need json to parse the string
            import json

            firebase_config = json.loads(firebase_config_str)
            cred = credentials.Certificate(firebase_config)
        else:
            raise FileNotFoundError("Could not find serviceAccountKey.json or __FIREBASE_CONFIG__ env var.")

    # Initialize the app if it's not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # 3. Check for auth token (for deployed environment)
    auth_token = os.environ.get("__INITIAL_AUTH_TOKEN__")
    if auth_token:
        try:
            # Verify the token to ensure our service has auth
            auth.verify_id_token(auth_token)
        except Exception as e:
            print(f"Auth token verification failed (this is ok on local): {e}")
            # This is okay if running locally, but good to know

    print("Firebase initialized successfully.")

except Exception as e:
    print(f"CRITICAL FIREBASE ERROR: {e}")
    print("Firebase did not initialize. The app will not be able to connect to the database.")
    db = None  # Ensure db is None if initialization fails


# --- Helper Function to get a collection reference ---
def get_collection(collection_name):
    """Helper to get a collection from the correct sandboxed path."""
    if not db:
        raise ConnectionError("Firestore database is not initialized.")
    return db.collection(f"{BASE_DB_PATH}/{collection_name}")


# --- Patients ---
def get_patients():
    patients_ref = get_collection('patients')
    docs = patients_ref.stream()
    patients = []
    for doc in docs:
        patient = doc.to_dict()
        patient['id'] = doc.id
        patients.append(patient)
    return patients


def add_patient(name, contact, history, dob, gender):
    patients_ref = get_collection('patients')
    doc_ref = patients_ref.document()
    doc_ref.set({
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,
        'gender': gender
    })
    return doc_ref.id


def update_patient(pid, name, contact, history, dob, gender):
    patients_ref = get_collection('patients')
    doc_ref = patients_ref.document(pid)
    doc_ref.update({
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,
        'gender': gender
    })


def delete_patient(pid):
    patients_ref = get_collection('patients')
    patients_ref.document(pid).delete()


# --- Doctors ---
def get_doctors():
    doctors_ref = get_collection('doctors')
    docs = doctors_ref.stream()
    doctors = []
    for doc in docs:
        doctor = doc.to_dict()
        doctor['id'] = doc.id
        doctors.append(doctor)
    return doctors


def add_doctor(name, specialty, schedule, fee):
    doctors_ref = get_collection('doctors')
    doc_ref = doctors_ref.document()
    doc_ref.set({
        'name': name,
        'specialty': specialty,
        'schedule': schedule,
        'fee': fee
    })
    return doc_ref.id


def update_doctor(did, name, specialty, schedule, fee):
    doctors_ref = get_collection('doctors')
    doc_ref = doctors_ref.document(did)
    doc_ref.update({
        'name': name,
        'specialty': specialty,
        'schedule': schedule,
        'fee': fee
    })


def delete_doctor(did):
    doctors_ref = get_collection('doctors')
    doctors_ref.document(did).delete()


# --- Appointments ---
def get_appointments():
    appts_ref = get_collection('appointments')
    docs = appts_ref.stream()
    appointments = []
    for doc in docs:
        appt = doc.to_dict()
        appt['id'] = doc.id
        appointments.append(appt)
    return appointments


def add_appointment(patient_id, doctor_id, datetime):
    appts_ref = get_collection('appointments')
    doc_ref = appts_ref.document()
    doc_ref.set({
        'patient': patient_id,  # Storing ID, not name
        'doctor': doctor_id,  # Storing ID, not name
        'datetime': datetime
    })
    return doc_ref.id


def update_appointment(aid, patient_id, doctor_id, datetime):
    appts_ref = get_collection('appointments')
    doc_ref = appts_ref.document(aid)
    doc_ref.update({
        'patient': patient_id,
        'doctor': doctor_id,
        'datetime': datetime
    })


def delete_appointment(aid):
    appts_ref = get_collection('appointments')
    appts_ref.document(aid).delete()


# --- Billing ---
def get_billing():
    billing_ref = get_collection('billing')
    docs = billing_ref.stream()
    bills = []
    for doc in docs:
        bill = doc.to_dict()
        bill['id'] = doc.id
        bills.append(bill)
    return bills


def add_bill(patient_id, items, total, status):
    billing_ref = get_collection('billing')
    doc_ref = billing_ref.document()
    doc_ref.set({
        'patient': patient_id,
        'items': items,
        'total': total,
        'status': status
    })
    return doc_ref.id


def update_bill(bid, patient_id, items, total, status):
    billing_ref = get_collection('billing')
    doc_ref = billing_ref.document(bid)
    doc_ref.update({
        'patient': patient_id,
        'items': items,
        'total': total,
        'status': status
    })


def delete_bill(bid):
    billing_ref = get_collection('billing')
    billing_ref.document(bid).delete()


# --- Inventory ---
def get_inventory():
    inventory_ref = get_collection('inventory')
    docs = inventory_ref.stream()
    items = []
    for doc in docs:
        item = doc.to_dict()
        item['id'] = doc.id
        items.append(item)
    return items


def add_inventory(item, quantity, supplier, price):
    inventory_ref = get_collection('inventory')
    doc_ref = inventory_ref.document()
    doc_ref.set({
        'item': item,
        'quantity': quantity,
        'supplier': supplier,
        'price': price
    })
    return doc_ref.id


def update_inventory(iid, item, quantity, supplier, price):
    inventory_ref = get_collection('inventory')
    doc_ref = inventory_ref.document(iid)
    doc_ref.update({
        'item': item,
        'quantity': quantity,
        'supplier': supplier,
        'price': price
    })


def delete_inventory(iid):
    inventory_ref = get_collection('inventory')
    inventory_ref.document(iid).delete()


# --- Transactional Logic ---

@firestore.transactional
def process_payment_transaction(transaction, bill_ref, bill_doc):
    """
    This is the core transactional logic.
    Firestore transactions require all reads before writes.
    """

    # --- 1. READ PHASE ---
    inventory_ref = get_collection('inventory')
    inventory_to_update = {}  # Stores refs and new stock levels

    for item in bill_doc.get('items'):
        item_id = item.get('id')

        # 'consult_fee' is not a real inventory item, so skip it
        if item_id == 'consult_fee':
            continue

        item_ref = inventory_ref.document(item_id)

        try:
            # Read the item from the database
            item_doc = item_ref.get(transaction=transaction)
        except Exception as e:
            raise Exception(f"Failed to read item '{item.get('name')}' from inventory. Error: {e}")

        if not item_doc.exists:
            raise Exception(f"Inventory item '{item.get('name')}' (ID: {item_id}) not found.")

        current_quantity = item_doc.to_dict().get('quantity', 0)
        new_quantity = current_quantity - item.get('quantity', 0)

        if new_quantity < 0:
            raise Exception(f"Not enough stock for '{item.get('name')}'. Only {current_quantity} left.")

        # Store the reference and new quantity for the write phase
        inventory_to_update[item_ref] = new_quantity

    # --- 2. WRITE PHASE ---

    # A. Update the bill status
    transaction.update(bill_ref, {
        'status': 'Paid'
    })

    # B. Update all inventory items
    for item_ref, new_quantity in inventory_to_update.items():
        transaction.update(item_ref, {
            'quantity': new_quantity
        })


def process_payment(bid):
    """
    Orchestrates the payment process using the transactional function.
    """
    if not db:
        raise ConnectionError("Firestore database is not initialized.")

    billing_ref = get_collection('billing')
    bill_ref = billing_ref.document(bid)

    # Get the bill document first, outside the transaction
    bill_doc = bill_ref.get()
    if not bill_doc.exists:
        raise Exception("Bill not found.")

    if bill_doc.to_dict().get('status') == 'Paid':
        raise Exception("This bill has already been paid.")

    transaction = db.transaction()
    process_payment_transaction(transaction, bill_ref, bill_doc)

