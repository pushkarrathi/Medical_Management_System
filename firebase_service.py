import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# --- Firebase Initialization ---
# Get the app_id from the global environment (if it exists)
app_id = 'default-app-id'
if os.environ.get('APP_ID'):
    app_id = os.environ.get('APP_ID')

try:
    # Check if the app is already initialized
    firebase_admin.get_app()
except ValueError:
    # App not initialized, so initialize it
    cred_path = 'serviceAccountKey.json'
    if not os.path.exists(cred_path):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: serviceAccountKey.json not found.           !!!")
        print("!!! Please download it from your Firebase project      !!!")
        print("!!! settings and place it in the root directory.       !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

db = firestore.client()


# --- Helper function to get the correct, sandboxed collection path ---
def get_collection_ref(collection_name):
    """
    Constructs the correct, platform-compliant path to a Firestore collection.
    This path is required for the app to have read/write permissions.
    Path: artifacts/{app_id}/public/data/{collection_name}
    """
    return db.collection('artifacts').document(app_id).collection('public').document('data').collection(collection_name)


# --- Helper function to calculate age ---
def _calculate_age(dob_string):
    """Calculates age from a YYYY-MM-DD date string."""
    if not dob_string:
        return ''
    try:
        dob = datetime.strptime(dob_string, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return ''  # Return empty if date is invalid


# --- PATIENTS ---
def get_patients():
    docs = get_collection_ref('patients').stream()
    patients = []
    for doc in docs:
        patient_data = doc.to_dict()
        patient_data['id'] = doc.id
        # MODIFIED: Calculate age from DOB
        patient_data['age'] = _calculate_age(patient_data.get('dob'))
        patients.append(patient_data)
    # Sort by name by default
    patients.sort(key=lambda x: x.get('name', '').lower())
    return patients


def add_patient(name, contact, history, dob, gender):
    """
    MODIFIED: Now accepts dob instead of age.
    """
    doc_ref = get_collection_ref('patients').add({
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,  # Stored DOB
        'gender': gender
    })
    return doc_ref[1].id  # Return the new document ID


def update_patient(pid, name, contact, history, dob, gender):
    """
    MODIFIED: Now accepts dob instead of age.
    """
    get_collection_ref('patients').document(pid).update({
        'name': name,
        'contact': contact,
        'history': history,
        'dob': dob,  # Stored DOB
        'gender': gender
    })


def delete_patient(pid):
    get_collection_ref('patients').document(pid).delete()


# --- DOCTORS ---
def get_doctors():
    docs = get_collection_ref('doctors').stream()
    doctors = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        doctors.append(doc_data)
    doctors.sort(key=lambda x: x.get('name', '').lower())
    return doctors


def add_doctor(name, specialty, schedule):
    doc_ref = get_collection_ref('doctors').add({
        'name': name,
        'specialty': specialty,
        'schedule': schedule
    })
    return doc_ref[1].id


def update_doctor(did, name, specialty, schedule):
    get_collection_ref('doctors').document(did).update({
        'name': name,
        'specialty': specialty,
        'schedule': schedule
    })


def delete_doctor(did):
    get_collection_ref('doctors').document(did).delete()


# --- APPOINTMENTS ---
def get_appointments():
    docs = get_collection_ref('appointments').stream()
    appointments = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        appointments.append(doc_data)
    appointments.sort(key=lambda x: x.get('datetime', ''))
    return appointments


def add_appointment(patient, doctor, datetime):
    doc_ref = get_collection_ref('appointments').add({
        'patient': patient,
        'doctor': doctor,
        'datetime': datetime
    })
    return doc_ref[1].id


def update_appointment(aid, patient, doctor, datetime):
    get_collection_ref('appointments').document(aid).update({
        'patient': patient,
        'doctor': doctor,
        'datetime': datetime
    })


def delete_appointment(aid):
    get_collection_ref('appointments').document(aid).delete()


# --- BILLING ---
def get_bills():
    docs = get_collection_ref('billing').stream()
    bills = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        bills.append(doc_data)
    bills.sort(key=lambda x: x.get('patient', '').lower())
    return bills


def add_bill(patient, amount, status):
    # Ensure amount is stored as a number, not a string
    try:
        numeric_amount = float(amount)
    except (ValueError, TypeError):
        numeric_amount = 0.0

    doc_ref = get_collection_ref('billing').add({
        'patient': patient,
        'amount': numeric_amount,
        'status': status
    })
    return doc_ref[1].id


def update_bill(bid, patient, amount, status):
    try:
        numeric_amount = float(amount)
    except (ValueError, TypeError):
        numeric_amount = 0.0

    get_collection_ref('billing').document(bid).update({
        'patient': patient,
        'amount': numeric_amount,
        'status': status
    })


def delete_bill(bid):
    get_collection_ref('billing').document(bid).delete()


# --- INVENTORY ---
def get_inventory():
    docs = get_collection_ref('inventory').stream()
    inventory = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data['id'] = doc.id
        inventory.append(doc_data)
    inventory.sort(key=lambda x: x.get('item', '').lower())
    return inventory


def add_inventory(item, quantity, supplier):
    try:
        numeric_quantity = int(quantity)
    except (ValueError, TypeError):
        numeric_quantity = 0

    doc_ref = get_collection_ref('inventory').add({
        'item': item,
        'quantity': numeric_quantity,
        'supplier': supplier
    })
    return doc_ref[1].id


def update_inventory(iid, item, quantity, supplier):
    try:
        numeric_quantity = int(quantity)
    except (ValueError, TypeError):
        numeric_quantity = 0

    get_collection_ref('inventory').document(iid).update({
        'item': item,
        'quantity': numeric_quantity,
        'supplier': supplier
    })


def delete_inventory(iid):
    get_collection_ref('inventory').document(iid).delete()

