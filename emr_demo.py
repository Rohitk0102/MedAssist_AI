"""
EMR Demo Script for the Medical Appointment Scheduling AI Agent
Demonstrates the complete EMR functionality with Indian timezone and SQLite database
"""
import sys
import os
from datetime import datetime, timedelta, date
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlite_database import SQLiteMedicalDatabase
from emr_agent import emr_agent


def run_emr_demo():
    """Run a comprehensive demo of the EMR system"""
    print("🏥 MedAssist AI - EMR System Demo")
    print("=" * 50)
    print("📍 Configured for Indian Timezone (Asia/Kolkata)")
    print("📧 Email: originalgangstar9963@gmail.com")
    print("🗄️  Database: SQLite (patients.db)")
    print()
    
    # Initialize database
    print("📋 Initializing EMR Database...")
    db = SQLiteMedicalDatabase()
    
    # Generate synthetic data
    print("👥 Generating 50 synthetic patient records...")
    db.generate_synthetic_patients(50)
    
    # Add sample doctors
    print("👨‍⚕️ Adding sample doctors...")
    db.add_doctor(
        "doc_001", "Dr. Rajesh", "Kumar", "General Medicine",
        "+91-9876543210", "rajesh.kumar@clinic.com",
        '{"monday": {"start": "09:00", "end": "17:00"}, "tuesday": {"start": "09:00", "end": "17:00"}, "wednesday": {"start": "09:00", "end": "17:00"}, "thursday": {"start": "09:00", "end": "17:00"}, "friday": {"start": "09:00", "end": "17:00"}}'
    )
    
    db.add_doctor(
        "doc_002", "Dr. Priya", "Sharma", "Cardiology",
        "+91-9876543211", "priya.sharma@clinic.com",
        '{"monday": {"start": "08:00", "end": "16:00"}, "tuesday": {"start": "08:00", "end": "16:00"}, "wednesday": {"start": "08:00", "end": "16:00"}, "thursday": {"start": "08:00", "end": "16:00"}, "friday": {"start": "08:00", "end": "14:00"}}'
    )
    
    # Set up clinic settings
    db.update_clinic_settings(
        "MedAssist Medical Clinic",
        "123 Medical Street, Mumbai, Maharashtra 400001",
        "+91-22-12345678",
        "originalgangstar9963@gmail.com",
        "Asia/Kolkata"
    )
    
    print("✅ Database initialized successfully!")
    print()
    
    # Demonstrate EMR search functionality
    print("🔍 Demonstrating EMR Search Functionality")
    print("-" * 40)
    
    # Search by name
    print("1. Searching patients by name 'Rajesh'...")
    patients = db.search_patients(name="Rajesh")
    if patients:
        for patient in patients[:3]:  # Show first 3 results
            print(f"   ✅ Found: {patient['name']} (ID: {patient['patient_id']}) - {patient['patient_type']} patient")
    else:
        print("   ❌ No patients found with name 'Rajesh'")
    
    print()
    
    # Search by ID
    print("2. Searching patient by ID 1...")
    patient = db.get_patient_by_id(1)
    if patient:
        print(f"   ✅ Found: {patient['name']} (ID: {patient['patient_id']})")
        print(f"      Last Visit: {patient['last_visit_date']}")
        print(f"      Visits Count: {patient['visits_count']}")
        print(f"      Patient Type: {patient['patient_type']}")
    else:
        print("   ❌ Patient with ID 1 not found")
    
    print()
    
    # Get patient statistics
    print("3. Getting patient statistics...")
    stats = db.get_patient_statistics()
    print(f"   📊 Total Patients: {stats['total_patients']}")
    print(f"   🆕 New Patients: {stats['new_patients']}")
    print(f"   🔄 Returning Patients: {stats['returning_patients']}")
    print(f"   📈 Average Visits: {stats['average_visits']}")
    
    print()
    
    # Demonstrate new vs returning patient detection
    print("4. Demonstrating new vs returning patient detection...")
    all_patients = db.get_all_patients()
    new_patients = [p for p in all_patients if p['visits_count'] == 1]
    returning_patients = [p for p in all_patients if p['visits_count'] > 1]
    
    print(f"   🆕 New Patients (visits_count = 1): {len(new_patients)}")
    for patient in new_patients[:3]:  # Show first 3
        print(f"      - {patient['name']} (ID: {patient['patient_id']})")
    
    print(f"   🔄 Returning Patients (visits_count > 1): {len(returning_patients)}")
    for patient in returning_patients[:3]:  # Show first 3
        print(f"      - {patient['name']} (ID: {patient['patient_id']}) - {patient['visits_count']} visits")
    
    print()
    
    # Demonstrate appointment booking
    print("5. Demonstrating appointment booking...")
    if all_patients:
        patient = all_patients[0]
        appointment_time = datetime.now() + timedelta(days=1)
        appointment_time = appointment_time.replace(hour=10, minute=0, second=0, microsecond=0)
        
        appointment_id = db.add_appointment(
            patient['patient_id'], 
            "doc_001", 
            appointment_time, 
            "general", 
            "Demo appointment"
        )
        
        print(f"   ✅ Booked appointment for {patient['name']}")
        print(f"      Appointment ID: {appointment_id}")
        print(f"      Date & Time: {appointment_time.strftime('%Y-%m-%d %H:%M')} IST")
        print(f"      Doctor: Dr. Rajesh Kumar")
    
    print()
    
    # Demonstrate JSON output format
    print("6. Demonstrating JSON output format...")
    sample_patient = all_patients[0] if all_patients else None
    if sample_patient:
        json_output = {
            "patient_id": sample_patient['patient_id'],
            "name": sample_patient['name'],
            "last_visit_date": sample_patient['last_visit_date'],
            "visits_count": sample_patient['visits_count'],
            "patient_type": sample_patient['patient_type'],
            "is_new_patient": sample_patient['visits_count'] == 1,
            "is_returning_patient": sample_patient['visits_count'] > 1
        }
        
        print("   📄 Sample JSON output:")
        print(json.dumps(json_output, indent=2))
    
    print()
    
    # Show current time in Indian timezone
    print("7. Current time in Indian timezone...")
    import pytz
    
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    print(f"   🕐 Current IST: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    print()
    
    # Summary
    print("🎉 EMR Demo completed successfully!")
    print()
    print("📋 EMR System Features Demonstrated:")
    print("✅ SQLite database with patients table")
    print("✅ 50 synthetic patient records with Indian names")
    print("✅ Search EMR by patient name or ID")
    print("✅ Detect new vs returning patients")
    print("✅ JSON format output")
    print("✅ Indian timezone support (Asia/Kolkata)")
    print("✅ Email configuration (originalgangstar9963@gmail.com)")
    print("✅ Appointment booking functionality")
    print("✅ Patient statistics and analytics")
    print("✅ Agent Development Kit integration")
    
    print()
    print("🚀 The EMR system is ready for use!")
    print("   - Database file: patients.db")
    print("   - Timezone: Asia/Kolkata")
    print("   - Email: originalgangstar9963@gmail.com")
    print("   - Agent: emr_agent (ready for ADK)")
    
    return True


def interactive_emr_demo():
    """Run an interactive EMR demo"""
    print("🎮 MedAssist AI - Interactive EMR Demo")
    print("=" * 40)
    
    # Initialize database
    db = SQLiteMedicalDatabase()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Search patient by name")
        print("2. Search patient by ID")
        print("3. View patient statistics")
        print("4. Add new patient")
        print("5. Update patient visit")
        print("6. View all patients")
        print("7. Book appointment")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            name = input("Enter patient name to search: ").strip()
            patients = db.search_patients(name=name)
            if patients:
                print(f"\n✅ Found {len(patients)} patient(s):")
                for patient in patients:
                    print(f"   - {patient['name']} (ID: {patient['patient_id']}) - {patient['patient_type']}")
            else:
                print("❌ No patients found")
        
        elif choice == "2":
            try:
                patient_id = int(input("Enter patient ID: ").strip())
                patient = db.get_patient_by_id(patient_id)
                if patient:
                    print(f"\n✅ Found patient:")
                    print(f"   Name: {patient['name']}")
                    print(f"   ID: {patient['patient_id']}")
                    print(f"   Last Visit: {patient['last_visit_date']}")
                    print(f"   Visits: {patient['visits_count']}")
                    print(f"   Type: {patient['patient_type']}")
                else:
                    print("❌ Patient not found")
            except ValueError:
                print("❌ Invalid patient ID")
        
        elif choice == "3":
            stats = db.get_patient_statistics()
            print(f"\n📊 Patient Statistics:")
            print(f"   Total Patients: {stats['total_patients']}")
            print(f"   New Patients: {stats['new_patients']}")
            print(f"   Returning Patients: {stats['returning_patients']}")
            print(f"   Average Visits: {stats['average_visits']}")
        
        elif choice == "4":
            name = input("Enter patient name: ").strip()
            if name:
                patient_id = db.add_patient(name)
                print(f"✅ New patient '{name}' added with ID: {patient_id}")
            else:
                print("❌ Name cannot be empty")
        
        elif choice == "5":
            try:
                patient_id = int(input("Enter patient ID to update visit: ").strip())
                patient = db.get_patient_by_id(patient_id)
                if patient:
                    db.update_patient_visit(patient_id)
                    updated_patient = db.get_patient_by_id(patient_id)
                    print(f"✅ Visit updated for {updated_patient['name']}")
                    print(f"   New visits count: {updated_patient['visits_count']}")
                else:
                    print("❌ Patient not found")
            except ValueError:
                print("❌ Invalid patient ID")
        
        elif choice == "6":
            patients = db.get_all_patients()
            print(f"\n📋 All Patients ({len(patients)} total):")
            for patient in patients[:10]:  # Show first 10
                print(f"   {patient['patient_id']}: {patient['name']} - {patient['patient_type']} ({patient['visits_count']} visits)")
            if len(patients) > 10:
                print(f"   ... and {len(patients) - 10} more")
        
        elif choice == "7":
            try:
                patient_id = int(input("Enter patient ID: ").strip())
                patient = db.get_patient_by_id(patient_id)
                if patient:
                    print(f"Booking appointment for: {patient['name']}")
                    appointment_time = input("Enter appointment time (YYYY-MM-DD HH:MM): ").strip()
                    try:
                        appointment_dt = datetime.strptime(appointment_time, "%Y-%m-%d %H:%M")
                        appointment_id = db.add_appointment(patient_id, "doc_001", appointment_dt, "general")
                        print(f"✅ Appointment booked with ID: {appointment_id}")
                    except ValueError:
                        print("❌ Invalid date format")
                else:
                    print("❌ Patient not found")
            except ValueError:
                print("❌ Invalid patient ID")
        
        elif choice == "8":
            print("👋 Thanks for using MedAssist AI EMR!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_emr_demo()
    else:
        run_emr_demo()
