"""
Automated Reminder and Notification Service for the Medical Appointment Scheduling AI Agent
"""
import smtplib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import Patient, Doctor, Appointment, AppointmentStatus
from database import MedicalDatabase
from no_show_predictor import NoShowPredictor


class NotificationService:
    """Automated notification and reminder service"""
    
    def __init__(self, database: MedicalDatabase, no_show_predictor: NoShowPredictor):
        self.db = database
        self.no_show_predictor = no_show_predictor
        self.smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': '',  # To be configured
            'password': ''   # To be configured
        }
    
    def send_appointment_reminder(self, appointment_id: str) -> bool:
        """Send appointment reminder to patient"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            return False
        
        patient = self.db.get_patient(appointment.patient_id)
        doctor = self.db.get_doctor(appointment.doctor_id)
        
        if not patient or not doctor:
            return False
        
        # Check if reminder already sent
        if appointment.reminder_sent:
            return True
        
        # Get no-show prediction for personalized messaging
        prediction = self.db.get_no_show_prediction(appointment_id)
        risk_level = "low"
        if prediction:
            if prediction.risk_score > 0.7:
                risk_level = "high"
            elif prediction.risk_score > 0.4:
                risk_level = "medium"
        
        # Send based on patient's preferred communication method
        success = False
        if patient.preferred_communication == "email":
            success = self._send_email_reminder(patient, doctor, appointment, risk_level)
        elif patient.preferred_communication == "sms":
            success = self._send_sms_reminder(patient, doctor, appointment, risk_level)
        else:  # phone
            success = self._send_phone_reminder(patient, doctor, appointment, risk_level)
        
        # Update appointment if reminder sent successfully
        if success:
            appointment.reminder_sent = True
            appointment.updated_at = datetime.now()
            self.db.update_appointment(appointment)
        
        return success
    
    def send_appointment_confirmation(self, appointment_id: str) -> bool:
        """Send appointment confirmation request"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            return False
        
        patient = self.db.get_patient(appointment.patient_id)
        doctor = self.db.get_doctor(appointment.doctor_id)
        
        if not patient or not doctor:
            return False
        
        # Check if confirmation already sent
        if appointment.confirmation_sent:
            return True
        
        # Send confirmation based on patient's preferred communication
        success = False
        if patient.preferred_communication == "email":
            success = self._send_email_confirmation(patient, doctor, appointment)
        elif patient.preferred_communication == "sms":
            success = self._send_sms_confirmation(patient, doctor, appointment)
        else:  # phone
            success = self._send_phone_confirmation(patient, doctor, appointment)
        
        # Update appointment if confirmation sent successfully
        if success:
            appointment.confirmation_sent = True
            appointment.updated_at = datetime.now()
            self.db.update_appointment(appointment)
        
        return success
    
    def send_no_show_follow_up(self, appointment_id: str) -> bool:
        """Send follow-up message after a no-show"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment or appointment.status != AppointmentStatus.NO_SHOW:
            return False
        
        patient = self.db.get_patient(appointment.patient_id)
        doctor = self.db.get_doctor(appointment.doctor_id)
        
        if not patient or not doctor:
            return False
        
        # Send follow-up message
        success = False
        if patient.preferred_communication == "email":
            success = self._send_email_no_show_followup(patient, doctor, appointment)
        elif patient.preferred_communication == "sms":
            success = self._send_sms_no_show_followup(patient, doctor, appointment)
        else:  # phone
            success = self._send_phone_no_show_followup(patient, doctor, appointment)
        
        return success
    
    def send_appointment_cancellation(self, appointment_id: str, reason: str = "") -> bool:
        """Send appointment cancellation notification"""
        appointment = self.db.get_appointment(appointment_id)
        if not appointment:
            return False
        
        patient = self.db.get_patient(appointment.patient_id)
        doctor = self.db.get_doctor(appointment.doctor_id)
        
        if not patient or not doctor:
            return False
        
        # Send cancellation notification
        success = False
        if patient.preferred_communication == "email":
            success = self._send_email_cancellation(patient, doctor, appointment, reason)
        elif patient.preferred_communication == "sms":
            success = self._send_sms_cancellation(patient, doctor, appointment, reason)
        else:  # phone
            success = self._send_phone_cancellation(patient, doctor, appointment, reason)
        
        return success
    
    def process_scheduled_reminders(self) -> Dict:
        """Process all appointments that need reminders"""
        settings = self.db.get_clinic_settings()
        if not settings:
            return {'error': 'Clinic settings not configured'}
        
        # Get appointments needing reminders
        appointments_needing_reminders = self.db.get_appointments_needing_reminders(
            settings.reminder_hours_before
        )
        
        # Get appointments needing confirmation
        appointments_needing_confirmation = self.db.get_appointments_needing_confirmation(
            settings.confirmation_hours_before
        )
        
        results = {
            'reminders_sent': 0,
            'confirmations_sent': 0,
            'reminder_failures': 0,
            'confirmation_failures': 0,
            'high_risk_appointments': 0
        }
        
        # Send reminders
        for appointment in appointments_needing_reminders:
            try:
                if self.send_appointment_reminder(appointment.id):
                    results['reminders_sent'] += 1
                else:
                    results['reminder_failures'] += 1
            except Exception as e:
                results['reminder_failures'] += 1
                print(f"Error sending reminder for appointment {appointment.id}: {e}")
        
        # Send confirmations
        for appointment in appointments_needing_confirmation:
            try:
                if self.send_appointment_confirmation(appointment.id):
                    results['confirmations_sent'] += 1
                else:
                    results['confirmation_failures'] += 1
            except Exception as e:
                results['confirmation_failures'] += 1
                print(f"Error sending confirmation for appointment {appointment.id}: {e}")
        
        # Check for high-risk appointments
        high_risk_appointments = self.no_show_predictor.get_high_risk_appointments()
        results['high_risk_appointments'] = len(high_risk_appointments)
        
        return results
    
    def _send_email_reminder(self, patient: Patient, doctor: Doctor, 
                           appointment: Appointment, risk_level: str) -> bool:
        """Send email reminder"""
        try:
            # Create email content based on risk level
            if risk_level == "high":
                subject = f"URGENT: Appointment Reminder - {doctor.first_name} {doctor.last_name}"
                body = self._get_high_risk_reminder_email(patient, doctor, appointment)
            else:
                subject = f"Appointment Reminder - {doctor.first_name} {doctor.last_name}"
                body = self._get_standard_reminder_email(patient, doctor, appointment)
            
            # Send email (simulated for demo)
            print(f"EMAIL REMINDER SENT to {patient.email}")
            print(f"Subject: {subject}")
            print(f"Body: {body[:200]}...")
            
            return True
        except Exception as e:
            print(f"Error sending email reminder: {e}")
            return False
    
    def _send_sms_reminder(self, patient: Patient, doctor: Doctor, 
                          appointment: Appointment, risk_level: str) -> bool:
        """Send SMS reminder"""
        try:
            appointment_time = appointment.appointment_datetime.strftime("%B %d, %Y at %I:%M %p")
            
            if risk_level == "high":
                message = f"URGENT: Your appointment with Dr. {doctor.last_name} is tomorrow at {appointment_time}. Please confirm by replying YES or call us to reschedule."
            else:
                message = f"Reminder: Your appointment with Dr. {doctor.last_name} is tomorrow at {appointment_time}. Reply YES to confirm."
            
            # Send SMS (simulated for demo)
            print(f"SMS REMINDER SENT to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending SMS reminder: {e}")
            return False
    
    def _send_phone_reminder(self, patient: Patient, doctor: Doctor, 
                           appointment: Appointment, risk_level: str) -> bool:
        """Send phone reminder (simulated)"""
        try:
            appointment_time = appointment.appointment_datetime.strftime("%B %d, %Y at %I:%M %p")
            
            if risk_level == "high":
                message = f"URGENT: Your appointment with Dr. {doctor.last_name} is tomorrow at {appointment_time}. Please call us to confirm or reschedule."
            else:
                message = f"Reminder: Your appointment with Dr. {doctor.last_name} is tomorrow at {appointment_time}. Please call us to confirm."
            
            # Simulate phone call
            print(f"PHONE REMINDER SENT to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending phone reminder: {e}")
            return False
    
    def _send_email_confirmation(self, patient: Patient, doctor: Doctor, 
                               appointment: Appointment) -> bool:
        """Send email confirmation request"""
        try:
            subject = f"Please Confirm Your Appointment - {doctor.first_name} {doctor.last_name}"
            body = self._get_confirmation_email(patient, doctor, appointment)
            
            print(f"EMAIL CONFIRMATION SENT to {patient.email}")
            print(f"Subject: {subject}")
            print(f"Body: {body[:200]}...")
            
            return True
        except Exception as e:
            print(f"Error sending email confirmation: {e}")
            return False
    
    def _send_sms_confirmation(self, patient: Patient, doctor: Doctor, 
                             appointment: Appointment) -> bool:
        """Send SMS confirmation request"""
        try:
            appointment_time = appointment.appointment_datetime.strftime("%B %d, %Y at %I:%M %p")
            message = f"Please confirm your appointment with Dr. {doctor.last_name} tomorrow at {appointment_time}. Reply YES to confirm or NO to cancel."
            
            print(f"SMS CONFIRMATION SENT to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending SMS confirmation: {e}")
            return False
    
    def _send_phone_confirmation(self, patient: Patient, doctor: Doctor, 
                               appointment: Appointment) -> bool:
        """Send phone confirmation request"""
        try:
            appointment_time = appointment.appointment_datetime.strftime("%B %d, %Y at %I:%M %p")
            message = f"Please confirm your appointment with Dr. {doctor.last_name} tomorrow at {appointment_time}. Call us to confirm or cancel."
            
            print(f"PHONE CONFIRMATION SENT to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending phone confirmation: {e}")
            return False
    
    def _get_standard_reminder_email(self, patient: Patient, doctor: Doctor, 
                                   appointment: Appointment) -> str:
        """Generate standard reminder email content"""
        appointment_time = appointment.appointment_datetime.strftime("%B %d, %Y at %I:%M %p")
        
        return f"""
Dear {patient.first_name},

This is a friendly reminder about your upcoming appointment:

Doctor: Dr. {doctor.first_name} {doctor.last_name}
Specialty: {doctor.specialty}
Date & Time: {appointment_time}
Duration: {appointment.duration} minutes
Appointment Type: {appointment.appointment_type}

Please arrive 15 minutes early for check-in. If you need to reschedule or cancel, please call us at least 24 hours in advance.

We look forward to seeing you!

Best regards,
{self.db.get_clinic_settings().clinic_name if self.db.get_clinic_settings() else 'Medical Clinic'}
        """.strip()
    
    def _get_high_risk_reminder_email(self, patient: Patient, doctor: Doctor, 
                                    appointment: Appointment) -> str:
        """Generate high-risk reminder email content"""
        appointment_time = appointment.appointment_datetime.strftime("%B %d, %Y at %I:%M %p")
        
        return f"""
Dear {patient.first_name},

IMPORTANT: This is an urgent reminder about your upcoming appointment:

Doctor: Dr. {doctor.first_name} {doctor.last_name}
Specialty: {doctor.specialty}
Date & Time: {appointment_time}
Duration: {appointment.duration} minutes
Appointment Type: {appointment.appointment_type}

Please confirm your attendance by replying to this email or calling us immediately. If you need to reschedule, please contact us as soon as possible.

We understand that circumstances can change, but please let us know so we can help other patients who may need this time slot.

Thank you for your attention to this matter.

Best regards,
{self.db.get_clinic_settings().clinic_name if self.db.get_clinic_settings() else 'Medical Clinic'}
        """.strip()
    
    def _get_confirmation_email(self, patient: Patient, doctor: Doctor, 
                              appointment: Appointment) -> str:
        """Generate confirmation email content"""
        appointment_time = appointment.appointment_datetime.strftime("%B %d, %Y at %I:%M %p")
        
        return f"""
Dear {patient.first_name},

Please confirm your appointment for tomorrow:

Doctor: Dr. {doctor.first_name} {doctor.last_name}
Date & Time: {appointment_time}
Duration: {appointment.duration} minutes

Please reply to this email with "CONFIRM" to confirm your appointment, or "CANCEL" if you need to cancel.

If you need to reschedule, please call us as soon as possible.

Thank you!

Best regards,
{self.db.get_clinic_settings().clinic_name if self.db.get_clinic_settings() else 'Medical Clinic'}
        """.strip()
    
    def _send_email_no_show_followup(self, patient: Patient, doctor: Doctor, 
                                   appointment: Appointment) -> bool:
        """Send no-show follow-up email"""
        try:
            subject = f"We Missed You - Reschedule Your Appointment"
            body = f"""
Dear {patient.first_name},

We noticed you missed your appointment with Dr. {doctor.last_name} on {appointment.appointment_datetime.strftime('%B %d, %Y at %I:%M %p')}.

We understand that things come up, and we're here to help. Please call us to reschedule your appointment at your convenience.

We're committed to providing you with the best care, and we look forward to seeing you soon.

Best regards,
{self.db.get_clinic_settings().clinic_name if self.db.get_clinic_settings() else 'Medical Clinic'}
            """.strip()
            
            print(f"NO-SHOW FOLLOW-UP EMAIL SENT to {patient.email}")
            print(f"Subject: {subject}")
            
            return True
        except Exception as e:
            print(f"Error sending no-show follow-up email: {e}")
            return False
    
    def _send_sms_no_show_followup(self, patient: Patient, doctor: Doctor, 
                                 appointment: Appointment) -> bool:
        """Send no-show follow-up SMS"""
        try:
            message = f"We missed you at your appointment with Dr. {doctor.last_name}. Please call us to reschedule. We're here to help!"
            
            print(f"NO-SHOW FOLLOW-UP SMS SENT to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending no-show follow-up SMS: {e}")
            return False
    
    def _send_phone_no_show_followup(self, patient: Patient, doctor: Doctor, 
                                   appointment: Appointment) -> bool:
        """Send no-show follow-up phone call"""
        try:
            message = f"We missed you at your appointment with Dr. {doctor.last_name}. Please call us to reschedule. We're here to help!"
            
            print(f"NO-SHOW FOLLOW-UP PHONE CALL to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending no-show follow-up phone call: {e}")
            return False
    
    def _send_email_cancellation(self, patient: Patient, doctor: Doctor, 
                               appointment: Appointment, reason: str) -> bool:
        """Send appointment cancellation email"""
        try:
            subject = f"Appointment Cancelled - {doctor.first_name} {doctor.last_name}"
            body = f"""
Dear {patient.first_name},

Your appointment with Dr. {doctor.last_name} on {appointment.appointment_datetime.strftime('%B %d, %Y at %I:%M %p')} has been cancelled.

{f'Reason: {reason}' if reason else ''}

Please call us to reschedule at your convenience.

Best regards,
{self.db.get_clinic_settings().clinic_name if self.db.get_clinic_settings() else 'Medical Clinic'}
            """.strip()
            
            print(f"CANCELLATION EMAIL SENT to {patient.email}")
            print(f"Subject: {subject}")
            
            return True
        except Exception as e:
            print(f"Error sending cancellation email: {e}")
            return False
    
    def _send_sms_cancellation(self, patient: Patient, doctor: Doctor, 
                             appointment: Appointment, reason: str) -> bool:
        """Send appointment cancellation SMS"""
        try:
            message = f"Your appointment with Dr. {doctor.last_name} has been cancelled. Please call us to reschedule."
            
            print(f"CANCELLATION SMS SENT to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending cancellation SMS: {e}")
            return False
    
    def _send_phone_cancellation(self, patient: Patient, doctor: Doctor, 
                               appointment: Appointment, reason: str) -> bool:
        """Send appointment cancellation phone call"""
        try:
            message = f"Your appointment with Dr. {doctor.last_name} has been cancelled. Please call us to reschedule."
            
            print(f"CANCELLATION PHONE CALL to {patient.phone}")
            print(f"Message: {message}")
            
            return True
        except Exception as e:
            print(f"Error sending cancellation phone call: {e}")
            return False
