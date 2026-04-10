"""
lib/__init__.py — NagarAI library exports.
"""

# Security
from .security import PIIRedactor, SessionManager, InputSanitizer, render_security_demo_panel

# AI Engine
from .ai_engine import NagarAIEngine, render_ai_chat_demo

# Payment
from .payment_mock import PaymentVerifier, calculate_fee, initiate_payment, verify_payment, format_receipt

# Appointment
from .appointment import AppointmentEngine, generate_available_slots, book_slot, cancel_booking, get_upcoming_appointments

# Location
from .location_mock import LocationService, find_nearest_hospitals, find_nearest_pharmacies, find_nearest_police, get_emergency_contacts

# Synthetic Data
from .synthetic_data import load_heatmap_data, generate_weekly_table, get_summary_metrics, generate_heatmap_grid

# i18n
from .i18n import t, get_available_languages, detect_language_from_query

__all__ = [
    "PIIRedactor", "SessionManager", "InputSanitizer", "render_security_demo_panel",
    "NagarAIEngine", "render_ai_chat_demo",
    "PaymentVerifier", "calculate_fee", "initiate_payment", "verify_payment", "format_receipt",
    "AppointmentEngine", "generate_available_slots", "book_slot", "cancel_booking", "get_upcoming_appointments",
    "LocationService", "find_nearest_hospitals", "find_nearest_pharmacies", "find_nearest_police", "get_emergency_contacts",
    "load_heatmap_data", "generate_weekly_table", "get_summary_metrics", "generate_heatmap_grid",
    "t", "get_available_languages", "detect_language_from_query",
]
