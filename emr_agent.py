"""
EMR (Electronic Medical Records) Agent for the Medical Appointment Scheduling AI Agent
Built with Agent Development Kit for Indian timezone and complete functionality
"""
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from google.adk.agents import Agent
from sqlite_database import SQLiteMedicalDatabase


# Initialize SQLite database
db = SQLiteMedicalDatabase()


def search_emr_by_name(patient_name: str) -> dict:
    """Search EMR by patient name.
    
    Args:
        patient_name (str): The name of the patient to search for
    
    Returns:
        dict: Search results in JSON format with patient information
    """
    try:
        patients = db.search_patients(name=patient_name)
        
        if not patients:
            return {
                "status": "not_found",
                "message": f"No patients found with name containing '{patient_name}'",
                "results": []
            }
        
        # Format results for JSON output
        results = []
        for patient in patients:
            result = {
                "patient_id": patient['patient_id'],
                "name": patient['name'],
                "last_visit_date": patient['last_visit_date'],
                "visits_count": patient['visits_count'],
                "patient_type": patient['patient_type'],
                "is_new_patient": patient['visits_count'] == 1,
                "is_returning_patient": patient['visits_count'] > 1
            }
            results.append(result)
        
        return {
            "status": "success",
            "message": f"Found {len(results)} patient(s) matching '{patient_name}'",
            "results": results,
            "total_count": len(results)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to search EMR: {str(e)}",
            "results": []
        }


def search_emr_by_id(patient_id: int) -> dict:
    """Search EMR by patient ID.
    
    Args:
        patient_id (int): The ID of the patient to search for
    
    Returns:
        dict: Patient information in JSON format
    """
    try:
        patient = db.get_patient_by_id(patient_id)
        
        if not patient:
            return {
                "status": "not_found",
                "message": f"No patient found with ID {patient_id}",
                "result": None
            }
        
        # Format result for JSON output
        result = {
            "patient_id": patient['patient_id'],
            "name": patient['name'],
            "last_visit_date": patient['last_visit_date'],
            "visits_count": patient['visits_count'],
            "patient_type": patient['patient_type'],
            "is_new_patient": patient['visits_count'] == 1,
            "is_returning_patient": patient['visits_count'] > 1
        }
        
        return {
            "status": "success",
            "message": f"Found patient with ID {patient_id}",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to search EMR: {str(e)}",
            "result": None
        }


def get_patient_statistics() -> dict:
    """Get comprehensive patient statistics.
    
    Returns:
        dict: Patient statistics in JSON format
    """
    try:
        stats = db.get_patient_statistics()
        
        return {
            "status": "success",
            "message": "Patient statistics retrieved successfully",
            "statistics": {
                "total_patients": stats['total_patients'],
                "new_patients": stats['new_patients'],
                "returning_patients": stats['returning_patients'],
                "average_visits": stats['average_visits'],
                "new_patient_percentage": round((stats['new_patients'] / stats['total_patients'] * 100), 2) if stats['total_patients'] > 0 else 0,
                "returning_patient_percentage": round((stats['returning_patients'] / stats['total_patients'] * 100), 2) if stats['total_patients'] > 0 else 0
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get patient statistics: {str(e)}",
            "statistics": None
        }


def add_new_patient(name: str, last_visit_date: str = None) -> dict:
    """Add a new patient to the EMR system.
    
    Args:
        name (str): Full name of the patient
        last_visit_date (str, optional): Last visit date in YYYY-MM-DD format
    
    Returns:
        dict: Result of adding the patient
    """
    try:
        visit_date = None
        if last_visit_date:
            visit_date = datetime.strptime(last_visit_date, "%Y-%m-%d").date()
        
        patient_id = db.add_patient(name, visit_date, 1)
        
        return {
            "status": "success",
            "message": f"New patient '{name}' added successfully",
            "patient_id": patient_id,
            "patient_type": "new"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to add patient: {str(e)}"
        }


def update_patient_visit(patient_id: int) -> dict:
    """Update patient's visit count and last visit date.
    
    Args:
        patient_id (int): ID of the patient to update
    
    Returns:
        dict: Result of the update
    """
    try:
        patient = db.get_patient_by_id(patient_id)
        if not patient:
            return {
                "status": "not_found",
                "message": f"Patient with ID {patient_id} not found"
            }
        
        db.update_patient_visit(patient_id)
        
        # Get updated patient info
        updated_patient = db.get_patient_by_id(patient_id)
        
        return {
            "status": "success",
            "message": f"Visit updated for patient '{updated_patient['name']}'",
            "patient_id": patient_id,
            "new_visits_count": updated_patient['visits_count'],
            "last_visit_date": updated_patient['last_visit_date'],
            "patient_type": updated_patient['patient_type']
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to update patient visit: {str(e)}"
        }


def get_all_patients() -> dict:
    """Get all patients in the EMR system.
    
    Returns:
        dict: All patients in JSON format
    """
    try:
        patients = db.get_all_patients()
        
        results = []
        for patient in patients:
            result = {
                "patient_id": patient['patient_id'],
                "name": patient['name'],
                "last_visit_date": patient['last_visit_date'],
                "visits_count": patient['visits_count'],
                "patient_type": patient['patient_type'],
                "is_new_patient": patient['visits_count'] == 1,
                "is_returning_patient": patient['visits_count'] > 1
            }
            results.append(result)
        
        return {
            "status": "success",
            "message": f"Retrieved {len(results)} patients",
            "results": results,
            "total_count": len(results)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get all patients: {str(e)}",
            "results": []
        }


def book_appointment(patient_id: int, doctor_id: str, appointment_datetime: str, 
                    appointment_type: str = "general", notes: str = "") -> dict:
    """Book an appointment for a patient.
    
    Args:
        patient_id (int): ID of the patient
        doctor_id (str): ID of the doctor
        appointment_datetime (str): Appointment date and time in YYYY-MM-DD HH:MM format
        appointment_type (str): Type of appointment
        notes (str): Additional notes
    
    Returns:
        dict: Result of booking the appointment
    """
    try:
        # Verify patient exists
        patient = db.get_patient_by_id(patient_id)
        if not patient:
            return {
                "status": "error",
                "message": f"Patient with ID {patient_id} not found"
            }
        
        # Parse appointment datetime
        appointment_dt = datetime.strptime(appointment_datetime, "%Y-%m-%d %H:%M")
        
        # Book the appointment
        appointment_id = db.add_appointment(
            patient_id, doctor_id, appointment_dt, appointment_type, notes
        )
        
        return {
            "status": "success",
            "message": "Appointment booked successfully",
            "appointment_id": appointment_id,
            "patient_name": patient['name'],
            "appointment_datetime": appointment_datetime,
            "appointment_type": appointment_type
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to book appointment: {str(e)}"
        }


def get_patient_appointments(patient_id: int) -> dict:
    """Get all appointments for a specific patient.
    
    Args:
        patient_id (int): ID of the patient
    
    Returns:
        dict: Patient appointments in JSON format
    """
    try:
        appointments = db.get_appointments(patient_id=patient_id)
        
        if not appointments:
            return {
                "status": "no_appointments",
                "message": f"No appointments found for patient ID {patient_id}",
                "appointments": []
            }
        
        return {
            "status": "success",
            "message": f"Found {len(appointments)} appointment(s) for patient ID {patient_id}",
            "appointments": appointments,
            "total_count": len(appointments)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to get patient appointments: {str(e)}",
            "appointments": []
        }


def initialize_database() -> dict:
    """Initialize the database with synthetic patient data.
    
    Returns:
        dict: Result of database initialization
    """
    try:
        db.generate_synthetic_patients(50)
        
        # Add sample doctors
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
        
        return {
            "status": "success",
            "message": "Database initialized successfully with 50 synthetic patients and sample data"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to initialize database: {str(e)}"
        }


# Create the EMR AI agent
emr_agent = Agent(
    name="emr_medical_agent",
    model="gemini-2.0-flash",
    description=(
        "AI-powered Electronic Medical Records (EMR) system for Indian medical clinics. "
        "Provides patient search, appointment scheduling, and medical record management "
        "with support for Indian timezone (Asia/Kolkata) and comprehensive patient tracking."
    ),
    instruction=(
        "You are an EMR (Electronic Medical Records) AI assistant for Indian medical clinics. "
        "You help healthcare professionals search patient records, manage appointments, and "
        "track patient visits. You can search patients by name or ID, identify new vs returning "
        "patients, book appointments, and provide comprehensive patient statistics. "
        "All operations are optimized for Indian timezone (Asia/Kolkata) and return results "
        "in JSON format for easy integration. Always be professional, accurate, and helpful "
        "in managing patient medical records."
    ),
    tools=[
        search_emr_by_name,
        search_emr_by_id,
        get_patient_statistics,
        add_new_patient,
        update_patient_visit,
        get_all_patients,
        book_appointment,
        get_patient_appointments,
        initialize_database
    ],
)
