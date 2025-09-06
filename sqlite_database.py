"""
SQLite Database for the Medical Appointment Scheduling AI Agent
Replaces the JSON-based database with SQLite for better performance and reliability
"""
import sqlite3
import random
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Any
import os


class SQLiteMedicalDatabase:
    """SQLite-based database for the medical appointment system"""
    
    def __init__(self, db_path: str = "patients.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create patients table as specified in requirements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                last_visit_date DATE,
                visits_count INTEGER DEFAULT 1
            )
        ''')
        
        # Create appointments table for scheduling functionality
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id TEXT,
                appointment_datetime DATETIME,
                status TEXT DEFAULT 'scheduled',
                appointment_type TEXT DEFAULT 'general',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        ''')
        
        # Create doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                specialty TEXT,
                phone TEXT,
                email TEXT,
                working_hours TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create clinic_settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clinic_settings (
                id INTEGER PRIMARY KEY,
                clinic_name TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                timezone TEXT DEFAULT 'Asia/Kolkata'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_synthetic_patients(self, count: int = 50):
        """Generate 50 synthetic patient records as specified"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Indian names for realistic data
        first_names = [
            "Aarav", "Aditya", "Akshay", "Aman", "Ankit", "Arjun", "Bharat", "Chirag", "Deepak", "Gaurav",
            "Harsh", "Ishaan", "Jatin", "Karan", "Laksh", "Manish", "Nikhil", "Omkar", "Pranav", "Rahul",
            "Rajesh", "Sahil", "Tarun", "Uday", "Vikram", "Yash", "Zubin",
            "Aanya", "Bhavya", "Chitra", "Deepika", "Esha", "Fatima", "Gayatri", "Hema", "Isha", "Jaya",
            "Kavya", "Lakshmi", "Meera", "Neha", "Priya", "Radha", "Sakshi", "Tara", "Uma", "Vidya", "Yamini"
        ]
        
        last_names = [
            "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Agarwal", "Jain", "Malhotra", "Reddy",
            "Nair", "Iyer", "Menon", "Pillai", "Rao", "Choudhary", "Mishra", "Tiwari", "Yadav", "Pandey",
            "Joshi", "Bhatt", "Mehta", "Gandhi", "Kapoor", "Khanna", "Saxena", "Agarwal", "Bansal", "Goel"
        ]
        
        # Clear existing patients
        cursor.execute("DELETE FROM patients")
        
        # Generate synthetic patients
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Random last visit date within past 2 years
            days_ago = random.randint(1, 730)  # 2 years = 730 days
            last_visit = date.today() - timedelta(days=days_ago)
            
            # Random visits count between 1 and 5
            visits_count = random.randint(1, 5)
            
            cursor.execute('''
                INSERT INTO patients (name, last_visit_date, visits_count)
                VALUES (?, ?, ?)
            ''', (name, last_visit, visits_count))
        
        conn.commit()
        conn.close()
        print(f"✅ Generated {count} synthetic patient records")
    
    def search_patients(self, name: str = None, patient_id: int = None) -> List[Dict]:
        """Search patients by name or ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if patient_id:
            cursor.execute('''
                SELECT patient_id, name, last_visit_date, visits_count
                FROM patients WHERE patient_id = ?
            ''', (patient_id,))
        elif name:
            cursor.execute('''
                SELECT patient_id, name, last_visit_date, visits_count
                FROM patients WHERE name LIKE ?
            ''', (f'%{name}%',))
        else:
            cursor.execute('''
                SELECT patient_id, name, last_visit_date, visits_count
                FROM patients ORDER BY name
            ''')
        
        results = []
        for row in cursor.fetchall():
            patient_data = {
                'patient_id': row[0],
                'name': row[1],
                'last_visit_date': row[2],
                'visits_count': row[3],
                'patient_type': 'new' if row[3] == 1 else 'returning'
            }
            results.append(patient_data)
        
        conn.close()
        return results
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Dict]:
        """Get patient by ID"""
        results = self.search_patients(patient_id=patient_id)
        return results[0] if results else None
    
    def add_patient(self, name: str, last_visit_date: date = None, visits_count: int = 1) -> int:
        """Add a new patient"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if last_visit_date is None:
            last_visit_date = date.today()
        
        cursor.execute('''
            INSERT INTO patients (name, last_visit_date, visits_count)
            VALUES (?, ?, ?)
        ''', (name, last_visit_date, visits_count))
        
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return patient_id
    
    def update_patient_visit(self, patient_id: int):
        """Update patient's visit count and last visit date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE patients 
            SET visits_count = visits_count + 1, last_visit_date = ?
            WHERE patient_id = ?
        ''', (date.today(), patient_id))
        
        conn.commit()
        conn.close()
    
    def get_all_patients(self) -> List[Dict]:
        """Get all patients"""
        return self.search_patients()
    
    def get_patient_statistics(self) -> Dict:
        """Get patient statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total patients
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]
        
        # New patients (visits_count = 1)
        cursor.execute("SELECT COUNT(*) FROM patients WHERE visits_count = 1")
        new_patients = cursor.fetchone()[0]
        
        # Returning patients (visits_count > 1)
        cursor.execute("SELECT COUNT(*) FROM patients WHERE visits_count > 1")
        returning_patients = cursor.fetchone()[0]
        
        # Average visits
        cursor.execute("SELECT AVG(visits_count) FROM patients")
        avg_visits = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_patients': total_patients,
            'new_patients': new_patients,
            'returning_patients': returning_patients,
            'average_visits': round(avg_visits, 2)
        }
    
    def add_doctor(self, doctor_id: str, first_name: str, last_name: str, 
                   specialty: str, phone: str, email: str, working_hours: str) -> bool:
        """Add a doctor"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO doctors 
                (doctor_id, first_name, last_name, specialty, phone, email, working_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doctor_id, first_name, last_name, specialty, phone, email, working_hours))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    def get_doctors(self) -> List[Dict]:
        """Get all doctors"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT doctor_id, first_name, last_name, specialty, phone, email, working_hours
            FROM doctors WHERE is_active = 1
        ''')
        
        doctors = []
        for row in cursor.fetchall():
            doctor = {
                'doctor_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'specialty': row[3],
                'phone': row[4],
                'email': row[5],
                'working_hours': row[6]
            }
            doctors.append(doctor)
        
        conn.close()
        return doctors
    
    def add_appointment(self, patient_id: int, doctor_id: str, appointment_datetime: datetime,
                       appointment_type: str = "general", notes: str = "") -> int:
        """Add an appointment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments 
            (patient_id, doctor_id, appointment_datetime, appointment_type, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, appointment_datetime, appointment_type, notes))
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return appointment_id
    
    def get_appointments(self, patient_id: int = None, doctor_id: str = None) -> List[Dict]:
        """Get appointments"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT a.appointment_id, a.patient_id, p.name, a.doctor_id, 
                   a.appointment_datetime, a.status, a.appointment_type, a.notes
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
        '''
        
        params = []
        if patient_id:
            query += " WHERE a.patient_id = ?"
            params.append(patient_id)
        elif doctor_id:
            query += " WHERE a.doctor_id = ?"
            params.append(doctor_id)
        
        query += " ORDER BY a.appointment_datetime"
        
        cursor.execute(query, params)
        
        appointments = []
        for row in cursor.fetchall():
            appointment = {
                'appointment_id': row[0],
                'patient_id': row[1],
                'patient_name': row[2],
                'doctor_id': row[3],
                'appointment_datetime': row[4],
                'status': row[5],
                'appointment_type': row[6],
                'notes': row[7]
            }
            appointments.append(appointment)
        
        conn.close()
        return appointments
    
    def update_clinic_settings(self, clinic_name: str, address: str, phone: str, email: str, timezone: str = "Asia/Kolkata"):
        """Update clinic settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO clinic_settings 
            (id, clinic_name, address, phone, email, timezone)
            VALUES (1, ?, ?, ?, ?, ?)
        ''', (clinic_name, address, phone, email, timezone))
        
        conn.commit()
        conn.close()
    
    def get_clinic_settings(self) -> Optional[Dict]:
        """Get clinic settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT clinic_name, address, phone, email, timezone
            FROM clinic_settings WHERE id = 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'clinic_name': row[0],
                'address': row[1],
                'phone': row[2],
                'email': row[3],
                'timezone': row[4]
            }
        return None
