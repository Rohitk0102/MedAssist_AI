"""
Simple demo script for the Medical Appointment Scheduling AI Agent
"""
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import MedicalDatabase
from scheduling_service import SchedulingService
from no_show_predictor import NoShowPredictor
from notification_service import NotificationService
from insurance_service import InsuranceService
from analytics_service import AnalyticsService
from models import Doctor, Patient, Appointment, ClinicSettings


def simple_demo():
    """Run a simple demo of MedAssist AI capabilities"""
    print("🏥 MedAssist AI - Simple Demo")
    print("=" * 40)
    
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
    
    # Add a sample doctor
    print("\n👨‍⚕️ Adding sample doctor...")
    doctor = Doctor(
        id="demo_doc",
        first_name="Demo",
        last_name="Doctor",
        specialty="General Practice",
        phone="(555) 123-4568",
        email="demo@doctor.com",
        working_hours={
            "monday": {"start": "09:00", "end": "17:00"},
            "tuesday": {"start": "09:00", "end": "17:00"},
            "wednesday": {"start": "09:00", "end": "17:00"},
            "thursday": {"start": "09:00", "end": "17:00"},
            "friday": {"start": "09:00", "end": "17:00"}
        }
    )
    db.add_doctor(doctor)
    print(f"✅ Added: Dr. {doctor.first_name} {doctor.last_name} ({doctor.specialty})")
    
    # Register a sample patient
    print("\n👥 Registering sample patient...")
    patient_id = scheduling_service.register_patient(
        first_name="Demo",
        last_name="Patient",
        date_of_birth=datetime(1990, 1, 1),
        phone="555-0001",
        email="demo@patient.com",
        address="123 Patient St, City, State 12345",
        emergency_contact="Emergency (555-0002)",
        insurance_provider="Demo Insurance",
        insurance_number="DEMO123456"
    )
    print(f"✅ Registered: Demo Patient (ID: {patient_id})")
    
    # Find next available appointment slot
    print("\n📅 Finding available appointment slot...")
    current_date = datetime.now()
    appointment_slot = None
    
    for days_ahead in range(1, 8):  # Check next 7 days
        test_date = current_date + timedelta(days=days_ahead)
        day_name = test_date.strftime('%A').lower()
        if day_name in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            available_slots = scheduling_service.get_available_slots("demo_doc", test_date)
            if available_slots:
                appointment_slot = available_slots[0]
                print(f"✅ Found available slot: {appointment_slot.strftime('%Y-%m-%d %H:%M')}")
                break
    
    if not appointment_slot:
        print("❌ No available appointment slots found")
        return
    
    # Book the appointment
    print("\n📅 Booking appointment...")
    appointment_id = scheduling_service.book_appointment(
        patient_id=patient_id,
        doctor_id="demo_doc",
        appointment_datetime=appointment_slot,
        appointment_type="general",
        notes="Demo appointment"
    )
    print(f"✅ Appointment booked successfully! ID: {appointment_id}")
    
    # Demonstrate no-show prediction
    print("\n🔮 Demonstrating no-show prediction...")
    prediction = no_show_predictor.predict_no_show_risk(patient_id, appointment_id)
    risk_level = "High" if prediction.risk_score > 0.6 else "Medium" if prediction.risk_score > 0.3 else "Low"
    print(f"📊 No-show risk: {risk_level} ({prediction.risk_score:.2f})")
    if prediction.risk_factors:
        print(f"   Risk factors: {', '.join(prediction.risk_factors)}")
    
    # Demonstrate insurance verification
    print("\n💳 Demonstrating insurance verification...")
    verification_result = insurance_service.verify_insurance(patient_id, appointment_id)
    print(f"🏥 Insurance status: {verification_result['status']}")
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
    
    # Summary
    print("\n🎉 Simple demo completed successfully!")
    print("\n📋 MedAssist AI capabilities demonstrated:")
    print("✅ Patient registration and management")
    print("✅ Doctor scheduling and availability")
    print("✅ Appointment booking and management")
    print("✅ No-show prediction and risk assessment")
    print("✅ Insurance verification and coverage")
    print("✅ Automated notifications and reminders")
    print("✅ Comprehensive analytics and reporting")
    
    print(f"\n💡 This demo shows how MedAssist AI can help medical practices:")
    print("   - Reduce no-shows through predictive intervention")
    print("   - Improve revenue through better insurance collection")
    print("   - Streamline operations with automated workflows")
    print("   - Gain insights through comprehensive analytics")
    
    return True


if __name__ == "__main__":
    simple_demo()
