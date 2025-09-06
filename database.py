"""
Database management for the Medical Appointment Scheduling AI Agent
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from models import (
    Patient, Doctor, Appointment, NoShowPrediction, ClinicSettings,
    AppointmentStatus, PatientStatus, InsuranceStatus
)


class MedicalDatabase:
    """Simple file-based database for the medical appointment system"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.patients_file = os.path.join(data_dir, "patients.json")
        self.doctors_file = os.path.join(data_dir, "doctors.json")
        self.appointments_file = os.path.join(data_dir, "appointments.json")
        self.predictions_file = os.path.join(data_dir, "no_show_predictions.json")
        self.settings_file = os.path.join(data_dir, "clinic_settings.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize empty files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize empty JSON files if they don't exist"""
        files = [
            self.patients_file,
            self.doctors_file,
            self.appointments_file,
            self.predictions_file,
            self.settings_file
        ]
        
        for file_path in files:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def _load_json(self, file_path: str) -> List[Dict]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_json(self, file_path: str, data: List[Dict]):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Patient Management
    def add_patient(self, patient: Patient) -> bool:
        """Add a new patient to the database"""
        patients = self._load_json(self.patients_file)
        
        # Check if patient already exists
        if any(p['id'] == patient.id for p in patients):
            return False
        
        patients.append(patient.to_dict())
        self._save_json(self.patients_file, patients)
        return True
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID"""
        patients = self._load_json(self.patients_file)
        for patient_data in patients:
            if patient_data['id'] == patient_id:
                return self._dict_to_patient(patient_data)
        return None
    
    def get_patients(self) -> List[Patient]:
        """Get all patients"""
        patients = self._load_json(self.patients_file)
        return [self._dict_to_patient(p) for p in patients]
    
    def update_patient(self, patient: Patient) -> bool:
        """Update patient information"""
        patients = self._load_json(self.patients_file)
        for i, p in enumerate(patients):
            if p['id'] == patient.id:
                patients[i] = patient.to_dict()
                self._save_json(self.patients_file, patients)
                return True
        return False
    
    def _dict_to_patient(self, data: Dict) -> Patient:
        """Convert dictionary to Patient object"""
        return Patient(
            id=data['id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=datetime.fromisoformat(data['date_of_birth']),
            phone=data['phone'],
            email=data['email'],
            address=data['address'],
            emergency_contact=data['emergency_contact'],
            insurance_provider=data['insurance_provider'],
            insurance_number=data['insurance_number'],
            insurance_status=InsuranceStatus(data['insurance_status']),
            status=PatientStatus(data['status']),
            no_show_count=data['no_show_count'],
            last_appointment=datetime.fromisoformat(data['last_appointment']) if data['last_appointment'] else None,
            preferred_communication=data['preferred_communication'],
            notes=data['notes'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    # Doctor Management
    def add_doctor(self, doctor: Doctor) -> bool:
        """Add a new doctor to the database"""
        doctors = self._load_json(self.doctors_file)
        
        if any(d['id'] == doctor.id for d in doctors):
            return False
        
        doctors.append(doctor.to_dict())
        self._save_json(self.doctors_file, doctors)
        return True
    
    def get_doctor(self, doctor_id: str) -> Optional[Doctor]:
        """Get doctor by ID"""
        doctors = self._load_json(self.doctors_file)
        for doctor_data in doctors:
            if doctor_data['id'] == doctor_id:
                return self._dict_to_doctor(doctor_data)
        return None
    
    def get_doctors(self) -> List[Doctor]:
        """Get all doctors"""
        doctors = self._load_json(self.doctors_file)
        return [self._dict_to_doctor(d) for d in doctors]
    
    def _dict_to_doctor(self, data: Dict) -> Doctor:
        """Convert dictionary to Doctor object"""
        return Doctor(
            id=data['id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            specialty=data['specialty'],
            phone=data['phone'],
            email=data['email'],
            working_hours=data['working_hours'],
            appointment_duration=data['appointment_duration'],
            max_patients_per_day=data['max_patients_per_day'],
            is_active=data['is_active']
        )
    
    # Appointment Management
    def add_appointment(self, appointment: Appointment) -> bool:
        """Add a new appointment to the database"""
        appointments = self._load_json(self.appointments_file)
        
        if any(a['id'] == appointment.id for a in appointments):
            return False
        
        appointments.append(appointment.to_dict())
        self._save_json(self.appointments_file, appointments)
        return True
    
    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID"""
        appointments = self._load_json(self.appointments_file)
        for appointment_data in appointments:
            if appointment_data['id'] == appointment_id:
                return self._dict_to_appointment(appointment_data)
        return None
    
    def get_appointments(self, doctor_id: Optional[str] = None, 
                        patient_id: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Appointment]:
        """Get appointments with optional filters"""
        appointments = self._load_json(self.appointments_file)
        result = []
        
        for appointment_data in appointments:
            appointment = self._dict_to_appointment(appointment_data)
            
            # Apply filters
            if doctor_id and appointment.doctor_id != doctor_id:
                continue
            if patient_id and appointment.patient_id != patient_id:
                continue
            if start_date and appointment.appointment_datetime < start_date:
                continue
            if end_date and appointment.appointment_datetime > end_date:
                continue
            
            result.append(appointment)
        
        return result
    
    def update_appointment(self, appointment: Appointment) -> bool:
        """Update appointment information"""
        appointments = self._load_json(self.appointments_file)
        for i, a in enumerate(appointments):
            if a['id'] == appointment.id:
                appointments[i] = appointment.to_dict()
                self._save_json(self.appointments_file, appointments)
                return True
        return False
    
    def _dict_to_appointment(self, data: Dict) -> Appointment:
        """Convert dictionary to Appointment object"""
        return Appointment(
            id=data['id'],
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            appointment_datetime=datetime.fromisoformat(data['appointment_datetime']),
            duration=data['duration'],
            status=AppointmentStatus(data['status']),
            appointment_type=data['appointment_type'],
            notes=data['notes'],
            insurance_verified=data['insurance_verified'],
            reminder_sent=data['reminder_sent'],
            confirmation_sent=data['confirmation_sent'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )
    
    # No-Show Prediction Management
    def add_no_show_prediction(self, prediction: NoShowPrediction) -> bool:
        """Add a no-show prediction"""
        predictions = self._load_json(self.predictions_file)
        
        # Remove existing prediction for this appointment
        predictions = [p for p in predictions if p['appointment_id'] != prediction.appointment_id]
        
        predictions.append(prediction.to_dict())
        self._save_json(self.predictions_file, predictions)
        return True
    
    def get_no_show_prediction(self, appointment_id: str) -> Optional[NoShowPrediction]:
        """Get no-show prediction for an appointment"""
        predictions = self._load_json(self.predictions_file)
        for prediction_data in predictions:
            if prediction_data['appointment_id'] == appointment_id:
                return self._dict_to_no_show_prediction(prediction_data)
        return None
    
    def _dict_to_no_show_prediction(self, data: Dict) -> NoShowPrediction:
        """Convert dictionary to NoShowPrediction object"""
        return NoShowPrediction(
            patient_id=data['patient_id'],
            appointment_id=data['appointment_id'],
            risk_score=data['risk_score'],
            risk_factors=data['risk_factors'],
            prediction_date=datetime.fromisoformat(data['prediction_date'])
        )
    
    # Clinic Settings
    def get_clinic_settings(self) -> Optional[ClinicSettings]:
        """Get clinic settings"""
        settings_data = self._load_json(self.settings_file)
        if settings_data:
            return self._dict_to_clinic_settings(settings_data[0])
        return None
    
    def update_clinic_settings(self, settings: ClinicSettings) -> bool:
        """Update clinic settings"""
        self._save_json(self.settings_file, [settings.to_dict()])
        return True
    
    def _dict_to_clinic_settings(self, data: Dict) -> ClinicSettings:
        """Convert dictionary to ClinicSettings object"""
        return ClinicSettings(
            clinic_name=data['clinic_name'],
            address=data['address'],
            phone=data['phone'],
            email=data['email'],
            timezone=data.get('timezone', 'America/New_York'),
            reminder_hours_before=data.get('reminder_hours_before', 24),
            confirmation_hours_before=data.get('confirmation_hours_before', 2),
            no_show_threshold=data.get('no_show_threshold', 3),
            auto_reschedule_enabled=data.get('auto_reschedule_enabled', True),
            insurance_verification_required=data.get('insurance_verification_required', True),
            cancellation_policy_hours=data.get('cancellation_policy_hours', 24)
        )
    
    def get_appointments_needing_reminders(self, hours_before: int = 24) -> List[Appointment]:
        """Get appointments that need reminders"""
        cutoff_time = datetime.now() + timedelta(hours=hours_before)
        appointments = self.get_appointments()
        
        needing_reminders = []
        for appointment in appointments:
            if (appointment.status.value in ['scheduled', 'confirmed'] and
                appointment.appointment_datetime <= cutoff_time and
                not appointment.reminder_sent):
                needing_reminders.append(appointment)
        
        return needing_reminders
    
    def get_appointments_needing_confirmation(self, hours_before: int = 2) -> List[Appointment]:
        """Get appointments that need confirmation"""
        cutoff_time = datetime.now() + timedelta(hours=hours_before)
        appointments = self.get_appointments()
        
        needing_confirmation = []
        for appointment in appointments:
            if (appointment.status.value == 'scheduled' and
                appointment.appointment_datetime <= cutoff_time and
                not appointment.confirmation_sent):
                needing_confirmation.append(appointment)
        
        return needing_confirmation
    
    def get_high_risk_patients(self) -> List[Patient]:
        """Get patients with high no-show risk"""
        patients = self.get_patients()
        return [p for p in patients if p.status.value == 'high_risk']
