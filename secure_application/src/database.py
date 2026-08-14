import os
import sqlite3
import hashlib
import time
from typing import Optional, List, Dict

DB_FILENAME = os.path.join(os.path.dirname(__file__), "hospital.db")


def get_conn():
    conn = sqlite3.connect(DB_FILENAME)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def init_db():
    """Create tables and seed initial users if needed."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            address TEXT,
            created_at INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            reason TEXT,
            created_at INTEGER,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES users(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            medication TEXT NOT NULL,
            instructions TEXT,
            created_at INTEGER,
            FOREIGN KEY(appointment_id) REFERENCES appointments(id),
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES users(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            note TEXT,
            created_at INTEGER,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES users(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            paid INTEGER DEFAULT 0,
            created_at INTEGER,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """
    )

    conn.commit()

    # Seed users if not present
    cur.execute("SELECT COUNT(1) as cnt FROM users")
    cnt = cur.fetchone()["cnt"]
    if cnt == 0:
        # default admin and doctor
        create_user("admin", "admin", "ADMIN")
        create_user("doctor", "doc", "DOCTOR")

    conn.close()


# User helpers
def create_user(username: str, password: str, role: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    password_hash = _hash_text(password)
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


# Patient helpers
def create_patient(name: str, age: int, gender: str, contact: str, address: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (name, age, gender, contact, address, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, age, gender, contact, address, int(time.time())),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def list_patients() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, gender, contact, address, created_at FROM patients ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_patient(patient_id: int) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# Appointments
def create_appointment(patient_id: int, doctor_id: int, datetime_str: str, reason: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO appointments (patient_id, doctor_id, datetime, reason, created_at) VALUES (?, ?, ?, ?, ?)",
        (patient_id, doctor_id, datetime_str, reason, int(time.time())),
    )
    conn.commit()
    aid = cur.lastrowid
    conn.close()
    return aid


def list_appointments(doctor_id: Optional[int] = None) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    if doctor_id:
        cur.execute(
            "SELECT a.id, a.patient_id, p.name as patient_name, a.doctor_id, u.username as doctor_name, a.datetime, a.reason FROM appointments a JOIN patients p ON a.patient_id = p.id JOIN users u ON a.doctor_id = u.id WHERE a.doctor_id = ? ORDER BY a.datetime",
            (doctor_id,),
        )
    else:
        cur.execute(
            "SELECT a.id, a.patient_id, p.name as patient_name, a.doctor_id, u.username as doctor_name, a.datetime, a.reason FROM appointments a JOIN patients p ON a.patient_id = p.id JOIN users u ON a.doctor_id = u.id ORDER BY a.datetime"
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# Prescriptions
def create_prescription(appointment_id: Optional[int], patient_id: int, doctor_id: int, medication: str, instructions: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, medication, instructions, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (appointment_id, patient_id, doctor_id, medication, instructions, int(time.time())),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def list_prescriptions_by_patient(patient_id: int) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT pr.id, pr.appointment_id, pr.medication, pr.instructions, pr.created_at, u.username as doctor_name FROM prescriptions pr LEFT JOIN users u ON pr.doctor_id = u.id WHERE pr.patient_id = ? ORDER BY pr.created_at DESC",
        (patient_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# Medical records
def add_medical_record(patient_id: int, doctor_id: Optional[int], note: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO medical_records (patient_id, doctor_id, note, created_at) VALUES (?, ?, ?, ?)",
        (patient_id, doctor_id, note, int(time.time())),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def list_medical_records_by_patient(patient_id: int) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT mr.id, mr.note, mr.created_at, u.username as doctor_name FROM medical_records mr LEFT JOIN users u ON mr.doctor_id = u.id WHERE mr.patient_id = ? ORDER BY mr.created_at DESC",
        (patient_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# Billing
def create_bill(patient_id: int, description: str, amount: float) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bills (patient_id, description, amount, paid, created_at) VALUES (?, ?, ?, 0, ?)",
        (patient_id, description, amount, int(time.time())),
    )
    conn.commit()
    bid = cur.lastrowid
    conn.close()
    return bid


def list_bills_by_patient(patient_id: int) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, description, amount, paid, created_at FROM bills WHERE patient_id = ? ORDER BY created_at DESC",
        (patient_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def mark_bill_paid(bill_id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE bills SET paid = 1 WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()


# Utility: list doctors
def list_doctors() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE role = 'DOCTOR'")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
