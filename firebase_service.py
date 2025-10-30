import firebase_admin
from firebase_admin import credentials, firestore

# --- Firebase Initialization ---
cred = credentials.Certificate('serviceAccountKey.json')
firebase_app = firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Platform-Specific Variables ---
# Get the app_id from the global environment (if it exists)
app_id = 'default-app-id'
try:
    if '__app_id' in globals():
        app_id = globals()['__app_id']
except NameError:
    pass  # Keep default-app-id


# --- Helper function to get the correct, sandboxed collection path ---
def get_collection_ref(collection_name):
    """
    Constructs the correct, platform-compliant path to a Firestore collection.
    This path is required for the app to have read/write permissions.
    Path: artifacts/{app_id}/public/data/{collection_name}
    """
    return db.collection('artifacts').document(app_id).collection('public').document('data').collection(collection_name)


# --- PATIENTS ---
def get_patients():
    docs = get_collection_ref('patients').stream()
    patients = []
    for doc in docs:
        patient_data = doc.to_dict()
        patient_data['id'] = doc.id
        patients.append(patient_data)
    return patients


def add_patient(name, contact, history):
    doc_ref = get_collection_ref('patients').add({
        'name': name,
        'contact': contact,
        'history': history
    })
    return doc_ref[1].id  # Return the new document ID


def update_patient(pid, name, contact, history):
    get_collection_ref('patients').document(pid).update({
        'name': name,
        'contact': contact,
        'history': history
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
    return bills


def add_bill(patient, amount, status):
    # Ensure amount is stored as a number, not a string
    try:
        numeric_amount = float(amount)
    except ValueError:
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
    except ValueError:
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
    return inventory


def add_inventory(item, quantity, supplier):
    try:
        numeric_quantity = int(quantity)
    except ValueError:
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
    except ValueError:
        numeric_quantity = 0

    get_collection_ref('inventory').document(iid).update({
        'item': item,
        'quantity': numeric_quantity,
        'supplier': supplier
    })


def delete_inventory(iid):
    get_collection_ref('inventory').document(iid).delete()


