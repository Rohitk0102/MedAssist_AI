"""
Analytics and Reporting Service for the Medical Appointment Scheduling AI Agent
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from models import AppointmentStatus, PatientStatus
from database import MedicalDatabase
from no_show_predictor import NoShowPredictor
from insurance_service import InsuranceService


class AnalyticsService:
    """Analytics and reporting service for clinic operations"""
    
    def __init__(self, database: MedicalDatabase, no_show_predictor: NoShowPredictor, 
                 insurance_service: InsuranceService):
        self.db = database
        self.no_show_predictor = no_show_predictor
        self.insurance_service = insurance_service
    
    def generate_clinic_dashboard(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate comprehensive clinic dashboard data"""
        return {
            'appointment_statistics': self.get_appointment_statistics(start_date, end_date),
            'revenue_analytics': self.get_revenue_analytics(start_date, end_date),
            'no_show_analytics': self.get_no_show_analytics(start_date, end_date),
            'patient_analytics': self.get_patient_analytics(),
            'doctor_performance': self.get_doctor_performance(start_date, end_date),
            'insurance_analytics': self.insurance_service.get_insurance_statistics(start_date, end_date),
            'operational_insights': self.get_operational_insights(start_date, end_date)
        }
    
    def get_appointment_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get comprehensive appointment statistics"""
        appointments = self.db.get_appointments(start_date=start_date, end_date=end_date)
        
        total_appointments = len(appointments)
        
        # Status breakdown
        status_counts = {}
        for status in AppointmentStatus:
            status_counts[status.value] = sum(1 for a in appointments if a.status == status)
        
        # Calculate rates
        completed = status_counts.get('completed', 0)
        no_shows = status_counts.get('no_show', 0)
        cancelled = status_counts.get('cancelled', 0)
        scheduled = status_counts.get('scheduled', 0)
        confirmed = status_counts.get('confirmed', 0)
        
        # No-show rate calculation
        attempted_appointments = completed + no_shows + cancelled
        no_show_rate = (no_shows / attempted_appointments * 100) if attempted_appointments > 0 else 0
        
        # Completion rate
        completion_rate = (completed / attempted_appointments * 100) if attempted_appointments > 0 else 0
        
        # Cancellation rate
        cancellation_rate = (cancelled / attempted_appointments * 100) if attempted_appointments > 0 else 0
        
        # Appointment type breakdown
        appointment_types = {}
        for appointment in appointments:
            appt_type = appointment.appointment_type
            appointment_types[appt_type] = appointment_types.get(appt_type, 0) + 1
        
        return {
            'total_appointments': total_appointments,
            'status_breakdown': status_counts,
            'no_show_rate': round(no_show_rate, 2),
            'completion_rate': round(completion_rate, 2),
            'cancellation_rate': round(cancellation_rate, 2),
            'appointment_types': appointment_types,
            'pending_appointments': scheduled + confirmed
        }
    
    def get_revenue_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get revenue analytics and financial insights"""
        appointments = self.db.get_appointments(start_date=start_date, end_date=end_date)
        
        # Revenue calculations
        avg_appointment_value = 150.0
        completed_appointments = [a for a in appointments if a.status == AppointmentStatus.COMPLETED]
        no_show_appointments = [a for a in appointments if a.status == AppointmentStatus.NO_SHOW]
        
        # Actual revenue
        actual_revenue = len(completed_appointments) * avg_appointment_value
        
        # Potential revenue (if all appointments were completed)
        potential_revenue = len(appointments) * avg_appointment_value
        
        # Lost revenue due to no-shows
        lost_revenue = len(no_show_appointments) * avg_appointment_value
        
        # Lost revenue due to cancellations
        cancelled_appointments = [a for a in appointments if a.status == AppointmentStatus.CANCELLED]
        cancelled_revenue = len(cancelled_appointments) * avg_appointment_value * 0.5  # 50% can be recovered
        
        # Insurance collection rate
        insurance_verified = sum(1 for a in appointments if a.insurance_verified)
        insurance_collection_rate = (insurance_verified / len(appointments) * 100) if appointments else 0
        
        return {
            'actual_revenue': actual_revenue,
            'potential_revenue': potential_revenue,
            'lost_revenue_no_shows': lost_revenue,
            'lost_revenue_cancellations': cancelled_revenue,
            'total_lost_revenue': lost_revenue + cancelled_revenue,
            'revenue_efficiency': (actual_revenue / potential_revenue * 100) if potential_revenue > 0 else 0,
            'insurance_collection_rate': round(insurance_collection_rate, 2),
            'avg_appointment_value': avg_appointment_value
        }
    
    def get_no_show_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get detailed no-show analytics"""
        appointments = self.db.get_appointments(start_date=start_date, end_date=end_date)
        
        # Overall no-show statistics
        no_show_stats = self.no_show_predictor.calculate_clinic_no_show_rate(start_date, end_date)
        
        # High-risk patients
        high_risk_patients = self.db.get_high_risk_patients()
        
        # No-show patterns by day of week
        no_show_by_day = {}
        for appointment in appointments:
            if appointment.status == AppointmentStatus.NO_SHOW:
                day = appointment.appointment_datetime.strftime('%A')
                no_show_by_day[day] = no_show_by_day.get(day, 0) + 1
        
        # No-show patterns by time of day
        no_show_by_hour = {}
        for appointment in appointments:
            if appointment.status == AppointmentStatus.NO_SHOW:
                hour = appointment.appointment_datetime.hour
                no_show_by_hour[hour] = no_show_by_hour.get(hour, 0) + 1
        
        # Patient no-show history
        patient_no_show_history = {}
        for appointment in appointments:
            if appointment.status == AppointmentStatus.NO_SHOW:
                patient_id = appointment.patient_id
                patient_no_show_history[patient_id] = patient_no_show_history.get(patient_id, 0) + 1
        
        # Top no-show patients
        top_no_show_patients = sorted(patient_no_show_history.items(), 
                                    key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'overall_statistics': no_show_stats,
            'high_risk_patients_count': len(high_risk_patients),
            'no_show_by_day': no_show_by_day,
            'no_show_by_hour': no_show_by_hour,
            'top_no_show_patients': top_no_show_patients,
            'recommendations': self._get_no_show_recommendations(no_show_stats)
        }
    
    def get_patient_analytics(self) -> Dict:
        """Get patient analytics and insights"""
        patients = self.db.get_patients()
        
        # Patient status breakdown
        status_counts = {}
        for status in PatientStatus:
            status_counts[status.value] = sum(1 for p in patients if p.status == status)
        
        # Communication preferences
        communication_preferences = {}
        for patient in patients:
            pref = patient.preferred_communication
            communication_preferences[pref] = communication_preferences.get(pref, 0) + 1
        
        # Insurance status breakdown
        insurance_status_counts = {}
        for patient in patients:
            status = patient.insurance_status.value
            insurance_status_counts[status] = insurance_status_counts.get(status, 0) + 1
        
        # Patient retention analysis
        active_patients = len([p for p in patients if p.status == PatientStatus.ACTIVE])
        high_risk_patients = len([p for p in patients if p.status == PatientStatus.HIGH_RISK])
        
        # New vs returning patients (based on last appointment)
        now = datetime.now()
        new_patients = len([p for p in patients if not p.last_appointment])
        returning_patients = len([p for p in patients if p.last_appointment and 
                                (now - p.last_appointment).days <= 365])
        
        return {
            'total_patients': len(patients),
            'status_breakdown': status_counts,
            'communication_preferences': communication_preferences,
            'insurance_status_breakdown': insurance_status_counts,
            'active_patients': active_patients,
            'high_risk_patients': high_risk_patients,
            'new_patients': new_patients,
            'returning_patients': returning_patients,
            'patient_retention_rate': (returning_patients / len(patients) * 100) if patients else 0
        }
    
    def get_doctor_performance(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get doctor performance analytics"""
        doctors = self.db.get_doctors()
        doctor_performance = {}
        
        for doctor in doctors:
            appointments = self.db.get_appointments(
                doctor_id=doctor.id, start_date=start_date, end_date=end_date
            )
            
            if not appointments:
                continue
            
            # Calculate metrics for this doctor
            total_appointments = len(appointments)
            completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
            no_shows = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
            cancelled = sum(1 for a in appointments if a.status == AppointmentStatus.CANCELLED)
            
            completion_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
            no_show_rate = (no_shows / total_appointments * 100) if total_appointments > 0 else 0
            
            # Revenue generated
            revenue = completed * 150.0  # Average appointment value
            
            doctor_performance[doctor.id] = {
                'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}",
                'specialty': doctor.specialty,
                'total_appointments': total_appointments,
                'completed_appointments': completed,
                'no_shows': no_shows,
                'cancelled': cancelled,
                'completion_rate': round(completion_rate, 2),
                'no_show_rate': round(no_show_rate, 2),
                'revenue_generated': revenue,
                'avg_appointments_per_day': total_appointments / max(1, (end_date - start_date).days)
            }
        
        return doctor_performance
    
    def get_operational_insights(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get operational insights and recommendations"""
        appointments = self.db.get_appointments(start_date=start_date, end_date=end_date)
        
        insights = {
            'peak_hours': self._get_peak_hours(appointments),
            'busiest_days': self._get_busiest_days(appointments),
            'appointment_duration_analysis': self._analyze_appointment_durations(appointments),
            'scheduling_efficiency': self._analyze_scheduling_efficiency(appointments),
            'recommendations': []
        }
        
        # Generate recommendations
        no_show_rate = self.get_appointment_statistics(start_date, end_date)['no_show_rate']
        if no_show_rate > 20:
            insights['recommendations'].append("High no-show rate detected. Consider implementing stricter reminder policies.")
        
        insurance_rate = self.insurance_service.get_insurance_statistics(start_date, end_date)['verification_rate']
        if insurance_rate < 80:
            insights['recommendations'].append("Low insurance verification rate. Implement pre-appointment verification.")
        
        # Check for scheduling inefficiencies
        if insights['scheduling_efficiency']['utilization_rate'] < 70:
            insights['recommendations'].append("Low scheduling utilization. Consider adjusting appointment slots.")
        
        return insights
    
    def _get_peak_hours(self, appointments: List) -> Dict:
        """Get peak appointment hours"""
        hour_counts = {}
        for appointment in appointments:
            hour = appointment.appointment_datetime.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Sort by count and return top 5
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_hours[:5])
    
    def _get_busiest_days(self, appointments: List) -> Dict:
        """Get busiest days of the week"""
        day_counts = {}
        for appointment in appointments:
            day = appointment.appointment_datetime.strftime('%A')
            day_counts[day] = day_counts.get(day, 0) + 1
        
        return day_counts
    
    def _analyze_appointment_durations(self, appointments: List) -> Dict:
        """Analyze appointment duration patterns"""
        durations = [a.duration for a in appointments]
        
        if not durations:
            return {'avg_duration': 0, 'duration_distribution': {}}
        
        avg_duration = sum(durations) / len(durations)
        
        # Duration distribution
        duration_distribution = {}
        for duration in durations:
            duration_distribution[duration] = duration_distribution.get(duration, 0) + 1
        
        return {
            'avg_duration': round(avg_duration, 2),
            'duration_distribution': duration_distribution
        }
    
    def _analyze_scheduling_efficiency(self, appointments: List) -> Dict:
        """Analyze scheduling efficiency"""
        if not appointments:
            return {'utilization_rate': 0, 'efficiency_score': 0}
        
        # Calculate utilization rate (completed vs total scheduled)
        completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
        total_scheduled = len(appointments)
        utilization_rate = (completed / total_scheduled * 100) if total_scheduled > 0 else 0
        
        # Calculate efficiency score (combination of completion rate and low no-show rate)
        no_shows = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
        no_show_rate = (no_shows / total_scheduled * 100) if total_scheduled > 0 else 0
        
        efficiency_score = utilization_rate - (no_show_rate * 0.5)  # Penalize no-shows
        
        return {
            'utilization_rate': round(utilization_rate, 2),
            'efficiency_score': round(max(0, efficiency_score), 2)
        }
    
    def _get_no_show_recommendations(self, no_show_stats: Dict) -> List[str]:
        """Get recommendations to reduce no-shows"""
        recommendations = []
        
        no_show_rate = no_show_stats.get('no_show_rate', 0)
        
        if no_show_rate > 25:
            recommendations.append("Implement automated reminder system with multiple touchpoints")
            recommendations.append("Consider requiring deposits for high-risk patients")
        elif no_show_rate > 15:
            recommendations.append("Increase reminder frequency for appointments")
            recommendations.append("Implement confirmation calls 24 hours before appointments")
        
        if no_show_stats.get('no_shows', 0) > 10:
            recommendations.append("Review and update patient communication preferences")
            recommendations.append("Implement no-show prediction system for proactive intervention")
        
        return recommendations
    
    def generate_monthly_report(self, year: int, month: int) -> Dict:
        """Generate comprehensive monthly report"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        return {
            'report_period': f"{start_date.strftime('%B %Y')}",
            'dashboard_data': self.generate_clinic_dashboard(start_date, end_date),
            'key_metrics': self._extract_key_metrics(start_date, end_date),
            'trend_analysis': self._analyze_trends(start_date, end_date),
            'action_items': self._generate_action_items(start_date, end_date)
        }
    
    def _extract_key_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Extract key performance metrics"""
        appointment_stats = self.get_appointment_statistics(start_date, end_date)
        revenue_stats = self.get_revenue_analytics(start_date, end_date)
        no_show_stats = self.get_no_show_analytics(start_date, end_date)
        
        return {
            'total_appointments': appointment_stats['total_appointments'],
            'completion_rate': appointment_stats['completion_rate'],
            'no_show_rate': appointment_stats['no_show_rate'],
            'revenue_efficiency': revenue_stats['revenue_efficiency'],
            'total_revenue': revenue_stats['actual_revenue'],
            'lost_revenue': revenue_stats['total_lost_revenue'],
            'high_risk_patients': no_show_stats['high_risk_patients_count']
        }
    
    def _analyze_trends(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze trends over time"""
        # This would typically compare with previous periods
        # For now, return basic trend indicators
        return {
            'appointment_volume_trend': 'stable',  # Would be calculated from historical data
            'no_show_trend': 'decreasing',  # Would be calculated from historical data
            'revenue_trend': 'increasing'  # Would be calculated from historical data
        }
    
    def _generate_action_items(self, start_date: datetime, end_date: datetime) -> List[str]:
        """Generate actionable recommendations"""
        action_items = []
        
        appointment_stats = self.get_appointment_statistics(start_date, end_date)
        revenue_stats = self.get_revenue_analytics(start_date, end_date)
        
        if appointment_stats['no_show_rate'] > 20:
            action_items.append("Implement automated reminder system")
            action_items.append("Review and update patient communication preferences")
        
        if revenue_stats['revenue_efficiency'] < 80:
            action_items.append("Improve insurance verification process")
            action_items.append("Implement pre-appointment payment collection")
        
        if appointment_stats['cancellation_rate'] > 15:
            action_items.append("Review cancellation policies")
            action_items.append("Implement cancellation fees for last-minute cancellations")
        
        return action_items
