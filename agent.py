"""
Medical Appointment Scheduling AI Agent
Main orchestrator with natural language interface
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.adk.agents import Agent

# Import our custom services (support both package and script execution)
try:
    from .database import MedicalDatabase
    from .scheduling_service import SchedulingService
    from .no_show_predictor import NoShowPredictor
    from .notification_service import NotificationService
    from .insurance_service import InsuranceService
    from .analytics_service import AnalyticsService
    from .models import Patient, Doctor, Appointment, ClinicSettings, AppointmentStatus
except ImportError:
    from database import MedicalDatabase
    from scheduling_service import SchedulingService
    from no_show_predictor import NoShowPredictor
    from notification_service import NotificationService
    from insurance_service import InsuranceService
    from analytics_service import AnalyticsService
    from models import Patient, Doctor, Appointment, ClinicSettings, AppointmentStatus


# Initialize services
db = MedicalDatabase()
scheduling_service = SchedulingService(db)
no_show_predictor = NoShowPredictor(db)
notification_service = NotificationService(db, no_show_predictor)
insurance_service = InsuranceService(db)
analytics_service = AnalyticsService(db, no_show_predictor, insurance_service)


def register_patient(first_name: str, last_name: str, date_of_birth: str, 
                    phone: str, email: str, address: str, emergency_contact: str,
                    insurance_provider: str, insurance_number: str,
                    preferred_communication: str = "phone", notes: str = "") -> dict:
    """Register a new patient in the system.
    
    Args:
        first_name (str): Patient's first name
        last_name (str): Patient's last name
        date_of_birth (str): Patient's date of birth (YYYY-MM-DD format)
        phone (str): Patient's phone number
        email (str): Patient's email address
        address (str): Patient's address
        emergency_contact (str): Emergency contact information
        insurance_provider (str): Insurance provider name
        insurance_number (str): Insurance policy number
        preferred_communication (str): Preferred communication method (phone, email, sms)
        notes (str): Additional notes about the patient
    
    Returns:
        dict: Registration status and patient ID or error message
    """
    try:
        # Parse date of birth
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
        
        patient_id = scheduling_service.register_patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            phone=phone,
            email=email,
            address=address,
            emergency_contact=emergency_contact,
            insurance_provider=insurance_provider,
            insurance_number=insurance_number,
            preferred_communication=preferred_communication,
            notes=notes
        )
        
        return {
            "status": "success",
            "message": f"Patient {first_name} {last_name} registered successfully",
            "patient_id": patient_id
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to register patient: {str(e)}"
        }


def find_patient(phone: str = None, email: str = None, 
                first_name: str = None, last_name: str = None) -> dict:
    """Find patients by various criteria.
    
    Args:
        phone (str, optional): Patient's phone number
        email (str, optional): Patient's email address
        first_name (str, optional): Patient's first name
        last_name (str, optional): Patient's last name
    
    Returns:
        dict: List of matching patients or error message
    """
    try:
        patients = scheduling_service.find_patient(
            phone=phone or None, email=email or None, first_name=first_name or None, last_name=last_name or None
        )
        
        if not patients:
            return {
                "status": "not_found",
                "message": "No patients found matching the criteria"
            }
        
        patient_list = []
        for patient in patients:
            patient_list.append({
                "patient_id": patient.id,
                "name": f"{patient.first_name} {patient.last_name}",
                "phone": patient.phone,
                "email": patient.email,
                "insurance_provider": patient.insurance_provider,
                "status": patient.status.value
            })
        
        return {
            "status": "success",
            "patients": patient_list,
            "count": len(patient_list)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to find patients: {str(e)}"
        }


def get_available_appointments(doctor_id: str, date: str, 
                             appointment_duration: int = 30) -> dict:
    """Get available appointment slots for a doctor on a specific date.
    
    Args:
        doctor_id (str): Doctor's ID
        date (str): Date in YYYY-MM-DD format
        appointment_duration (int): Duration in minutes (default 30)
    
    Returns:
        dict: List of available appointment slots or error message
    """
    try:
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
        available_slots = scheduling_service.get_available_slots(
            doctor_id=doctor_id,
            date=appointment_date,
            appointment_duration=appointment_duration
        )
        
        if not available_slots:
            return {
                "status": "no_slots",
                "message": f"No available slots for doctor {doctor_id} on {date}"
            }
        
        slots_list = []
        for slot in available_slots:
            slots_list.append({
                "datetime": slot.strftime("%Y-%m-%d %H:%M"),
                "time": slot.strftime("%I:%M %p"),
                "date": slot.strftime("%B %d, %Y")
            })
        
        return {
            "status": "success",
            "available_slots": slots_list,
            "count": len(slots_list)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get available appointments: {str(e)}"
        }


def book_appointment(patient_id: str, doctor_id: str, appointment_datetime: str,
                    appointment_type: str = "general", notes: str = "") -> dict:
    """Book a new appointment.
    
    Args:
        patient_id (str): Patient's ID
        doctor_id (str): Doctor's ID
        appointment_datetime (str): Appointment date and time (YYYY-MM-DD HH:MM format)
        appointment_type (str): Type of appointment (default: general)
        notes (str): Additional notes for the appointment
    
    Returns:
        dict: Booking status and appointment ID or error message
    """
    try:
        appointment_dt = datetime.strptime(appointment_datetime, "%Y-%m-%d %H:%M")
        
        appointment_id = scheduling_service.book_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_dt,
            appointment_type=appointment_type,
            notes=notes
        )
        
        # Generate no-show prediction
        prediction = no_show_predictor.predict_no_show_risk(patient_id, appointment_id)
        
        # Verify insurance
        insurance_result = insurance_service.verify_insurance(patient_id, appointment_id)
        
        return {
            "status": "success",
            "message": "Appointment booked successfully",
            "appointment_id": appointment_id,
            "appointment_datetime": appointment_dt.strftime("%Y-%m-%d %H:%M"),
            "no_show_risk": {
                "risk_score": prediction.risk_score,
                "risk_level": "High" if prediction.risk_score > 0.6 else "Medium" if prediction.risk_score > 0.3 else "Low",
                "risk_factors": prediction.risk_factors
            },
            "insurance_status": insurance_result.get("status", "unknown")
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to book appointment: {str(e)}"
        }


def reschedule_appointment(appointment_id: str, new_datetime: str) -> dict:
    """Reschedule an existing appointment.
    
    Args:
        appointment_id (str): ID of the appointment to reschedule
        new_datetime (str): New appointment date and time (YYYY-MM-DD HH:MM format)
    
    Returns:
        dict: Rescheduling status or error message
    """
    try:
        new_dt = datetime.strptime(new_datetime, "%Y-%m-%d %H:%M")
        
        success = scheduling_service.reschedule_appointment(appointment_id, new_dt)
        
        if success:
            return {
                "status": "success",
                "message": "Appointment rescheduled successfully",
                "new_datetime": new_dt.strftime("%Y-%m-%d %H:%M")
            }
        else:
            return {
                "status": "error",
                "error_message": "Failed to reschedule appointment - slot may not be available"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to reschedule appointment: {str(e)}"
        }


def cancel_appointment(appointment_id: str, reason: str = "") -> dict:
    """Cancel an appointment.
    
    Args:
        appointment_id (str): ID of the appointment to cancel
        reason (str): Reason for cancellation
    
    Returns:
        dict: Cancellation status or error message
    """
    try:
        success = scheduling_service.cancel_appointment(appointment_id, reason)
        
        if success:
            # Send cancellation notification
            notification_service.send_appointment_cancellation(appointment_id, reason)
            
            return {
                "status": "success",
                "message": "Appointment cancelled successfully"
            }
        else:
            return {
                "status": "error",
                "error_message": "Failed to cancel appointment"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to cancel appointment: {str(e)}"
        }


def send_reminders() -> dict:
    """Send automated reminders for upcoming appointments.
    
    Returns:
        dict: Reminder processing results
    """
    try:
        results = notification_service.process_scheduled_reminders()
        
        return {
            "status": "success",
            "message": "Reminder processing completed",
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to process reminders: {str(e)}"
        }


def get_clinic_analytics(start_date: str, end_date: str) -> dict:
    """Get comprehensive clinic analytics for a date range.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        dict: Clinic analytics data or error message
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        dashboard_data = analytics_service.generate_clinic_dashboard(start_dt, end_dt)
        
        return {
            "status": "success",
            "analytics": dashboard_data,
            "period": f"{start_date} to {end_date}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get analytics: {str(e)}"
        }


def get_patient_appointments(patient_id: str, upcoming_only: bool = True) -> dict:
    """Get appointments for a specific patient.
    
    Args:
        patient_id (str): Patient's ID
        upcoming_only (bool): Whether to show only upcoming appointments
    
    Returns:
        dict: List of patient appointments or error message
    """
    try:
        appointments = scheduling_service.get_patient_appointments(patient_id, upcoming_only)
        
        appointment_list = []
        for appointment in appointments:
            doctor = db.get_doctor(appointment.doctor_id)
            appointment_list.append({
                "appointment_id": appointment.id,
                "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Unknown",
                "appointment_datetime": appointment.appointment_datetime.strftime("%Y-%m-%d %H:%M"),
                "status": appointment.status.value,
                "appointment_type": appointment.appointment_type,
                "notes": appointment.notes
            })
        
        return {
            "status": "success",
            "appointments": appointment_list,
            "count": len(appointment_list)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get patient appointments: {str(e)}"
        }


def verify_insurance(patient_id: str, appointment_id: str) -> dict:
    """Verify patient's insurance coverage.
    
    Args:
        patient_id (str): Patient's ID
        appointment_id (str): Appointment ID
    
    Returns:
        dict: Insurance verification results
    """
    try:
        result = insurance_service.verify_insurance(patient_id, appointment_id)
        
        return {
            "status": "success",
            "verification_result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to verify insurance: {str(e)}"
        }


def get_no_show_predictions() -> dict:
    """Get high-risk appointments that may result in no-shows.
    
    Returns:
        dict: List of high-risk appointments with predictions
    """
    try:
        high_risk_appointments = no_show_predictor.get_high_risk_appointments()
        
        predictions_list = []
        for appointment, prediction in high_risk_appointments:
            patient = db.get_patient(appointment.patient_id)
            doctor = db.get_doctor(appointment.doctor_id)
            
            predictions_list.append({
                "appointment_id": appointment.id,
                "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
                "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Unknown",
                "appointment_datetime": appointment.appointment_datetime.strftime("%Y-%m-%d %H:%M"),
                "risk_score": prediction.risk_score,
                "risk_level": "High" if prediction.risk_score > 0.6 else "Medium" if prediction.risk_score > 0.3 else "Low",
                "risk_factors": prediction.risk_factors,
                "recommendations": no_show_predictor.get_risk_mitigation_recommendations(prediction)
            })
        
        return {
            "status": "success",
            "high_risk_appointments": predictions_list,
            "count": len(predictions_list)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get no-show predictions: {str(e)}"
        }


# Create the main AI agent
medassist_agent = Agent(
    name="medassist_ai_agent",
    model="gemini-2.0-flash",
    description=(
        "AI-powered medical appointment scheduling agent that automates patient booking, "
        "reduces no-shows, and streamlines clinic operations. Handles patient registration, "
        "appointment scheduling, insurance verification, automated reminders, and analytics."
    ),
    instruction=(
        "You are MedAssist AI, a comprehensive medical appointment scheduling assistant. "
        "You help medical practices manage appointments, reduce no-shows, and improve operations. "
        "You can register patients, book appointments, send reminders, verify insurance, "
        "predict no-shows, and provide analytics. Always be helpful, professional, and "
        "provide clear information about appointment status, insurance coverage, and "
        "any recommendations to improve patient care and clinic efficiency."
    ),
    tools=[
        register_patient,
        find_patient,
        get_available_appointments,
        book_appointment,
        reschedule_appointment,
        cancel_appointment,
        send_reminders,
        get_clinic_analytics,
        get_patient_appointments,
        verify_insurance,
        get_no_show_predictions
    ],
)
