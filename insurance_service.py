"""
Insurance Verification and Collection Automation Service for the Medical Appointment Scheduling AI Agent
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from models import Patient, Appointment, InsuranceStatus
from database import MedicalDatabase


class InsuranceService:
    """Insurance verification and collection automation service"""
    
    def __init__(self, database: MedicalDatabase):
        self.db = database
        
        # Insurance provider patterns for validation
        self.insurance_patterns = {
            'medicare': r'^[0-9]{3}-[0-9]{2}-[0-9]{4}$',
            'medicaid': r'^[A-Z]{2}[0-9]{8}$',
            'blue_cross': r'^[A-Z]{3}[0-9]{6}$',
            'aetna': r'^[0-9]{9}$',
            'cigna': r'^[0-9]{10}$',
            'humana': r'^[0-9]{9}$',
            'kaiser': r'^[0-9]{10}$',
            'united_healthcare': r'^[0-9]{9}$'
        }
        
        # Insurance coverage verification (simulated)
        self.coverage_database = {
            'medicare': {'active': True, 'copay': 20, 'deductible': 0},
            'medicaid': {'active': True, 'copay': 0, 'deductible': 0},
            'blue_cross': {'active': True, 'copay': 25, 'deductible': 500},
            'aetna': {'active': True, 'copay': 30, 'deductible': 1000},
            'cigna': {'active': True, 'copay': 25, 'deductible': 750},
            'humana': {'active': True, 'copay': 20, 'deductible': 500},
            'kaiser': {'active': True, 'copay': 15, 'deductible': 0},
            'united_healthcare': {'active': True, 'copay': 30, 'deductible': 1000}
        }
    
    def verify_insurance(self, patient_id: str, appointment_id: str) -> Dict:
        """Verify patient's insurance coverage"""
        patient = self.db.get_patient(patient_id)
        appointment = self.db.get_appointment(appointment_id)
        
        if not patient or not appointment:
            return {'status': 'error', 'message': 'Patient or appointment not found'}
        
        # Validate insurance number format
        validation_result = self._validate_insurance_number(
            patient.insurance_provider, patient.insurance_number
        )
        
        if not validation_result['valid']:
            return {
                'status': 'invalid',
                'message': validation_result['message'],
                'insurance_status': InsuranceStatus.INVALID
            }
        
        # Check coverage in simulated database
        coverage_info = self._check_coverage(patient.insurance_provider, patient.insurance_number)
        
        if not coverage_info['active']:
            return {
                'status': 'expired',
                'message': 'Insurance coverage is not active',
                'insurance_status': InsuranceStatus.EXPIRED
            }
        
        # Update patient's insurance status
        patient.insurance_status = InsuranceStatus.VERIFIED
        self.db.update_patient(patient)
        
        # Update appointment insurance verification
        appointment.insurance_verified = True
        appointment.updated_at = datetime.now()
        self.db.update_appointment(appointment)
        
        return {
            'status': 'verified',
            'message': 'Insurance verified successfully',
            'insurance_status': InsuranceStatus.VERIFIED,
            'coverage_info': coverage_info
        }
    
    def _validate_insurance_number(self, provider: str, insurance_number: str) -> Dict:
        """Validate insurance number format"""
        provider_lower = provider.lower().replace(' ', '_')
        
        # Check if provider pattern exists
        if provider_lower not in self.insurance_patterns:
            return {
                'valid': False,
                'message': f'Unknown insurance provider: {provider}'
            }
        
        # Validate format
        pattern = self.insurance_patterns[provider_lower]
        if not re.match(pattern, insurance_number):
            return {
                'valid': False,
                'message': f'Invalid insurance number format for {provider}'
            }
        
        return {'valid': True, 'message': 'Insurance number format is valid'}
    
    def _check_coverage(self, provider: str, insurance_number: str) -> Dict:
        """Check insurance coverage (simulated)"""
        provider_lower = provider.lower().replace(' ', '_')
        
        # Simulate coverage check
        if provider_lower in self.coverage_database:
            coverage = self.coverage_database[provider_lower].copy()
            
            # Simulate some coverage issues based on insurance number
            if insurance_number.endswith('0'):
                coverage['active'] = False
                coverage['reason'] = 'Policy suspended'
            elif insurance_number.endswith('1'):
                coverage['copay'] *= 2  # Higher copay
                coverage['note'] = 'High-deductible plan'
            
            return coverage
        else:
            return {
                'active': False,
                'copay': 0,
                'deductible': 0,
                'reason': 'Provider not found in system'
            }
    
    def calculate_patient_responsibility(self, patient_id: str, appointment_id: str, 
                                       service_cost: float = 150.0) -> Dict:
        """Calculate patient's financial responsibility"""
        patient = self.db.get_patient(patient_id)
        appointment = self.db.get_appointment(appointment_id)
        
        if not patient or not appointment:
            return {'error': 'Patient or appointment not found'}
        
        # Verify insurance first
        insurance_verification = self.verify_insurance(patient_id, appointment_id)
        
        if insurance_verification['status'] != 'verified':
            return {
                'total_cost': service_cost,
                'insurance_coverage': 0,
                'patient_responsibility': service_cost,
                'payment_required': True,
                'insurance_status': insurance_verification['status'],
                'message': 'Insurance not verified - full payment required'
            }
        
        coverage_info = insurance_verification['coverage_info']
        
        # Calculate patient responsibility
        copay = coverage_info.get('copay', 0)
        deductible = coverage_info.get('deductible', 0)
        
        # Simulate deductible tracking (in real system, this would be persistent)
        remaining_deductible = max(0, deductible - 200)  # Assume some deductible already met
        
        if remaining_deductible > 0:
            # Patient pays deductible amount or service cost, whichever is less
            deductible_payment = min(remaining_deductible, service_cost)
            copay_payment = 0
        else:
            # Deductible met, patient pays copay
            deductible_payment = 0
            copay_payment = min(copay, service_cost)
        
        patient_responsibility = deductible_payment + copay_payment
        insurance_coverage = service_cost - patient_responsibility
        
        return {
            'total_cost': service_cost,
            'insurance_coverage': insurance_coverage,
            'patient_responsibility': patient_responsibility,
            'copay': copay_payment,
            'deductible': deductible_payment,
            'remaining_deductible': max(0, remaining_deductible - deductible_payment),
            'payment_required': patient_responsibility > 0,
            'insurance_status': 'verified',
            'message': 'Insurance verified - payment calculated'
        }
    
    def get_payment_options(self, patient_id: str, amount: float) -> List[Dict]:
        """Get available payment options for patient"""
        patient = self.db.get_patient(patient_id)
        
        if not patient:
            return []
        
        payment_options = []
        
        # Insurance coverage
        if patient.insurance_status == InsuranceStatus.VERIFIED:
            payment_options.append({
                'type': 'insurance',
                'description': 'Insurance coverage',
                'amount': 0,
                'available': True
            })
        
        # Cash payment
        payment_options.append({
            'type': 'cash',
            'description': 'Cash payment',
            'amount': amount,
            'available': True
        })
        
        # Credit card
        payment_options.append({
            'type': 'credit_card',
            'description': 'Credit card payment',
            'amount': amount,
            'available': True
        })
        
        # Payment plan (for amounts over $100)
        if amount > 100:
            payment_options.append({
                'type': 'payment_plan',
                'description': 'Payment plan (3 installments)',
                'amount': amount / 3,
                'available': True,
                'installments': 3
            })
        
        # Financial assistance (for high amounts)
        if amount > 500:
            payment_options.append({
                'type': 'financial_assistance',
                'description': 'Financial assistance program',
                'amount': amount * 0.5,  # 50% reduction
                'available': True,
                'requires_application': True
            })
        
        return payment_options
    
    def process_payment(self, patient_id: str, appointment_id: str, 
                       payment_type: str, amount: float, 
                       payment_details: Dict = None) -> Dict:
        """Process payment for appointment"""
        patient = self.db.get_patient(patient_id)
        appointment = self.db.get_appointment(appointment_id)
        
        if not patient or not appointment:
            return {'status': 'error', 'message': 'Patient or appointment not found'}
        
        # Validate payment amount
        financial_info = self.calculate_patient_responsibility(patient_id, appointment_id)
        required_amount = financial_info.get('patient_responsibility', 0)
        
        if amount < required_amount:
            return {
                'status': 'error',
                'message': f'Insufficient payment. Required: ${required_amount:.2f}, Provided: ${amount:.2f}'
            }
        
        # Process payment based on type
        if payment_type == 'cash':
            return self._process_cash_payment(patient, appointment, amount)
        elif payment_type == 'credit_card':
            return self._process_credit_card_payment(patient, appointment, amount, payment_details)
        elif payment_type == 'insurance':
            return self._process_insurance_payment(patient, appointment)
        elif payment_type == 'payment_plan':
            return self._process_payment_plan(patient, appointment, amount, payment_details)
        else:
            return {'status': 'error', 'message': 'Invalid payment type'}
    
    def _process_cash_payment(self, patient: Patient, appointment: Appointment, amount: float) -> Dict:
        """Process cash payment"""
        # Simulate cash payment processing
        print(f"Cash payment of ${amount:.2f} received from {patient.first_name} {patient.last_name}")
        
        return {
            'status': 'success',
            'message': 'Cash payment processed successfully',
            'payment_id': f'CASH_{appointment.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': amount,
            'payment_type': 'cash'
        }
    
    def _process_credit_card_payment(self, patient: Patient, appointment: Appointment, 
                                   amount: float, payment_details: Dict) -> Dict:
        """Process credit card payment"""
        if not payment_details or 'card_number' not in payment_details:
            return {'status': 'error', 'message': 'Credit card details required'}
        
        # Simulate credit card processing
        card_number = payment_details['card_number']
        if not re.match(r'^[0-9]{16}$', card_number.replace(' ', '')):
            return {'status': 'error', 'message': 'Invalid credit card number'}
        
        print(f"Credit card payment of ${amount:.2f} processed for {patient.first_name} {patient.last_name}")
        
        return {
            'status': 'success',
            'message': 'Credit card payment processed successfully',
            'payment_id': f'CC_{appointment.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': amount,
            'payment_type': 'credit_card',
            'last_four': card_number[-4:]
        }
    
    def _process_insurance_payment(self, patient: Patient, appointment: Appointment) -> Dict:
        """Process insurance payment"""
        if patient.insurance_status != InsuranceStatus.VERIFIED:
            return {'status': 'error', 'message': 'Insurance not verified'}
        
        # Simulate insurance claim submission
        print(f"Insurance claim submitted for {patient.first_name} {patient.last_name}")
        
        return {
            'status': 'success',
            'message': 'Insurance claim submitted successfully',
            'payment_id': f'INS_{appointment.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': 0,
            'payment_type': 'insurance'
        }
    
    def _process_payment_plan(self, patient: Patient, appointment: Appointment, 
                            amount: float, payment_details: Dict) -> Dict:
        """Process payment plan setup"""
        if not payment_details or 'installments' not in payment_details:
            return {'status': 'error', 'message': 'Payment plan details required'}
        
        installments = payment_details['installments']
        installment_amount = amount / installments
        
        print(f"Payment plan set up for {patient.first_name} {patient.last_name}: {installments} installments of ${installment_amount:.2f}")
        
        return {
            'status': 'success',
            'message': f'Payment plan set up: {installments} installments of ${installment_amount:.2f}',
            'payment_id': f'PLAN_{appointment.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': installment_amount,
            'payment_type': 'payment_plan',
            'installments': installments
        }
    
    def get_insurance_statistics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get insurance-related statistics"""
        appointments = self.db.get_appointments(start_date=start_date, end_date=end_date)
        
        total_appointments = len(appointments)
        verified_insurance = sum(1 for a in appointments if a.insurance_verified)
        unverified_insurance = total_appointments - verified_insurance
        
        # Calculate potential revenue impact
        avg_appointment_value = 150.0
        potential_revenue_loss = unverified_insurance * avg_appointment_value * 0.3  # 30% collection rate for unverified
        
        return {
            'total_appointments': total_appointments,
            'verified_insurance': verified_insurance,
            'unverified_insurance': unverified_insurance,
            'verification_rate': (verified_insurance / total_appointments * 100) if total_appointments > 0 else 0,
            'potential_revenue_loss': potential_revenue_loss,
            'recommendation': 'Increase insurance verification before appointments' if unverified_insurance > total_appointments * 0.2 else 'Insurance verification rate is good'
        }
    
    def get_patients_needing_insurance_verification(self) -> List[Patient]:
        """Get patients with unverified insurance"""
        patients = self.db.get_patients()
        return [p for p in patients if p.insurance_status != InsuranceStatus.VERIFIED]
    
    def batch_verify_insurance(self, patient_ids: List[str]) -> Dict:
        """Batch verify insurance for multiple patients"""
        results = {
            'total_processed': len(patient_ids),
            'verified': 0,
            'failed': 0,
            'errors': []
        }
        
        for patient_id in patient_ids:
            try:
                patient = self.db.get_patient(patient_id)
                if not patient:
                    results['errors'].append(f'Patient {patient_id} not found')
                    results['failed'] += 1
                    continue
                
                # Get next appointment for verification
                appointments = self.db.get_appointments(patient_id=patient_id)
                upcoming_appointments = [a for a in appointments 
                                       if a.appointment_datetime > datetime.now() 
                                       and a.status.value in ['scheduled', 'confirmed']]
                
                if not upcoming_appointments:
                    results['errors'].append(f'No upcoming appointments for patient {patient_id}')
                    results['failed'] += 1
                    continue
                
                next_appointment = min(upcoming_appointments, key=lambda x: x.appointment_datetime)
                verification_result = self.verify_insurance(patient_id, next_appointment.id)
                
                if verification_result['status'] == 'verified':
                    results['verified'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f'Verification failed for patient {patient_id}: {verification_result["message"]}')
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f'Error processing patient {patient_id}: {str(e)}')
        
        return results
