"""
Configuration settings for the Medical Appointment Scheduling AI Agent
"""
import os
from typing import Dict, Any
from models import ClinicSettings


class Config:
    """Configuration class for MedAssist AI"""
    
    # Database settings
    DATABASE_DIR = os.getenv("DATABASE_DIR", "data")
    DATABASE_BACKUP_ENABLED = os.getenv("DATABASE_BACKUP_ENABLED", "true").lower() == "true"
    DATABASE_BACKUP_INTERVAL_HOURS = int(os.getenv("DATABASE_BACKUP_INTERVAL_HOURS", "24"))
    
    # AI Agent settings
    AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.0-flash")
    AGENT_NAME = os.getenv("AGENT_NAME", "medassist_ai_agent")
    
    # Notification settings
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMS_ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"
    PHONE_CALLS_ENABLED = os.getenv("PHONE_CALLS_ENABLED", "false").lower() == "true"
    
    # Email configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "originalgangstar9963@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # SMS configuration (Twilio)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Reminder settings
    DEFAULT_REMINDER_HOURS = int(os.getenv("DEFAULT_REMINDER_HOURS", "24"))
    DEFAULT_CONFIRMATION_HOURS = int(os.getenv("DEFAULT_CONFIRMATION_HOURS", "2"))
    MAX_REMINDER_ATTEMPTS = int(os.getenv("MAX_REMINDER_ATTEMPTS", "3"))
    
    # No-show prediction settings
    NO_SHOW_RISK_THRESHOLD = float(os.getenv("NO_SHOW_RISK_THRESHOLD", "0.6"))
    HIGH_RISK_PATIENT_THRESHOLD = int(os.getenv("HIGH_RISK_PATIENT_THRESHOLD", "3"))
    
    # Insurance verification settings
    INSURANCE_VERIFICATION_REQUIRED = os.getenv("INSURANCE_VERIFICATION_REQUIRED", "true").lower() == "true"
    AUTO_VERIFY_INSURANCE = os.getenv("AUTO_VERIFY_INSURANCE", "true").lower() == "true"
    
    # Analytics settings
    ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "365"))
    REPORT_GENERATION_ENABLED = os.getenv("REPORT_GENERATION_ENABLED", "true").lower() == "true"
    
    # Security settings
    ENCRYPT_PATIENT_DATA = os.getenv("ENCRYPT_PATIENT_DATA", "false").lower() == "true"
    AUDIT_LOG_ENABLED = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"
    
    # Performance settings
    MAX_CONCURRENT_OPERATIONS = int(os.getenv("MAX_CONCURRENT_OPERATIONS", "10"))
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/medassist.log")
    LOG_MAX_SIZE_MB = int(os.getenv("LOG_MAX_SIZE_MB", "10"))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    @classmethod
    def get_default_clinic_settings(cls) -> ClinicSettings:
        """Get default clinic settings"""
        return ClinicSettings(
            clinic_name=os.getenv("CLINIC_NAME", "MedAssist Medical Clinic"),
            address=os.getenv("CLINIC_ADDRESS", "123 Medical Drive, Healthcare City, HC 12345"),
            phone=os.getenv("CLINIC_PHONE", "(555) 123-4567"),
            email=os.getenv("CLINIC_EMAIL", "originalgangstar9963@gmail.com"),
            timezone=os.getenv("CLINIC_TIMEZONE", "Asia/Kolkata"),
            reminder_hours_before=cls.DEFAULT_REMINDER_HOURS,
            confirmation_hours_before=cls.DEFAULT_CONFIRMATION_HOURS,
            no_show_threshold=cls.HIGH_RISK_PATIENT_THRESHOLD,
            auto_reschedule_enabled=os.getenv("AUTO_RESCHEDULE_ENABLED", "true").lower() == "true",
            insurance_verification_required=cls.INSURANCE_VERIFICATION_REQUIRED,
            cancellation_policy_hours=int(os.getenv("CANCELLATION_POLICY_HOURS", "24"))
        )
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return any issues"""
        issues = []
        warnings = []
        
        # Check required settings for email
        if cls.EMAIL_ENABLED:
            if not cls.SMTP_USERNAME or not cls.SMTP_PASSWORD:
                issues.append("Email enabled but SMTP credentials not configured")
        
        # Check required settings for SMS
        if cls.SMS_ENABLED:
            if not cls.TWILIO_ACCOUNT_SID or not cls.TWILIO_AUTH_TOKEN:
                issues.append("SMS enabled but Twilio credentials not configured")
        
        # Check database directory
        if not os.path.exists(cls.DATABASE_DIR):
            try:
                os.makedirs(cls.DATABASE_DIR, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create database directory: {e}")
        
        # Check log directory
        log_dir = os.path.dirname(cls.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                warnings.append(f"Cannot create log directory: {e}")
        
        # Validate numeric settings
        if cls.DEFAULT_REMINDER_HOURS < 1 or cls.DEFAULT_REMINDER_HOURS > 168:  # 1 hour to 1 week
            issues.append("DEFAULT_REMINDER_HOURS must be between 1 and 168")
        
        if cls.NO_SHOW_RISK_THRESHOLD < 0 or cls.NO_SHOW_RISK_THRESHOLD > 1:
            issues.append("NO_SHOW_RISK_THRESHOLD must be between 0 and 1")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    @classmethod
    def get_environment_info(cls) -> Dict[str, Any]:
        """Get environment information for debugging"""
        import sys
        return {
            "python_version": sys.version,
            "database_dir": cls.DATABASE_DIR,
            "email_enabled": cls.EMAIL_ENABLED,
            "sms_enabled": cls.SMS_ENABLED,
            "phone_calls_enabled": cls.PHONE_CALLS_ENABLED,
            "agent_model": cls.AGENT_MODEL,
            "log_level": cls.LOG_LEVEL,
            "cache_enabled": cls.CACHE_ENABLED
        }


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    LOG_LEVEL = "DEBUG"
    CACHE_ENABLED = False
    AUDIT_LOG_ENABLED = True


class ProductionConfig(Config):
    """Production environment configuration"""
    LOG_LEVEL = "WARNING"
    CACHE_ENABLED = True
    AUDIT_LOG_ENABLED = True
    ENCRYPT_PATIENT_DATA = True


class TestingConfig(Config):
    """Testing environment configuration"""
    DATABASE_DIR = "test_data"
    LOG_LEVEL = "ERROR"
    CACHE_ENABLED = False
    EMAIL_ENABLED = False
    SMS_ENABLED = False
    PHONE_CALLS_ENABLED = False


# Configuration factory
def get_config(environment: str = None) -> Config:
    """Get configuration based on environment"""
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    return config_map.get(environment, DevelopmentConfig)
