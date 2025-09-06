"""
Database models for the Medical Appointment Scheduling AI Agent
"""
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json


class AppointmentStatus(Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class PatientStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    HIGH_RISK = "high_risk"


class InsuranceStatus(Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass
class Patient:
    """Patient information model"""
    id: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    phone: str
    email: str
    address: str
    emergency_contact: str
    insurance_provider: str
    insurance_number: str
    insurance_status: InsuranceStatus = InsuranceStatus.PENDING
    status: PatientStatus = PatientStatus.ACTIVE
    no_show_count: int = 0
    last_appointment: Optional[datetime] = None
    preferred_communication: str = "phone"  # phone, email, sms
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat(),
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'insurance_provider': self.insurance_provider,
            'insurance_number': self.insurance_number,
            'insurance_status': self.insurance_status.value,
            'status': self.status.value,
            'no_show_count': self.no_show_count,
            'last_appointment': self.last_appointment.isoformat() if self.last_appointment else None,
            'preferred_communication': self.preferred_communication,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class Doctor:
    """Doctor/Provider information model"""
    id: str
    first_name: str
    last_name: str
    specialty: str
    phone: str
    email: str
    working_hours: dict  # {"monday": {"start": "09:00", "end": "17:00"}, ...}
    appointment_duration: int = 30  # minutes
    max_patients_per_day: int = 20
    is_active: bool = True
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'specialty': self.specialty,
            'phone': self.phone,
            'email': self.email,
            'working_hours': self.working_hours,
            'appointment_duration': self.appointment_duration,
            'max_patients_per_day': self.max_patients_per_day,
            'is_active': self.is_active
        }


@dataclass
class Appointment:
    """Appointment model"""
    id: str
    patient_id: str
    doctor_id: str
    appointment_datetime: datetime
    duration: int = 30  # minutes
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    appointment_type: str = "general"  # general, follow_up, consultation, etc.
    notes: str = ""
    insurance_verified: bool = False
    reminder_sent: bool = False
    confirmation_sent: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_datetime': self.appointment_datetime.isoformat(),
            'duration': self.duration,
            'status': self.status.value,
            'appointment_type': self.appointment_type,
            'notes': self.notes,
            'insurance_verified': self.insurance_verified,
            'reminder_sent': self.reminder_sent,
            'confirmation_sent': self.confirmation_sent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class NoShowPrediction:
    """No-show prediction model"""
    patient_id: str
    appointment_id: str
    risk_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    prediction_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'patient_id': self.patient_id,
            'appointment_id': self.appointment_id,
            'risk_score': self.risk_score,
            'risk_factors': self.risk_factors,
            'prediction_date': self.prediction_date.isoformat()
        }


@dataclass
class ClinicSettings:
    """Clinic configuration settings"""
    clinic_name: str
    address: str
    phone: str
    email: str
    timezone: str = "America/New_York"
    reminder_hours_before: int = 24
    confirmation_hours_before: int = 2
    no_show_threshold: int = 3
    auto_reschedule_enabled: bool = True
    insurance_verification_required: bool = True
    cancellation_policy_hours: int = 24
    
    def to_dict(self) -> dict:
        return {
            'clinic_name': self.clinic_name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'timezone': self.timezone,
            'reminder_hours_before': self.reminder_hours_before,
            'confirmation_hours_before': self.confirmation_hours_before,
            'no_show_threshold': self.no_show_threshold,
            'auto_reschedule_enabled': self.auto_reschedule_enabled,
            'insurance_verification_required': self.insurance_verification_required,
            'cancellation_policy_hours': self.cancellation_policy_hours
        }
