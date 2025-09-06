"""
Appointment Scheduling Service for the Medical Appointment Scheduling AI Agent
"""
import uuid
from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Tuple
try:
    from .models import Patient, Doctor, Appointment, AppointmentStatus, PatientStatus
    from .database import MedicalDatabase
except ImportError:
    from models import Patient, Doctor, Appointment, AppointmentStatus, PatientStatus
    from database import MedicalDatabase


class SchedulingService:
    """Core appointment scheduling service"""
    
    def __init__(self, database: MedicalDatabase):
        self.db = database
    
    def register_patient(self, first_name: str, last_name: str, date_of_birth: datetime,
                        phone: str, email: str, address: str, emergency_contact: str,
                        insurance_provider: str, insurance_number: str,
                        preferred_communication: str = "phone", notes: str = "") -> str:
        """Register a new patient"""
        patient_id = str(uuid.uuid4())
        patient = Patient(
            id=patient_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone=phone,
            email=email,
            address=address,
            emergency_contact=emergency_contact,
            insurance_provider=insurance_provider,
            insurance_number=insurance_number,
            preferred_communication=preferred_communication,
            notes=notes
        )
        
        if self.db.add_patient(patient):
            return patient_id
        else:
            raise ValueError("Failed to register patient - patient may already exist")
    
    def find_patient(self, phone: str = None, email: str = None, 
                    first_name: str = None, last_name: str = None) -> List[Patient]:
        """Find patients by various criteria"""
        patients = self.db.get_patients()
        results = []
        
        for patient in patients:
            match = True
            
            if phone and patient.phone != phone:
                match = False
            if email and patient.email != email:
                match = False
            if first_name and patient.first_name.lower() != first_name.lower():
                match = False
            if last_name and patient.last_name.lower() != last_name.lower():
                match = False
            
            if match:
                results.append(patient)
        
        return results
    
    def get_available_slots(self, doctor_id: str, date: datetime, 
                          appointment_duration: int = 30) -> List[datetime]:
        """Get available appointment slots for a doctor on a specific date"""
        doctor = self.db.get_doctor(doctor_id)
        if not doctor:
            return []
        
        # Get doctor's working hours for the day
        day_name = date.strftime('%A').lower()
        if day_name not in doctor.working_hours:
            return []
        
        working_hours = doctor.working_hours[day_name]
        start_time = datetime.strptime(working_hours['start'], '%H:%M').time()
        end_time = datetime.strptime(working_hours['end'], '%H:%M').time()
        
        # Get existing appointments for the day
        if hasattr(date, 'date'):
            date_obj = date.date()
        else:
            date_obj = date
        start_of_day = datetime.combine(date_obj, start_time)
        end_of_day = datetime.combine(date_obj, end_time)
        existing_appointments = self.db.get_appointments(
            doctor_id=doctor_id,
            start_date=start_of_day,
            end_date=end_of_day
        )
        
        # Create list of occupied time slots
        occupied_slots = []
        for appointment in existing_appointments:
            if appointment.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]:
                occupied_slots.append(appointment.appointment_datetime)
        
        # Generate available slots
        available_slots = []
        current_time = start_of_day
        
        while current_time + timedelta(minutes=appointment_duration) <= end_of_day:
            # Check if this slot conflicts with existing appointments
            slot_conflict = False
            for occupied_slot in occupied_slots:
                if abs((current_time - occupied_slot).total_seconds()) < appointment_duration * 60:
                    slot_conflict = True
                    break
            
            if not slot_conflict:
                available_slots.append(current_time)
            
            current_time += timedelta(minutes=appointment_duration)
        
        return available_slots
    
    def book_appointment(self, patient_id: str, doctor_id: str, 
                        appointment_datetime: datetime, appointment_type: str = "general",
                        notes: str = "") -> str:
        """Book a new appointment"""
        # Validate patient exists
        patient = self.db.get_patient(patient_id)
        if not patient:
            raise ValueError("Patient not found")
        
        # Validate doctor exists
        doctor = self.db.get_doctor(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")
        
        # Check if slot is available
        available_slots = self.get_available_slots(doctor_id, appointment_datetime, doctor.appointment_duration)
        if appointment_datetime not in available_slots:
            raise ValueError("Appointment slot not available")
        
        # Create appointment
        appointment_id = str(uuid.uuid4())
        appointment = Appointment(
            id=appointment_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_datetime,
            duration=doctor.appointment_duration,
            appointment_type=appointment_type,
            notes=notes
        )
        
        if self.db.add_appointment(appointment):
            return appointment_id
        else:
            raise ValueError("Failed to book appointment")
    
    def reschedule_appointment(self, appointment_id: str, new_datetime: datetime) -> bool:
        """Reschedule an existing appointment"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            return False
        
        # Check if new slot is available
        available_slots = self.get_available_slots(
            appointment.doctor_id, new_datetime, appointment.duration
        )
        if new_datetime not in available_slots:
            return False
        
        # Update appointment
        appointment.appointment_datetime = new_datetime
        appointment.status = AppointmentStatus.RESCHEDULED
        appointment.updated_at = datetime.now()
        
        return self.db.update_appointment(appointment)
    
    def cancel_appointment(self, appointment_id: str, reason: str = "") -> bool:
        """Cancel an appointment"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            return False
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.notes += f"\nCancelled: {reason}" if reason else "\nCancelled"
        appointment.updated_at = datetime.now()
        
        return self.db.update_appointment(appointment)
    
    def mark_no_show(self, appointment_id: str) -> bool:
        """Mark an appointment as no-show"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            return False
        
        appointment.status = AppointmentStatus.NO_SHOW
        appointment.updated_at = datetime.now()
        
        # Update patient's no-show count
        patient = self.db.get_patient(appointment.patient_id)
        if patient:
            patient.no_show_count += 1
            if patient.no_show_count >= 3:  # Threshold for high-risk patients
                patient.status = PatientStatus.HIGH_RISK
            self.db.update_patient(patient)
        
        return self.db.update_appointment(appointment)
    
    def complete_appointment(self, appointment_id: str, notes: str = "") -> bool:
        """Mark an appointment as completed"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            return False
        
        appointment.status = AppointmentStatus.COMPLETED
        appointment.notes += f"\nCompleted: {notes}" if notes else "\nCompleted"
        appointment.updated_at = datetime.now()
        
        # Update patient's last appointment date
        patient = self.db.get_patient(appointment.patient_id)
        if patient:
            patient.last_appointment = appointment.appointment_datetime
            self.db.update_patient(patient)
        
        return self.db.update_appointment(appointment)
    
    def get_patient_appointments(self, patient_id: str, 
                               upcoming_only: bool = True) -> List[Appointment]:
        """Get appointments for a specific patient"""
        appointments = self.db.get_appointments(patient_id=patient_id)
        
        if upcoming_only:
            now = datetime.now()
            appointments = [a for a in appointments if a.appointment_datetime > now]
        
        return sorted(appointments, key=lambda x: x.appointment_datetime)
    
    def get_doctor_schedule(self, doctor_id: str, date: datetime) -> List[Appointment]:
        """Get doctor's schedule for a specific date"""
        start_of_day = datetime.combine(date.date(), time.min)
        end_of_day = datetime.combine(date.date(), time.max)
        
        appointments = self.db.get_appointments(
            doctor_id=doctor_id,
            start_date=start_of_day,
            end_date=end_of_day
        )
        
        return sorted(appointments, key=lambda x: x.appointment_datetime)
    
    def get_appointments_needing_reminders(self, hours_before: int = 24) -> List[Appointment]:
        """Get appointments that need reminders"""
        cutoff_time = datetime.now() + timedelta(hours=hours_before)
        appointments = self.db.get_appointments()
        
        needing_reminders = []
        for appointment in appointments:
            if (appointment.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED] and
                appointment.appointment_datetime <= cutoff_time and
                not appointment.reminder_sent):
                needing_reminders.append(appointment)
        
        return needing_reminders
    
    def get_appointments_needing_confirmation(self, hours_before: int = 2) -> List[Appointment]:
        """Get appointments that need confirmation"""
        cutoff_time = datetime.now() + timedelta(hours=hours_before)
        appointments = self.db.get_appointments()
        
        needing_confirmation = []
        for appointment in appointments:
            if (appointment.status == AppointmentStatus.SCHEDULED and
                appointment.appointment_datetime <= cutoff_time and
                not appointment.confirmation_sent):
                needing_confirmation.append(appointment)
        
        return needing_confirmation
    
    def get_high_risk_patients(self) -> List[Patient]:
        """Get patients with high no-show risk"""
        patients = self.db.get_patients()
        return [p for p in patients if p.status == PatientStatus.HIGH_RISK]
    
    def get_appointment_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get appointment statistics for a date range"""
        appointments = self.db.get_appointments(start_date=start_date, end_date=end_date)
        
        stats = {
            'total_appointments': len(appointments),
            'scheduled': 0,
            'confirmed': 0,
            'completed': 0,
            'cancelled': 0,
            'no_shows': 0,
            'rescheduled': 0
        }
        
        for appointment in appointments:
            status = appointment.status.value
            if status in stats:
                stats[status] += 1
        
        # Calculate no-show rate
        total_attempted = stats['completed'] + stats['no_shows'] + stats['cancelled']
        stats['no_show_rate'] = (stats['no_shows'] / total_attempted * 100) if total_attempted > 0 else 0
        
        return stats
