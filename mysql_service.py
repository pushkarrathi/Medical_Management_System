import mysql.connector
from mysql.connector import Error
import json

# MySQL connection details
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345',
    'database': 'medai'
}

# Global connection
conn = None

def create_database_if_not_exists():
    """Create the 'medai' database if it doesn't exist."""
    try:
        temp_conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = temp_conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS medai")
        temp_conn.commit()
        cursor.close()
        temp_conn.close()
    except Error as e:
        print(f"Error creating database: {e}")

def create_tables():
    """Create necessary tables if they don't exist."""
    global conn
    if conn is None:
        return
    cursor = conn.cursor()

    # Patients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            contact VARCHAR(255),
            history TEXT,
            dob VARCHAR(255),
            gender VARCHAR(50)
        )
    """)

    # Doctors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            specialty VARCHAR(255),
            schedule TEXT,
            fee DECIMAL(10,2)
        )
    """)

    # Appointments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id VARCHAR(255) PRIMARY KEY,
            patient VARCHAR(255),
            doctor VARCHAR(255),
            datetime VARCHAR(255)
        )
    """)

    # Billing table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            id VARCHAR(255) PRIMARY KEY,
            patient VARCHAR(255),
            items JSON,
            total DECIMAL(10,2),
            status VARCHAR(50)
        )
    """)

    # Inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id VARCHAR(255) PRIMARY KEY,
            item VARCHAR(255),
            quantity INT,
            supplier VARCHAR(255),
            price DECIMAL(10,2)
        )
    """)

    conn.commit()
    cursor.close()

def init_mysql():
    """Initialize MySQL connection and create database/tables."""
    global conn
    try:
        create_database_if_not_exists()
        conn = mysql.connector.connect(**DB_CONFIG)
        create_tables()
        print("MySQL initialized successfully.")
    except Error as e:
        print(f"Error initializing MySQL: {e}")
        conn = None

# Initialize on import
init_mysql()

# --- Helper functions ---
def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally fetch results."""
    if conn is None:
        raise ConnectionError("MySQL is not initialized.")
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    if fetch:
        result = cursor.fetchall()
    else:
        conn.commit()
        result = None
    cursor.close()
    return result

# --- Patients ---
def add_patient_mysql(pid, name, contact, history, dob, gender):
    query = """
        INSERT INTO patients (id, name, contact, history, dob, gender)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name=VALUES(name), contact=VALUES(contact), history=VALUES(history), dob=VALUES(dob), gender=VALUES(gender)
    """
    execute_query(query, (pid, name, contact, history, dob, gender))

def update_patient_mysql(pid, name, contact, history, dob, gender):
    query = """
        UPDATE patients SET name=%s, contact=%s, history=%s, dob=%s, gender=%s WHERE id=%s
    """
    execute_query(query, (name, contact, history, dob, gender, pid))

def delete_patient_mysql(pid):
    query = "DELETE FROM patients WHERE id=%s"
    execute_query(query, (pid,))

# --- Doctors ---
def add_doctor_mysql(did, name, specialty, schedule, fee):
    query = """
        INSERT INTO doctors (id, name, specialty, schedule, fee)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name=VALUES(name), specialty=VALUES(specialty), schedule=VALUES(schedule), fee=VALUES(fee)
    """
    execute_query(query, (did, name, specialty, schedule, fee))

def update_doctor_mysql(did, name, specialty, schedule, fee):
    query = """
        UPDATE doctors SET name=%s, specialty=%s, schedule=%s, fee=%s WHERE id=%s
    """
    execute_query(query, (name, specialty, schedule, fee, did))

def delete_doctor_mysql(did):
    query = "DELETE FROM doctors WHERE id=%s"
    execute_query(query, (did,))

# --- Appointments ---
def add_appointment_mysql(aid, patient_id, doctor_id, datetime):
    query = """
        INSERT INTO appointments (id, patient, doctor, datetime)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        patient=VALUES(patient), doctor=VALUES(doctor), datetime=VALUES(datetime)
    """
    execute_query(query, (aid, patient_id, doctor_id, datetime))

def update_appointment_mysql(aid, patient_id, doctor_id, datetime):
    query = """
        UPDATE appointments SET patient=%s, doctor=%s, datetime=%s WHERE id=%s
    """
    execute_query(query, (patient_id, doctor_id, datetime, aid))

def delete_appointment_mysql(aid):
    query = "DELETE FROM appointments WHERE id=%s"
    execute_query(query, (aid,))

# --- Billing ---
def add_bill_mysql(bid, patient_id, items, total, status):
    items_json = json.dumps(items)
    query = """
        INSERT INTO billing (id, patient, items, total, status)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        patient=VALUES(patient), items=VALUES(items), total=VALUES(total), status=VALUES(status)
    """
    execute_query(query, (bid, patient_id, items_json, total, status))

def update_bill_mysql(bid, patient_id, items, total, status):
    items_json = json.dumps(items)
    query = """
        UPDATE billing SET patient=%s, items=%s, total=%s, status=%s WHERE id=%s
    """
    execute_query(query, (patient_id, items_json, total, status, bid))

def delete_bill_mysql(bid):
    query = "DELETE FROM billing WHERE id=%s"
    execute_query(query, (bid,))

def process_payment_mysql(bid):
    # For simplicity, just update status to 'Paid' (inventory update would require more complex logic)
    query = "UPDATE billing SET status='Paid' WHERE id=%s"
    execute_query(query, (bid,))

# --- Inventory ---
def add_inventory_mysql(iid, item, quantity, supplier, price):
    query = """
        INSERT INTO inventory (id, item, quantity, supplier, price)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        item=VALUES(item), quantity=VALUES(quantity), supplier=VALUES(supplier), price=VALUES(price)
    """
    execute_query(query, (iid, item, quantity, supplier, price))

def update_inventory_mysql(iid, item, quantity, supplier, price):
    query = """
        UPDATE inventory SET item=%s, quantity=%s, supplier=%s, price=%s WHERE id=%s
    """
    execute_query(query, (item, quantity, supplier, price, iid))

def delete_inventory_mysql(iid):
    query = "DELETE FROM inventory WHERE id=%s"
    execute_query(query, (iid,))
