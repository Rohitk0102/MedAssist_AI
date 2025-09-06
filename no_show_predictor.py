"""
No-Show Prediction System for the Medical Appointment Scheduling AI Agent
"""
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
try:
    from .models import Patient, Appointment, NoShowPrediction, AppointmentStatus
    from .database import MedicalDatabase
except ImportError:
    from models import Patient, Appointment, NoShowPrediction, AppointmentStatus
    from database import MedicalDatabase


class NoShowPredictor:
    """AI-powered no-show prediction system"""
    
    def __init__(self, database: MedicalDatabase):
        self.db = database
    
    def predict_no_show_risk(self, patient_id: str, appointment_id: str) -> NoShowPrediction:
        """Predict the risk of a patient not showing up for an appointment"""
        patient = self.db.get_patient(patient_id)
        appointment = self.db.get_appointment(appointment_id)
        
        if not patient or not appointment:
            raise ValueError("Patient or appointment not found")
        
        # Calculate risk factors and their weights
        risk_factors = []
        risk_score = 0.0
        
        # Historical no-show rate (40% weight)
        historical_risk = self._calculate_historical_risk(patient)
        risk_score += historical_risk * 0.4
        if historical_risk > 0.3:
            risk_factors.append("High historical no-show rate")
        
        # Appointment timing factors (25% weight)
        timing_risk = self._calculate_timing_risk(appointment)
        risk_score += timing_risk * 0.25
        if timing_risk > 0.3:
            risk_factors.append("Unfavorable appointment timing")
        
        # Patient demographics and behavior (20% weight)
        demographic_risk = self._calculate_demographic_risk(patient)
        risk_score += demographic_risk * 0.2
        if demographic_risk > 0.3:
            risk_factors.append("Demographic risk factors")
        
        # Insurance and financial factors (15% weight)
        financial_risk = self._calculate_financial_risk(patient, appointment)
        risk_score += financial_risk * 0.15
        if financial_risk > 0.3:
            risk_factors.append("Insurance/financial concerns")
        
        # Ensure risk score is between 0 and 1
        risk_score = max(0.0, min(1.0, risk_score))
        
        prediction = NoShowPrediction(
            patient_id=patient_id,
            appointment_id=appointment_id,
            risk_score=risk_score,
            risk_factors=risk_factors
        )
        
        # Save prediction to database
        self.db.add_no_show_prediction(prediction)
        
        return prediction
    
    def _calculate_historical_risk(self, patient: Patient) -> float:
        """Calculate risk based on patient's historical no-show behavior"""
        # Get patient's appointment history
        appointments = self.db.get_appointments(patient_id=patient.id)
        
        if len(appointments) < 2:
            # New patients have moderate risk
            return 0.3
        
        no_shows = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
        total_appointments = len(appointments)
        no_show_rate = no_shows / total_appointments
        
        # Recent behavior has more weight
        recent_appointments = [a for a in appointments 
                             if a.appointment_datetime > datetime.now() - timedelta(days=90)]
        if recent_appointments:
            recent_no_shows = sum(1 for a in recent_appointments 
                                if a.status == AppointmentStatus.NO_SHOW)
            recent_no_show_rate = recent_no_shows / len(recent_appointments)
            # Weight recent behavior more heavily
            no_show_rate = (no_show_rate * 0.3) + (recent_no_show_rate * 0.7)
        
        return min(1.0, no_show_rate * 2)  # Scale up the risk
    
    def _calculate_timing_risk(self, appointment: Appointment) -> float:
        """Calculate risk based on appointment timing factors"""
        risk = 0.0
        appointment_time = appointment.appointment_datetime
        
        # Day of week risk
        weekday = appointment_time.weekday()
        if weekday == 0:  # Monday
            risk += 0.1
        elif weekday == 4:  # Friday
            risk += 0.15
        elif weekday >= 5:  # Weekend
            risk += 0.2
        
        # Time of day risk
        hour = appointment_time.hour
        if hour < 9 or hour > 16:  # Early morning or late afternoon
            risk += 0.1
        elif hour == 12:  # Lunch time
            risk += 0.05
        
        # Advance booking risk (appointments booked too far in advance)
        days_advance = (appointment_time - appointment.created_at).days
        if days_advance > 30:
            risk += 0.1
        elif days_advance > 60:
            risk += 0.2
        
        # Last-minute booking risk
        if days_advance < 1:
            risk += 0.15
        
        return min(1.0, risk)
    
    def _calculate_demographic_risk(self, patient: Patient) -> float:
        """Calculate risk based on patient demographics and behavior"""
        risk = 0.0
        
        # Age-based risk (younger patients tend to no-show more)
        age = (datetime.now() - patient.date_of_birth).days / 365.25
        if age < 25:
            risk += 0.2
        elif age < 35:
            risk += 0.1
        elif age > 65:
            risk -= 0.1  # Older patients are more reliable
        
        # Communication preference risk
        if patient.preferred_communication == "email":
            risk += 0.05  # Email reminders are less effective
        
        # Patient status
        if patient.status.value == "high_risk":
            risk += 0.3
        
        # Emergency contact availability (proxy for reliability)
        if not patient.emergency_contact or len(patient.emergency_contact.strip()) < 5:
            risk += 0.1
        
        return max(0.0, min(1.0, risk))
    
    def _calculate_financial_risk(self, patient: Patient, appointment: Appointment) -> float:
        """Calculate risk based on insurance and financial factors"""
        risk = 0.0
        
        # Insurance verification status
        if not appointment.insurance_verified:
            risk += 0.2
        
        # Insurance provider reliability
        unreliable_providers = ["medicaid", "medicare", "self_pay"]
        if patient.insurance_provider.lower() in unreliable_providers:
            risk += 0.1
        
        # Insurance number format (basic validation)
        if len(patient.insurance_number) < 5:
            risk += 0.15
        
        return min(1.0, risk)
    
    def get_high_risk_appointments(self, risk_threshold: float = 0.6) -> List[Tuple[Appointment, NoShowPrediction]]:
        """Get appointments with high no-show risk"""
        appointments = self.db.get_appointments()
        high_risk_appointments = []
        
        for appointment in appointments:
            if appointment.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]:
                prediction = self.db.get_no_show_prediction(appointment.id)
                
                if not prediction:
                    # Generate prediction if it doesn't exist
                    prediction = self.predict_no_show_risk(appointment.patient_id, appointment.id)
                
                if prediction.risk_score >= risk_threshold:
                    high_risk_appointments.append((appointment, prediction))
        
        return high_risk_appointments
    
    def get_risk_mitigation_recommendations(self, prediction: NoShowPrediction) -> List[str]:
        """Get recommendations to reduce no-show risk"""
        recommendations = []
        
        if prediction.risk_score > 0.7:
            recommendations.append("Schedule multiple reminder calls")
            recommendations.append("Send SMS and email reminders")
            recommendations.append("Consider offering appointment rescheduling")
        
        if prediction.risk_score > 0.5:
            recommendations.append("Send confirmation call 24 hours before")
            recommendations.append("Verify insurance information")
        
        if "High historical no-show rate" in prediction.risk_factors:
            recommendations.append("Require deposit or pre-payment")
            recommendations.append("Schedule during preferred time slots")
        
        if "Unfavorable appointment timing" in prediction.risk_factors:
            recommendations.append("Offer alternative time slots")
            recommendations.append("Send extra reminder for timing")
        
        if "Insurance/financial concerns" in prediction.risk_factors:
            recommendations.append("Verify insurance coverage")
            recommendations.append("Discuss payment options")
        
        return recommendations
    
    def calculate_clinic_no_show_rate(self, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate overall clinic no-show statistics"""
        appointments = self.db.get_appointments(start_date=start_date, end_date=end_date)
        
        total_appointments = len(appointments)
        no_shows = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
        completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
        cancelled = sum(1 for a in appointments if a.status == AppointmentStatus.CANCELLED)
        
        # Calculate rates
        no_show_rate = (no_shows / total_appointments * 100) if total_appointments > 0 else 0
        completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
        cancellation_rate = (cancelled / total_appointments * 100) if total_appointments > 0 else 0
        
        # Calculate potential revenue loss
        avg_appointment_value = 150  # Average appointment value in dollars
        potential_revenue_loss = no_shows * avg_appointment_value
        
        return {
            'total_appointments': total_appointments,
            'no_shows': no_shows,
            'completed': completed,
            'cancelled': cancelled,
            'no_show_rate': round(no_show_rate, 2),
            'completion_rate': round(completion_rate, 2),
            'cancellation_rate': round(cancellation_rate, 2),
            'potential_revenue_loss': potential_revenue_loss
        }
    
    def get_patient_risk_profile(self, patient_id: str) -> Dict:
        """Get comprehensive risk profile for a patient"""
        patient = self.db.get_patient(patient_id)
        if not patient:
            return {}
        
        # Get all appointments for this patient
        appointments = self.db.get_appointments(patient_id=patient_id)
        
        # Calculate various metrics
        total_appointments = len(appointments)
        no_shows = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
        completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
        
        no_show_rate = (no_shows / total_appointments * 100) if total_appointments > 0 else 0
        
        # Get most recent prediction if available
        recent_appointments = [a for a in appointments 
                             if a.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]]
        latest_prediction = None
        if recent_appointments:
            latest_appointment = max(recent_appointments, key=lambda x: x.appointment_datetime)
            latest_prediction = self.db.get_no_show_prediction(latest_appointment.id)
        
        return {
            'patient_id': patient_id,
            'patient_name': f"{patient.first_name} {patient.last_name}",
            'total_appointments': total_appointments,
            'no_shows': no_shows,
            'completed': completed,
            'no_show_rate': round(no_show_rate, 2),
            'current_risk_score': latest_prediction.risk_score if latest_prediction else 0.0,
            'risk_level': self._get_risk_level(no_show_rate),
            'last_appointment': patient.last_appointment.isoformat() if patient.last_appointment else None
        }
    
    def _get_risk_level(self, no_show_rate: float) -> str:
        """Convert no-show rate to risk level"""
        if no_show_rate < 10:
            return "Low"
        elif no_show_rate < 25:
            return "Medium"
        elif no_show_rate < 40:
            return "High"
        else:
            return "Very High"
