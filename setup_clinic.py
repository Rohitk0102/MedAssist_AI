"""
Setup script for initializing the Medical Appointment Scheduling AI Agent
"""
import os
import sys
from datetime import datetime
from database import MedicalDatabase
from models import Doctor, ClinicSettings
from config import get_config


def setup_clinic():
    """Initialize the clinic with default settings and sample data"""
    print("🏥 Setting up MedAssist AI Medical Clinic...")
    
    # Initialize database
    db = MedicalDatabase()
    print("✅ Database initialized")
    
    # Setup clinic settings
    config = get_config()
    clinic_settings = config.get_default_clinic_settings()
    db.update_clinic_settings(clinic_settings)
    print(f"✅ Clinic settings configured: {clinic_settings.clinic_name}")
    
    # Add sample doctors
    sample_doctors = [
        Doctor(
            id="doc_001",
            first_name="Sarah",
            last_name="Johnson",
            specialty="Internal Medicine",
            phone="(555) 123-4567",
            email="sarah.johnson@medassist.com",
            working_hours={
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "15:00"},
                "saturday": {"start": "10:00", "end": "14:00"},
                "sunday": {"start": "10:00", "end": "12:00"}
            },
            appointment_duration=30,
            max_patients_per_day=20
        ),
        Doctor(
            id="doc_002",
            first_name="Michael",
            last_name="Chen",
            specialty="Cardiology",
            phone="(555) 123-4568",
            email="michael.chen@medassist.com",
            working_hours={
                "monday": {"start": "08:00", "end": "16:00"},
                "tuesday": {"start": "08:00", "end": "16:00"},
                "wednesday": {"start": "08:00", "end": "16:00"},
                "thursday": {"start": "08:00", "end": "16:00"},
                "friday": {"start": "08:00", "end": "14:00"},
                "saturday": {"start": "09:00", "end": "13:00"},
                "sunday": {"start": "09:00", "end": "11:00"}
            },
            appointment_duration=45,
            max_patients_per_day=15
        ),
        Doctor(
            id="doc_003",
            first_name="Emily",
            last_name="Rodriguez",
            specialty="Pediatrics",
            phone="(555) 123-4569",
            email="emily.rodriguez@medassist.com",
            working_hours={
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "16:00"},
                "saturday": {"start": "10:00", "end": "15:00"},
                "sunday": {"start": "10:00", "end": "12:00"}
            },
            appointment_duration=30,
            max_patients_per_day=25
        )
    ]
    
    for doctor in sample_doctors:
        if db.add_doctor(doctor):
            print(f"✅ Added doctor: Dr. {doctor.first_name} {doctor.last_name} ({doctor.specialty})")
        else:
            print(f"⚠️  Doctor already exists: Dr. {doctor.first_name} {doctor.last_name}")
    
    # Create necessary directories
    directories = ["data", "logs", "backups", "reports"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Validate configuration
    validation_result = config.validate_config()
    if validation_result["valid"]:
        print("✅ Configuration validation passed")
    else:
        print("❌ Configuration validation failed:")
        for issue in validation_result["issues"]:
            print(f"   - {issue}")
    
    if validation_result["warnings"]:
        print("⚠️  Configuration warnings:")
        for warning in validation_result["warnings"]:
            print(f"   - {warning}")
    
    print("\n🎉 MedAssist AI setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure email/SMS settings in .env file (optional)")
    print("2. Run the agent: python agent.py")
    print("3. Start booking appointments and managing your clinic!")
    
    return True


def reset_clinic():
    """Reset the clinic database (use with caution!)"""
    print("⚠️  WARNING: This will delete all clinic data!")
    response = input("Are you sure you want to reset? Type 'yes' to confirm: ")
    
    if response.lower() == 'yes':
        # Remove data files
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
        
        print("✅ Clinic data reset completed")
        return True
    else:
        print("❌ Reset cancelled")
        return False


def show_clinic_status():
    """Show current clinic status and statistics"""
    db = MedicalDatabase()
    
    print("🏥 MedAssist AI Clinic Status")
    print("=" * 40)
    
    # Clinic settings
    settings = db.get_clinic_settings()
    if settings:
        print(f"Clinic Name: {settings.clinic_name}")
        print(f"Phone: {settings.phone}")
        print(f"Email: {settings.email}")
        print(f"Timezone: {settings.timezone}")
    else:
        print("❌ Clinic settings not configured")
    
    # Statistics
    patients = db.get_patients()
    doctors = db.get_doctors()
    appointments = db.get_appointments()
    
    print(f"\n📊 Statistics:")
    print(f"Total Patients: {len(patients)}")
    print(f"Total Doctors: {len(doctors)}")
    print(f"Total Appointments: {len(appointments)}")
    
    # Recent appointments
    if appointments:
        recent_appointments = sorted(appointments, key=lambda x: x.appointment_datetime, reverse=True)[:5]
        print(f"\n📅 Recent Appointments:")
        for appointment in recent_appointments:
            patient = db.get_patient(appointment.patient_id)
            doctor = db.get_doctor(appointment.doctor_id)
            patient_name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown"
            doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Unknown"
            print(f"   - {appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')}: {patient_name} with {doctor_name} ({appointment.status.value})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            setup_clinic()
        elif command == "reset":
            reset_clinic()
        elif command == "status":
            show_clinic_status()
        else:
            print("Usage: python setup_clinic.py [setup|reset|status]")
    else:
        setup_clinic()
