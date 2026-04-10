"""
i18n.py — English language support for NagarAI.

All translations in English for international hackathon demo.
"""

from typing import Dict


DEFAULT_LANG = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App Identity
    "app_name": {"en": "NagarAI", "bn": "NagarAI"},
    "app_tagline": {"en": "One App, Two Services", "bn": "One App, Two Services"},
    "app_subtitle": {"en": "AI-Powered Civic Service Platform", "bn": "AI-Powered Civic Service Platform"},

    # Landing Page
    "welcome": {"en": "Welcome", "bn": "Welcome"},
    "choose_service": {"en": "Choose Your Service Type", "bn": "Choose Your Service Type"},
    "govt_service": {"en": "Government Service", "bn": "Government Service"},
    "govt_service_desc": {"en": "Trade License, Passport, Birth Certificate — Apply faster with AI", "bn": "Trade License, Passport, Birth Certificate — Apply faster with AI"},
    "social_service": {"en": "Social Service", "bn": "Social Service"},
    "social_service_desc": {"en": "Emergency Services — Find nearest hospitals, pharmacies without login", "bn": "Emergency Services — Find nearest hospitals, pharmacies without login"},
    "view_heatmap": {"en": "Feedback Heatmap", "bn": "Feedback Heatmap"},
    "view_heatmap_desc": {"en": "View service demand and satisfaction data", "bn": "View service demand and satisfaction data"},

    # Government Service Page
    "govt_service_title": {"en": "Government Service Application", "bn": "Government Service Application"},
    "enter_query": {"en": "Describe the service you need", "bn": "Describe the service you need"},
    "query_placeholder": {"en": "e.g., I need a trade license", "bn": "e.g., I need a trade license"},
    "intent_detected": {"en": "Service Detected", "bn": "Service Detected"},
    "intent_not_detected": {"en": "Service Not Detected", "bn": "Service Not Detected"},
    "try_again": {"en": "Try Again", "bn": "Try Again"},
    "fill_form": {"en": "Fill the Form", "bn": "Fill the Form"},
    "submit": {"en": "Submit", "bn": "Submit"},
    "next_step": {"en": "Next Step", "bn": "Next Step"},
    "all_complete": {"en": "All information complete ✅", "bn": "All information complete ✅"},

    # Form Fields
    "full_name": {"en": "Full Name", "bn": "Full Name"},
    "nid_number": {"en": "National ID Number", "bn": "National ID Number"},
    "phone_number": {"en": "Mobile Number", "bn": "Mobile Number"},
    "email": {"en": "Email", "bn": "Email"},
    "address": {"en": "Address", "bn": "Address"},
    "date_of_birth": {"en": "Date of Birth", "bn": "Date of Birth"},

    # Payment
    "payment": {"en": "Payment", "bn": "Payment"},
    "fee": {"en": "Fee", "bn": "Fee"},
    "free": {"en": "Free", "bn": "Free"},
    "pay_now": {"en": "Pay Now", "bn": "Pay Now"},
    "payment_processing": {"en": "Payment Processing...", "bn": "Payment Processing..."},
    "payment_success": {"en": "Payment Successful ✅", "bn": "Payment Successful ✅"},
    "payment_failed": {"en": "Payment Failed ❌", "bn": "Payment Failed ❌"},
    "receipt": {"en": "Receipt", "bn": "Receipt"},
    "transaction_id": {"en": "Transaction ID", "bn": "Transaction ID"},
    "receipt_number": {"en": "Receipt Number", "bn": "Receipt Number"},
    "amount": {"en": "Amount", "bn": "Amount"},
    "sms_confirmation": {"en": "SMS Confirmation Sent", "bn": "SMS Confirmation Sent"},

    # Appointment
    "appointment": {"en": "Appointment", "bn": "Appointment"},
    "select_date": {"en": "Select Date", "bn": "Select Date"},
    "select_time": {"en": "Select Time", "bn": "Select Time"},
    "book_appointment": {"en": "Book Appointment", "bn": "Book Appointment"},
    "appointment_confirmed": {"en": "Appointment Confirmed", "bn": "Appointment Confirmed"},
    "reference": {"en": "Reference", "bn": "Reference"},
    "no_slots": {"en": "No Available Slots", "bn": "No Available Slots"},

    # Social Service Page
    "social_service_title": {"en": "Emergency Social Service", "bn": "Emergency Social Service"},
    "no_login_needed": {"en": "No Login Required", "bn": "No Login Required"},
    "emergency": {"en": "Emergency", "bn": "Emergency"},
    "nearest_hospitals": {"en": "Nearest Hospitals", "bn": "Nearest Hospitals"},
    "nearest_pharmacies": {"en": "Nearest Pharmacies", "bn": "Nearest Pharmacies"},
    "nearest_police": {"en": "Nearest Police Stations", "bn": "Nearest Police Stations"},
    "distance": {"en": "Distance", "bn": "Distance"},
    "km": {"en": "km", "bn": "km"},
    "call": {"en": "Call", "bn": "Call"},
    "beds_available": {"en": "Beds Available", "bn": "Beds Available"},
    "open_24h": {"en": "Open 24 Hours", "bn": "Open 24 Hours"},
    "enter_location": {"en": "Enter Your Location", "bn": "Enter Your Location"},
    "demo_location": {"en": "Use Demo Location", "bn": "Use Demo Location"},
    "emergency_contacts": {"en": "Emergency Contacts", "bn": "Emergency Contacts"},
    "national_emergency": {"en": "National Emergency", "bn": "National Emergency"},
    "fire_service": {"en": "Fire Service", "bn": "Fire Service"},
    "ambulance": {"en": "Ambulance", "bn": "Ambulance"},

    # Heatmap Page
    "heatmap_title": {"en": "Service Feedback Heatmap", "bn": "Service Feedback Heatmap"},
    "service_demand": {"en": "Service Demand", "bn": "Service Demand"},
    "satisfaction": {"en": "Satisfaction", "bn": "Satisfaction"},
    "positive": {"en": "Positive", "bn": "Positive"},
    "neutral": {"en": "Neutral", "bn": "Neutral"},
    "negative": {"en": "Negative", "bn": "Negative"},
    "applications": {"en": "Applications", "bn": "Applications"},
    "peak_area": {"en": "Peak Demand Area", "bn": "Peak Demand Area"},
    "nagarai_impact": {"en": "NagarAI Impact", "bn": "NagarAI Impact"},
    "users_served": {"en": "Users Served", "bn": "Users Served"},
    "time_saved": {"en": "Time Saved", "bn": "Time Saved"},
    "success_rate": {"en": "Success Rate", "bn": "Success Rate"},
    "minutes": {"en": "minutes", "bn": "minutes"},
    "improvement": {"en": "Improvement", "bn": "Improvement"},
    "demo_data_label": {"en": "Demo Data", "bn": "Demo Data"},

    # Security
    "security_notice": {
        "en": "🔒 Your data is completely secure. No personal information is stored.",
        "bn": "🔒 Your data is completely secure. No personal information is stored."
    },
    "pii_redacted": {"en": "Personal information redacted", "bn": "Personal information redacted"},
    "session_active": {"en": "Active Session", "bn": "Active Session"},
    "session_expires": {"en": "Session Expires", "bn": "Session Expires"},

    # Validation Messages
    "error_name_required": {"en": "Name is required", "bn": "Name is required"},
    "error_name_short": {"en": "Name must be at least 3 characters", "bn": "Name must be at least 3 characters"},
    "error_phone_invalid": {"en": "Enter a valid 11-digit phone number", "bn": "Enter a valid 11-digit phone number"},
    "error_nid_invalid": {"en": "Enter a valid National ID number", "bn": "Enter a valid National ID number"},
    "error_email_invalid": {"en": "Enter a valid email address", "bn": "Enter a valid email address"},
    "error_address_short": {"en": "Enter a complete address", "bn": "Enter a complete address"},
    "error_dob_invalid": {"en": "Enter date in YYYY-MM-DD format", "bn": "Enter date in YYYY-MM-DD format"},

    # Navigation
    "back_to_home": {"en": "Back to Home", "bn": "Back to Home"},
    "language_toggle": {"en": "বাংলা", "bn": "বাংলা"},
}


def t(key: str, lang: str = "en") -> str:
    """Translate a key to the specified language."""
    if key not in TRANSLATIONS:
        return key
    lang_dict = TRANSLATIONS[key]
    return lang_dict.get(lang, lang_dict.get("en", key))


def get_available_languages() -> list:
    """Get list of supported language codes."""
    return ["en"]


def detect_language_from_query(query: str) -> str:
    """Detect language from query text."""
    return DEFAULT_LANG
