"""Hospital Management CLI application."""

import sys
import database
import auth
from typing import Optional


HEADER = "=" * 39 + "\n       HOSPITAL MANAGEMENT SYSTEM\n" + "=" * 39


def prompt_int(prompt: str, allow_empty: bool = False) -> Optional[int]:
    while True:
        val = input(prompt).strip()
        if allow_empty and val == "":
            return None
        try:
            return int(val)
        except ValueError:
            print("Please enter a valid number.")


def prompt_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Value cannot be empty.")


def login_flow():
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = auth.login(username, password)
    if not user:
        print("Login failed: invalid credentials")
        return None
    print(f"Logged in as {user['username']} ({user['role']})")
    return user


def register_patient_flow():
    name = prompt_nonempty("Patient name: ")
    age = prompt_int("Age: ")
    gender = input("Gender: ").strip()
    contact = input("Contact: ").strip()
    address = input("Address: ").strip()
    pid = database.create_patient(name, age or 0, gender, contact, address)
    print(f"Patient created with ID {pid}")


def view_patients_flow():
    patients = database.list_patients()
    if not patients:
        print("No patients found.")
        return
    print("Patients:")
    for p in patients:
        print(f"ID: {p['id']} | Name: {p['name']} | Age: {p['age']} | Gender: {p['gender']} | Contact: {p['contact']}")


def book_appointment_flow(current_user):
    patients = database.list_patients()
    if not patients:
        print("No patients available. Register a patient first.")
        return
    print("Select patient:")
    for p in patients:
        print(f"{p['id']}: {p['name']}")
    pid = prompt_int("Patient ID: ")
    patient = database.get_patient(pid)
    if not patient:
        print("Invalid patient ID")
        return
    doctors = database.list_doctors()
    if not doctors:
        print("No doctors available.")
        return
    print("Select doctor:")
    for d in doctors:
        print(f"{d['id']}: Dr. {d['username']}")
    did = prompt_int("Doctor ID: ")
    # basic datetime as string
    dt = prompt_nonempty("Appointment date/time (e.g. 2026-08-14 15:30): ")
    reason = input("Reason: ").strip()
    aid = database.create_appointment(pid, did, dt, reason)
    print(f"Appointment booked with ID {aid}")


def view_appointments_flow(current_user):
    if current_user['role'] == 'DOCTOR':
        appts = database.list_appointments(doctor_id=current_user['id'])
    else:
        appts = database.list_appointments()
    if not appts:
        print("No appointments found.")
        return
    print("Appointments:")
    for a in appts:
        print(f"ID: {a['id']} | Patient: {a['patient_name']} | Doctor: {a['doctor_name']} | When: {a['datetime']} | Reason: {a['reason']}")


def add_prescription_flow(current_user):
    if current_user['role'] != 'DOCTOR':
        print("Only DOCTOR role can add prescriptions.")
        return
    # List appointments for this doctor
    appts = database.list_appointments(doctor_id=current_user['id'])
    if not appts:
        print("No appointments found for you. You can still prescribe by entering patient ID.")
    else:
        print("Your appointments:")
        for a in appts:
            print(f"{a['id']}: Patient {a['patient_name']} at {a['datetime']}")
    appt_id = prompt_int("Appointment ID (or press Enter to skip): ", allow_empty=True)
    if appt_id:
        # fetch appointment patient id
        pass
    patient_id = prompt_int("Patient ID: ")
    patient = database.get_patient(patient_id)
    if not patient:
        print("Invalid patient ID")
        return
    med = prompt_nonempty("Medication (name, dose): ")
    instr = input("Instructions: ").strip()
    pres_id = database.create_prescription(appt_id, patient_id, current_user['id'], med, instr)
    # add to medical records
    database.add_medical_record(patient_id, current_user['id'], f"Prescription: {med} - {instr}")
    print(f"Prescription added with ID {pres_id}")


def view_medical_records_flow():
    pid = prompt_int("Patient ID to view records: ")
    patient = database.get_patient(pid)
    if not patient:
        print("Invalid patient ID")
        return
    print(f"Medical records for {patient['name']}:")
    records = database.list_medical_records_by_patient(pid)
    if not records:
        print("No medical records found.")
    else:
        for r in records:
            doc = r.get('doctor_name') or 'System'
            print(f"- {r['created_at']}: by {doc} | {r['note']}")
    print("Prescriptions:")
    pres = database.list_prescriptions_by_patient(pid)
    if not pres:
        print("No prescriptions.")
    else:
        for p in pres:
            doc = p.get('doctor_name') or 'Unknown'
            print(f"- {p['created_at']}: by {doc} | {p['medication']} | {p['instructions']}")


def billing_flow(current_user):
    pid = prompt_int("Patient ID for bill: ")
    patient = database.get_patient(pid)
    if not patient:
        print("Invalid patient ID")
        return
    print("Existing bills:")
    bills = database.list_bills_by_patient(pid)
    if bills:
        for b in bills:
            status = 'PAID' if b['paid'] else 'UNPAID'
            print(f"{b['id']}: {b['description']} - {b['amount']} ({status})")
    else:
        print("No bills yet.")
    choice = input("Add new bill? (y/N): ").strip().lower()
    if choice == 'y':
        desc = prompt_nonempty("Description: ")
        while True:
            amt_str = input("Amount: ").strip()
            try:
                amt = float(amt_str)
                break
            except ValueError:
                print("Enter a valid amount number.")
        bid = database.create_bill(pid, desc, amt)
        print(f"Bill created with ID {bid}")
    pay = input("Mark a bill paid? (y/N): ").strip().lower()
    if pay == 'y':
        bid = prompt_int("Bill ID to mark paid: ")
        database.mark_bill_paid(bid)
        print("Bill marked paid.")


def main_loop():
    current_user = None
    while True:
        print("\n" + HEADER)
        print("\n1. Login\n2. Register Patient\n3. View Patients\n4. Book Appointment\n5. View Appointments\n6. Add Prescription\n7. View Medical Records\n8. Generate/View Bill\n9. Exit\n")
        try:
            choice = input("Select option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting")
            return
        if choice == '1':
            user = login_flow()
            if user:
                current_user = user
        elif choice == '2':
            if not current_user:
                print("Please login first.")
                continue
            register_patient_flow()
        elif choice == '3':
            if not current_user:
                print("Please login first.")
                continue
            view_patients_flow()
        elif choice == '4':
            if not current_user:
                print("Please login first.")
                continue
            book_appointment_flow(current_user)
        elif choice == '5':
            if not current_user:
                print("Please login first.")
                continue
            view_appointments_flow(current_user)
        elif choice == '6':
            if not current_user:
                print("Please login first.")
                continue
            add_prescription_flow(current_user)
        elif choice == '7':
            if not current_user:
                print("Please login first.")
                continue
            view_medical_records_flow()
        elif choice == '8':
            if not current_user:
                print("Please login first.")
                continue
            billing_flow(current_user)
        elif choice == '9':
            print("Goodbye")
            return
        else:
            print("Invalid option. Choose 1-9.")


def main():
    database.init_db()
    print("Starting Hospital Management System")
    main_loop()


if __name__ == '__main__':
    main()