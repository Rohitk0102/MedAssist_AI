"""
Demo script for the Medical Appointment Scheduling AI Agent
This script demonstrates the key features and capabilities of MedAssist AI
"""
import sys
from datetime import datetime, timedelta
from database import MedicalDatabase
from scheduling_service import SchedulingService
from no_show_predictor import NoShowPredictor
from notification_service import NotificationService
from insurance_service import InsuranceService
from analytics_service import AnalyticsService
from models import Doctor, Patient, Appointment, ClinicSettings


def run_demo():
    """Run a comprehensive demo of MedAssist AI capabilities"""
    print("🏥 MedAssist AI - Medical Appointment Scheduling Demo")
    print("=" * 60)
    
    # Initialize services
    print("\n📋 Initializing services...")
    db = MedicalDatabase()
    scheduling_service = SchedulingService(db)
    no_show_predictor = NoShowPredictor(db)
    notification_service = NotificationService(db, no_show_predictor)
    insurance_service = InsuranceService(db)
    analytics_service = AnalyticsService(db, no_show_predictor, insurance_service)
    
    # Setup clinic settings
    clinic_settings = ClinicSettings(
        clinic_name="MedAssist Demo Clinic",
        address="123 Demo Street, Healthcare City, HC 12345",
        phone="(555) 123-4567",
        email="demo@medassist.com"
    )
    db.update_clinic_settings(clinic_settings)
    print("✅ Clinic settings configured")
    
    # Add sample doctors
    print("\n👨‍⚕️ Adding sample doctors...")
    doctors = [
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
                "friday": {"start": "09:00", "end": "15:00"}
            }
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
                "friday": {"start": "08:00", "end": "14:00"}
            }
        )
    ]
    
    for doctor in doctors:
        if db.add_doctor(doctor):
            print(f"✅ Added: Dr. {doctor.first_name} {doctor.last_name} ({doctor.specialty})")
        else:
            print(f"⚠️  Doctor already exists: Dr. {doctor.first_name} {doctor.last_name}")
    
    # Register sample patients
    print("\n👥 Registering sample patients...")
    patients_data = [
        {
            "first_name": "John",
            "last_name": "Smith",
            "date_of_birth": datetime(1985, 3, 15),
            "phone": "555-1234",
            "email": "john.smith@email.com",
            "address": "123 Main St, City, State 12345",
            "emergency_contact": "Jane Smith (555-5678)",
            "insurance_provider": "Blue Cross",
            "insurance_number": "BC123456789",
            "preferred_communication": "phone"
        },
        {
            "first_name": "Maria",
            "last_name": "Garcia",
            "date_of_birth": datetime(1990, 7, 22),
            "phone": "555-2345",
            "email": "maria.garcia@email.com",
            "address": "456 Oak Ave, City, State 12345",
            "emergency_contact": "Carlos Garcia (555-6789)",
            "insurance_provider": "Aetna",
            "insurance_number": "AET987654321",
            "preferred_communication": "email"
        },
        {
            "first_name": "Robert",
            "last_name": "Johnson",
            "date_of_birth": datetime(1978, 11, 8),
            "phone": "555-3456",
            "email": "robert.johnson@email.com",
            "address": "789 Pine St, City, State 12345",
            "emergency_contact": "Linda Johnson (555-7890)",
            "insurance_provider": "Medicare",
            "insurance_number": "123-45-6789",
            "preferred_communication": "sms"
        }
    ]
    
    patient_ids = []
    for patient_data in patients_data:
        patient_id = scheduling_service.register_patient(**patient_data)
        patient_ids.append(patient_id)
        print(f"✅ Registered: {patient_data['first_name']} {patient_data['last_name']}")
    
    # Book sample appointments - find next available weekdays
    print("\n📅 Booking sample appointments...")
    
    # Find next available weekday for each doctor
    current_date = datetime.now()
    appointment_times = []
    
    for days_ahead in range(1, 8):  # Check next 7 days
        test_date = current_date + timedelta(days=days_ahead)
        day_name = test_date.strftime('%A').lower()
        if day_name in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:  # Weekdays only
            appointment_times.append(test_date)
            if len(appointment_times) >= 3:  # We need 3 appointments
                break
    
    appointments_data = [
        {
            "patient_id": patient_ids[0],
            "doctor_id": "doc_001",
            "appointment_datetime": appointment_times[0].replace(hour=10, minute=0),
            "appointment_type": "general",
            "notes": "Annual checkup"
        },
        {
            "patient_id": patient_ids[1],
            "doctor_id": "doc_002",
            "appointment_datetime": appointment_times[0].replace(hour=14, minute=0),  # Same day, different doctor
            "appointment_type": "consultation",
            "notes": "Heart health consultation"
        },
        {
            "patient_id": patient_ids[2],
            "doctor_id": "doc_001",
            "appointment_datetime": appointment_times[1].replace(hour=9, minute=30),  # Different day
            "appointment_type": "follow_up",
            "notes": "Follow-up appointment"
        }
    ]
    
    appointment_ids = []
    for i, appointment_data in enumerate(appointments_data):
        # Create a copy to avoid modifying the original
        appointment_copy = appointment_data.copy()
        
        # Get available slots for the doctor on the requested date
        doctor_id = appointment_copy["doctor_id"]
        requested_date = appointment_copy["appointment_datetime"].date()
        available_slots = scheduling_service.get_available_slots(doctor_id, requested_date)
        
        if available_slots:
            # Use the first available slot
            appointment_copy["appointment_datetime"] = available_slots[0]
            appointment_id = scheduling_service.book_appointment(**appointment_copy)
            appointment_ids.append(appointment_id)
            patient = db.get_patient(appointment_copy["patient_id"])
            doctor = db.get_doctor(appointment_copy["doctor_id"])
            print(f"✅ Booked: {patient.first_name} {patient.last_name} with Dr. {doctor.last_name}")
        else:
            # Try next available date
            for days_ahead in range(1, 8):
                test_date = requested_date + timedelta(days=days_ahead)
                day_name = test_date.strftime('%A').lower()
                if day_name in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                    available_slots = scheduling_service.get_available_slots(doctor_id, test_date)
                    if available_slots:
                        appointment_copy["appointment_datetime"] = available_slots[0]
                        appointment_id = scheduling_service.book_appointment(**appointment_copy)
                        appointment_ids.append(appointment_id)
                        patient = db.get_patient(appointment_copy["patient_id"])
                        doctor = db.get_doctor(appointment_copy["doctor_id"])
                        print(f"✅ Booked: {patient.first_name} {patient.last_name} with Dr. {doctor.last_name}")
                        break
            else:
                print(f"⚠️  No available slots for doctor {doctor_id} in next 7 days")
    
    # Demonstrate no-show prediction
    print("\n🔮 Demonstrating no-show prediction...")
    for i, appointment_id in enumerate(appointment_ids):
        patient_id = appointments_data[i]["patient_id"]
        prediction = no_show_predictor.predict_no_show_risk(patient_id, appointment_id)
        
        patient = db.get_patient(patient_id)
        risk_level = "High" if prediction.risk_score > 0.6 else "Medium" if prediction.risk_score > 0.3 else "Low"
        
        print(f"📊 {patient.first_name} {patient.last_name}: {risk_level} risk ({prediction.risk_score:.2f})")
        if prediction.risk_factors:
            print(f"   Risk factors: {', '.join(prediction.risk_factors)}")
    
    # Demonstrate insurance verification
    print("\n💳 Demonstrating insurance verification...")
    for i, appointment_id in enumerate(appointment_ids):
        patient_id = appointments_data[i]["patient_id"]
        verification_result = insurance_service.verify_insurance(patient_id, appointment_id)
        
        patient = db.get_patient(patient_id)
        print(f"🏥 {patient.first_name} {patient.last_name}: {verification_result['status']}")
        if verification_result['status'] == 'verified':
            coverage_info = verification_result.get('coverage_info', {})
            print(f"   Copay: ${coverage_info.get('copay', 0)}")
            print(f"   Deductible: ${coverage_info.get('deductible', 0)}")
    
    # Demonstrate notification system
    print("\n📱 Demonstrating notification system...")
    results = notification_service.process_scheduled_reminders()
    print(f"✅ Reminders sent: {results['reminders_sent']}")
    print(f"✅ Confirmations sent: {results['confirmations_sent']}")
    print(f"⚠️  High-risk appointments: {results['high_risk_appointments']}")
    
    # Demonstrate analytics
    print("\n📈 Demonstrating analytics...")
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now() + timedelta(days=30)
    
    dashboard_data = analytics_service.generate_clinic_dashboard(start_date, end_date)
    
    appointment_stats = dashboard_data['appointment_statistics']
    print(f"📊 Total appointments: {appointment_stats['total_appointments']}")
    print(f"📊 Completion rate: {appointment_stats['completion_rate']}%")
    print(f"📊 No-show rate: {appointment_stats['no_show_rate']}%")
    
    revenue_analytics = dashboard_data['revenue_analytics']
    print(f"💰 Actual revenue: ${revenue_analytics['actual_revenue']:.2f}")
    print(f"💰 Potential revenue: ${revenue_analytics['potential_revenue']:.2f}")
    print(f"💰 Revenue efficiency: {revenue_analytics['revenue_efficiency']:.1f}%")
    
    # Demonstrate high-risk patient identification
    print("\n⚠️  High-risk patients identified:")
    high_risk_appointments = no_show_predictor.get_high_risk_appointments()
    for appointment, prediction in high_risk_appointments:
        patient = db.get_patient(appointment.patient_id)
        doctor = db.get_doctor(appointment.doctor_id)
        print(f"🚨 {patient.first_name} {patient.last_name} with Dr. {doctor.last_name}")
        print(f"   Risk score: {prediction.risk_score:.2f}")
        print(f"   Appointment: {appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')}")
    
    # Demonstrate available slots
    print("\n🕐 Demonstrating available appointment slots...")
    available_slots = scheduling_service.get_available_slots("doc_001", tomorrow)
    print(f"📅 Available slots for Dr. Johnson tomorrow: {len(available_slots)}")
    for slot in available_slots[:5]:  # Show first 5 slots
        print(f"   - {slot.strftime('%H:%M')}")
    
    # Summary
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Summary of MedAssist AI capabilities demonstrated:")
    print("✅ Patient registration and management")
    print("✅ Doctor scheduling and availability")
    print("✅ Appointment booking and management")
    print("✅ No-show prediction and risk assessment")
    print("✅ Insurance verification and coverage")
    print("✅ Automated notifications and reminders")
    print("✅ Comprehensive analytics and reporting")
    print("✅ High-risk patient identification")
    print("✅ Revenue optimization insights")
    
    print(f"\n💡 This demo shows how MedAssist AI can help medical practices:")
    print("   - Reduce no-shows through predictive intervention")
    print("   - Improve revenue through better insurance collection")
    print("   - Streamline operations with automated workflows")
    print("   - Gain insights through comprehensive analytics")
    
    return True


def interactive_demo():
    """Run an interactive demo where users can try different features"""
    print("🎮 MedAssist AI - Interactive Demo")
    print("=" * 40)
    
    # Initialize services
    db = MedicalDatabase()
    scheduling_service = SchedulingService(db)
    
    while True:
        print("\nWhat would you like to try?")
        print("1. Register a new patient")
        print("2. Find a patient")
        print("3. Check available appointments")
        print("4. Book an appointment")
        print("5. View clinic analytics")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            register_patient_interactive(scheduling_service)
        elif choice == "2":
            find_patient_interactive(scheduling_service)
        elif choice == "3":
            check_availability_interactive(scheduling_service)
        elif choice == "4":
            book_appointment_interactive(scheduling_service)
        elif choice == "5":
            view_analytics_interactive()
        elif choice == "6":
            print("👋 Thanks for trying MedAssist AI!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


def register_patient_interactive(scheduling_service):
    """Interactive patient registration"""
    print("\n👤 Register New Patient")
    print("-" * 25)
    
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    phone = input("Phone number: ").strip()
    email = input("Email: ").strip()
    insurance_provider = input("Insurance provider: ").strip()
    insurance_number = input("Insurance number: ").strip()
    
    try:
        patient_id = scheduling_service.register_patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime(1990, 1, 1),  # Default DOB for demo
            phone=phone,
            email=email,
            address="123 Demo St, City, State 12345",  # Default address
            emergency_contact="Emergency Contact (555-0000)",  # Default
            insurance_provider=insurance_provider,
            insurance_number=insurance_number
        )
        print(f"✅ Patient registered successfully! ID: {patient_id}")
    except Exception as e:
        print(f"❌ Error: {e}")


def find_patient_interactive(scheduling_service):
    """Interactive patient search"""
    print("\n🔍 Find Patient")
    print("-" * 15)
    
    search_type = input("Search by (1) phone, (2) email, (3) name: ").strip()
    
    if search_type == "1":
        phone = input("Phone number: ").strip()
        patients = scheduling_service.find_patient(phone=phone)
    elif search_type == "2":
        email = input("Email: ").strip()
        patients = scheduling_service.find_patient(email=email)
    elif search_type == "3":
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        patients = scheduling_service.find_patient(first_name=first_name, last_name=last_name)
    else:
        print("❌ Invalid search type")
        return
    
    if patients:
        print(f"\n✅ Found {len(patients)} patient(s):")
        for patient in patients:
            print(f"   - {patient.first_name} {patient.last_name} (ID: {patient.id})")
            print(f"     Phone: {patient.phone}, Email: {patient.email}")
    else:
        print("❌ No patients found")


def check_availability_interactive(scheduling_service):
    """Interactive availability check"""
    print("\n🕐 Check Available Appointments")
    print("-" * 30)
    
    # Show available doctors
    db = MedicalDatabase()
    doctors = db.get_doctors()
    print("Available doctors:")
    for i, doctor in enumerate(doctors):
        print(f"{i+1}. Dr. {doctor.first_name} {doctor.last_name} ({doctor.specialty})")
    
    try:
        doctor_choice = int(input("Select doctor (number): ")) - 1
        if 0 <= doctor_choice < len(doctors):
            doctor = doctors[doctor_choice]
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            date = datetime.strptime(date_str, "%Y-%m-%d")
            
            available_slots = scheduling_service.get_available_slots(doctor.id, date)
            
            if available_slots:
                print(f"\n✅ Available slots for Dr. {doctor.last_name} on {date_str}:")
                for slot in available_slots:
                    print(f"   - {slot.strftime('%H:%M')}")
            else:
                print(f"❌ No available slots for Dr. {doctor.last_name} on {date_str}")
        else:
            print("❌ Invalid doctor selection")
    except ValueError:
        print("❌ Invalid input")


def book_appointment_interactive(scheduling_service):
    """Interactive appointment booking"""
    print("\n📅 Book Appointment")
    print("-" * 18)
    
    # Find patient
    phone = input("Patient phone number: ").strip()
    patients = scheduling_service.find_patient(phone=phone)
    
    if not patients:
        print("❌ Patient not found")
        return
    
    patient = patients[0]
    print(f"✅ Found patient: {patient.first_name} {patient.last_name}")
    
    # Select doctor
    db = MedicalDatabase()
    doctors = db.get_doctors()
    print("\nAvailable doctors:")
    for i, doctor in enumerate(doctors):
        print(f"{i+1}. Dr. {doctor.first_name} {doctor.last_name} ({doctor.specialty})")
    
    try:
        doctor_choice = int(input("Select doctor (number): ")) - 1
        if 0 <= doctor_choice < len(doctors):
            doctor = doctors[doctor_choice]
            
            # Get available slots
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            date = datetime.strptime(date_str, "%Y-%m-%d")
            available_slots = scheduling_service.get_available_slots(doctor.id, date)
            
            if available_slots:
                print(f"\nAvailable slots:")
                for i, slot in enumerate(available_slots[:10]):  # Show first 10
                    print(f"{i+1}. {slot.strftime('%H:%M')}")
                
                slot_choice = int(input("Select time slot (number): ")) - 1
                if 0 <= slot_choice < len(available_slots):
                    selected_slot = available_slots[slot_choice]
                    
                    appointment_type = input("Appointment type (general/consultation/follow_up): ").strip() or "general"
                    notes = input("Notes (optional): ").strip()
                    
                    try:
                        appointment_id = scheduling_service.book_appointment(
                            patient_id=patient.id,
                            doctor_id=doctor.id,
                            appointment_datetime=selected_slot,
                            appointment_type=appointment_type,
                            notes=notes
                        )
                        print(f"✅ Appointment booked successfully! ID: {appointment_id}")
                        print(f"   Date: {selected_slot.strftime('%Y-%m-%d %H:%M')}")
                        print(f"   Doctor: Dr. {doctor.last_name}")
                        print(f"   Patient: {patient.first_name} {patient.last_name}")
                    except Exception as e:
                        print(f"❌ Error booking appointment: {e}")
                else:
                    print("❌ Invalid slot selection")
            else:
                print(f"❌ No available slots for Dr. {doctor.last_name} on {date_str}")
        else:
            print("❌ Invalid doctor selection")
    except ValueError:
        print("❌ Invalid input")


def view_analytics_interactive():
    """Interactive analytics viewing"""
    print("\n📈 Clinic Analytics")
    print("-" * 18)
    
    try:
        start_date_str = input("Start date (YYYY-MM-DD) or press Enter for last 30 days: ").strip()
        end_date_str = input("End date (YYYY-MM-DD) or press Enter for today: ").strip()
        
        if not start_date_str:
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        if not end_date_str:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        # Initialize analytics service
        db = MedicalDatabase()
        no_show_predictor = NoShowPredictor(db)
        insurance_service = InsuranceService(db)
        analytics_service = AnalyticsService(db, no_show_predictor, insurance_service)
        
        dashboard_data = analytics_service.generate_clinic_dashboard(start_date, end_date)
        
        print(f"\n📊 Analytics for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print("-" * 50)
        
        # Appointment statistics
        appointment_stats = dashboard_data['appointment_statistics']
        print(f"Total Appointments: {appointment_stats['total_appointments']}")
        print(f"Completion Rate: {appointment_stats['completion_rate']}%")
        print(f"No-Show Rate: {appointment_stats['no_show_rate']}%")
        print(f"Cancellation Rate: {appointment_stats['cancellation_rate']}%")
        
        # Revenue analytics
        revenue_analytics = dashboard_data['revenue_analytics']
        print(f"\n💰 Revenue Analytics:")
        print(f"Actual Revenue: ${revenue_analytics['actual_revenue']:.2f}")
        print(f"Potential Revenue: ${revenue_analytics['potential_revenue']:.2f}")
        print(f"Lost Revenue (No-shows): ${revenue_analytics['lost_revenue_no_shows']:.2f}")
        print(f"Revenue Efficiency: {revenue_analytics['revenue_efficiency']:.1f}%")
        
        # Patient analytics
        patient_analytics = dashboard_data['patient_analytics']
        print(f"\n👥 Patient Analytics:")
        print(f"Total Patients: {patient_analytics['total_patients']}")
        print(f"Active Patients: {patient_analytics['active_patients']}")
        print(f"High-Risk Patients: {patient_analytics['high_risk_patients']}")
        
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        run_demo()
