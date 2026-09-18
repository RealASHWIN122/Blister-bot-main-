import sqlite3
import os

DB_NAME = 'attendance.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Use IF NOT EXISTS to preserve data across reboots
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caretakers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            work_shift TEXT,
            is_patient BOOLEAN,
            face_path TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            health_issues TEXT,
            med_schedule TEXT,
            assigned_caretaker_id INTEGER,
            face_path TEXT,
            FOREIGN KEY(assigned_caretaker_id) REFERENCES caretakers(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            med_name TEXT NOT NULL,
            dosage TEXT,
            slot_index INTEGER,
            med_count INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def add_caretaker(name, work_shift, is_patient, face_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO caretakers (name, work_shift, is_patient, face_path)
        VALUES (?, ?, ?, ?)
    ''', (name, work_shift, is_patient, face_path))
    c_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return c_id

def add_patient(name, age, gender, health_issues, med_schedule, assigned_caretaker_id, face_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO patients (name, age, gender, health_issues, med_schedule, assigned_caretaker_id, face_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, gender, health_issues, med_schedule, assigned_caretaker_id, face_path))
    p_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return p_id

def add_inventory(med_name, dosage, slot_index, med_count):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventory (med_name, dosage, slot_index, med_count)
        VALUES (?, ?, ?, ?)
    ''', (med_name, dosage, slot_index, med_count))
    inv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inv_id

def get_inventory(med_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    if med_name:
        cursor.execute('SELECT * FROM inventory WHERE med_name = ?', (med_name,))
        res = cursor.fetchone()
    else:
        cursor.execute('SELECT * FROM inventory')
        res = cursor.fetchall()
    conn.close()
    return res

def decrement_inventory(med_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE inventory SET med_count = med_count - 1 WHERE med_name = ?', (med_name,))
    conn.commit()
    
    cursor.execute('SELECT med_count FROM inventory WHERE med_name = ?', (med_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_person_by_id(person_id, is_caretaker=True):
    conn = get_connection()
    cursor = conn.cursor()
    table = "caretakers" if is_caretaker else "patients"
    cursor.execute(f'SELECT * FROM {table} WHERE id = ?', (person_id,))
    res = cursor.fetchone()
    conn.close()
    return res

def get_patient_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    # Use LIKE for fuzzy matching
    cursor.execute('SELECT * FROM patients WHERE name LIKE ?', (f'%{name}%',))
    res = cursor.fetchone()
    
    if res:
        # Map row to dictionary for easier access
        columns = [column[0] for column in cursor.description]
        patient_dict = dict(zip(columns, res))
        conn.close()
        return patient_dict
    
    conn.close()
    return None

def update_patient(name, updates_dict):
    conn = get_connection()
    cursor = conn.cursor()
    
    # First, find the patient ID
    cursor.execute('SELECT id FROM patients WHERE name LIKE ?', (f'%{name}%',))
    res = cursor.fetchone()
    
    if not res:
        conn.close()
        return False
        
    patient_id = res[0]
    
    # Build the SET clause
    set_clauses = []
    values = []
    
    valid_columns = ['name', 'age', 'gender', 'health_issues', 'med_schedule', 'assigned_caretaker_id', 'face_path']
    for key, val in updates_dict.items():
        if key in valid_columns:
            set_clauses.append(f"{key} = ?")
            values.append(val)
            
    if not set_clauses:
        conn.close()
        return False
        
    values.append(patient_id)
    query = f"UPDATE patients SET {', '.join(set_clauses)} WHERE id = ?"
    
    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()
    return True

# Initialize database when this module is loaded
init_db()
