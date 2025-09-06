"""
Setup script for MedAssist AI EMR System
Initializes the complete EMR system with Indian timezone and email configuration
"""
import os
import sys
from datetime import datetime
from sqlite_database import SQLiteMedicalDatabase
from emr_agent import emr_agent


def setup_emr_system():
    """Initialize the complete EMR system"""
    print("🏥 MedAssist AI EMR System Setup")
    print("=" * 50)
    print("📍 Indian Timezone: Asia/Kolkata")
    print("📧 Email: originalgangstar9963@gmail.com")
    print("🗄️  Database: SQLite (patients.db)")
    print()
    
    # Initialize database
    print("📋 Initializing SQLite database...")
    db = SQLiteMedicalDatabase()
    print("✅ Database initialized")
    
    # Generate synthetic patients
    print("👥 Generating 50 synthetic patient records...")
    db.generate_synthetic_patients(50)
    print("✅ Patient records generated")
    
    # Add sample doctors
    print("👨‍⚕️ Adding sample doctors...")
    doctors = [
        {
            "id": "doc_001",
            "first_name": "Dr. Rajesh",
            "last_name": "Kumar",
            "specialty": "General Medicine",
            "phone": "+91-9876543210",
            "email": "rajesh.kumar@clinic.com"
        },
        {
            "id": "doc_002", 
            "first_name": "Dr. Priya",
            "last_name": "Sharma",
            "specialty": "Cardiology",
            "phone": "+91-9876543211",
            "email": "priya.sharma@clinic.com"
        },
        {
            "id": "doc_003",
            "first_name": "Dr. Amit",
            "last_name": "Patel",
            "specialty": "Pediatrics",
            "phone": "+91-9876543212",
            "email": "amit.patel@clinic.com"
        }
    ]
    
    working_hours = '{"monday": {"start": "09:00", "end": "17:00"}, "tuesday": {"start": "09:00", "end": "17:00"}, "wednesday": {"start": "09:00", "end": "17:00"}, "thursday": {"start": "09:00", "end": "17:00"}, "friday": {"start": "09:00", "end": "17:00"}}'
    
    for doctor in doctors:
        db.add_doctor(
            doctor["id"], doctor["first_name"], doctor["last_name"],
            doctor["specialty"], doctor["phone"], doctor["email"], working_hours
        )
        print(f"✅ Added: {doctor['first_name']} {doctor['last_name']} ({doctor['specialty']})")
    
    # Set up clinic settings
    print("🏥 Configuring clinic settings...")
    db.update_clinic_settings(
        "MedAssist Medical Clinic",
        "123 Medical Street, Mumbai, Maharashtra 400001",
        "+91-22-12345678",
        "originalgangstar9963@gmail.com",
        "Asia/Kolkata"
    )
    print("✅ Clinic settings configured")
    
    # Create necessary directories
    directories = ["logs", "backups", "reports"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Verify setup
    print("\n🔍 Verifying setup...")
    stats = db.get_patient_statistics()
    print(f"✅ Total patients: {stats['total_patients']}")
    print(f"✅ New patients: {stats['new_patients']}")
    print(f"✅ Returning patients: {stats['returning_patients']}")
    
    doctors = db.get_doctors()
    print(f"✅ Doctors added: {len(doctors)}")
    
    settings = db.get_clinic_settings()
    if settings:
        print(f"✅ Clinic: {settings['clinic_name']}")
        print(f"✅ Timezone: {settings['timezone']}")
        print(f"✅ Email: {settings['email']}")
    
    print("\n🎉 EMR System setup completed successfully!")
    print("\n📋 System Features:")
    print("✅ SQLite database with patients table")
    print("✅ 50 synthetic patient records with Indian names")
    print("✅ EMR search by name and ID")
    print("✅ New vs returning patient detection")
    print("✅ JSON format output")
    print("✅ Indian timezone support (Asia/Kolkata)")
    print("✅ Email configuration (originalgangstar9963@gmail.com)")
    print("✅ Agent Development Kit integration")
    print("✅ Appointment booking functionality")
    
    print("\n🚀 Next steps:")
    print("1. Run 'python emr_demo.py' to see the system in action")
    print("2. Run 'python emr_demo.py interactive' for interactive demo")
    print("3. Use 'emr_agent' for Agent Development Kit integration")
    print("4. Configure email settings in .env file if needed")
    
    return True


def show_system_status():
    """Show current system status"""
    print("🏥 MedAssist AI EMR System Status")
    print("=" * 40)
    
    try:
        db = SQLiteMedicalDatabase()
        
        # Check database
        stats = db.get_patient_statistics()
        print(f"📊 Database Status:")
        print(f"   Total Patients: {stats['total_patients']}")
        print(f"   New Patients: {stats['new_patients']}")
        print(f"   Returning Patients: {stats['returning_patients']}")
        print(f"   Average Visits: {stats['average_visits']}")
        
        # Check doctors
        doctors = db.get_doctors()
        print(f"\n👨‍⚕️ Doctors: {len(doctors)}")
        for doctor in doctors:
            print(f"   - {doctor['first_name']} {doctor['last_name']} ({doctor['specialty']})")
        
        # Check clinic settings
        settings = db.get_clinic_settings()
        if settings:
            print(f"\n🏥 Clinic Settings:")
            print(f"   Name: {settings['clinic_name']}")
            print(f"   Address: {settings['address']}")
            print(f"   Phone: {settings['phone']}")
            print(f"   Email: {settings['email']}")
            print(f"   Timezone: {settings['timezone']}")
        
        # Check appointments
        appointments = db.get_appointments()
        print(f"\n📅 Appointments: {len(appointments)}")
        
        print(f"\n✅ System is ready and operational!")
        
    except Exception as e:
        print(f"❌ System error: {e}")
        print("Run 'python setup_emr.py setup' to initialize the system")


def reset_emr_system():
    """Reset the EMR system (use with caution!)"""
    print("⚠️  WARNING: This will delete all EMR data!")
    response = input("Are you sure you want to reset? Type 'yes' to confirm: ")
    
    if response.lower() == 'yes':
        try:
            # Remove database file
            if os.path.exists("patients.db"):
                os.remove("patients.db")
                print("✅ Database file removed")
            
            # Remove other data files
            data_files = [
                "data/patients.json",
                "data/doctors.json", 
                "data/appointments.json",
                "data/no_show_predictions.json",
                "data/clinic_settings.json"
            ]
            
            for file_path in data_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✅ Removed: {file_path}")
            
            print("✅ EMR system reset completed")
            print("Run 'python setup_emr.py setup' to reinitialize")
            return True
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            return False
    else:
        print("❌ Reset cancelled")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_emr_system()
        elif command == "status":
            show_system_status()
        elif command == "reset":
            reset_emr_system()
        else:
            print("Usage: python setup_emr.py [setup|status|reset]")
    else:
        setup_emr_system()
