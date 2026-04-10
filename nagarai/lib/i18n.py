"""
i18n.py - Bilingual language support (Bengali + English) for NagarAI.

Demo purpose: Show judges seamless language toggle throughout the app.
All user-facing text is available in both বাংলা and English.
"""

from typing import Dict


# Language state stored in Streamlit session state
DEFAULT_LANG = "bn"  # Bengali default


# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # App Identity
    "app_name": {"bn": "নাগরআই", "en": "NagarAI"},
    "app_tagline": {"bn": "এক অ্যাপ, দুই সেবা", "en": "One App, Two Services"},
    "app_subtitle": {"bn": "এআই-চালিত নাগরিক সেবা প্ল্যাটফর্ম", "en": "AI-Powered Civic Service Platform"},
    
    # Landing Page
    "welcome": {"bn": "স্বাগতম", "en": "Welcome"},
    "choose_service": {"bn": "আপনার সেবা ধরন বেছে নিন", "en": "Choose Your Service Type"},
    "govt_service": {"bn": "সরকারি সেবা", "en": "Government Service"},
    "govt_service_desc": {"bn": "ট্রেড লাইসেন্স, পাসপোর্ট, জন্ম সনদ - এআই দিয়ে দ্রুত আবেদন", "en": "Trade License, Passport, Birth Certificate - Apply faster with AI"},
    "social_service": {"bn": "সামাজিক সেবা", "en": "Social Service"},
    "social_service_desc": {"bn": "জরুরি সেবা - কোনো লগইন ছাড়াই নিকটস্থ হাসপাতাল, ফার্মেসি খুঁজুন", "en": "Emergency Services - Find nearest hospitals, pharmacies without login"},
    "view_heatmap": {"bn": "ফিডব্যাক হিটম্যাপ", "en": "Feedback Heatmap"},
    "view_heatmap_desc": {"bn": "সেবার চাহিদা এবং সন্তুষ্টির তথ্য দেখুন", "en": "View service demand and satisfaction data"},
    
    # Government Service Page
    "govt_service_title": {"bn": "সরকারি সেবা আবেদন", "en": "Government Service Application"},
    "enter_query": {"bn": "আপনার প্রয়োজনীয় সেবা লিখুন", "en": "Describe the service you need"},
    "query_placeholder": {"bn": "যেমন: আমি ট্রেড লাইসেন্স চাই", "en": "e.g., I need a trade license"},
    "intent_detected": {"bn": "সেবা সনাক্ত হয়েছে", "en": "Service Detected"},
    "intent_not_detected": {"bn": "সেবা সনাক্ত করা যায়নি", "en": "Service Not Detected"},
    "try_again": {"bn": "আবার চেষ্টা করুন", "en": "Try Again"},
    "fill_form": {"bn": "ফর্ম পূরণ করুন", "en": "Fill the Form"},
    "submit": {"bn": "জমা দিন", "en": "Submit"},
    "next_step": {"bn": "পরবর্তী ধাপ", "en": "Next Step"},
    "all_complete": {"bn": "সকল তথ্য পূরণ হয়েছে ✅", "en": "All information complete ✅"},
    
    # Form Fields
    "full_name": {"bn": "পূর্ণ নাম", "en": "Full Name"},
    "nid_number": {"bn": "জাতীয় পরিচয়পত্র নম্বর", "en": "National ID Number"},
    "phone_number": {"bn": "মোবাইল নম্বর", "en": "Mobile Number"},
    "email": {"bn": "ইমেইল", "en": "Email"},
    "address": {"bn": "ঠিকানা", "en": "Address"},
    "date_of_birth": {"bn": "জন্ম তারিখ", "en": "Date of Birth"},
    
    # Payment
    "payment": {"bn": "পেমেন্ট", "en": "Payment"},
    "fee": {"bn": "ফি", "en": "Fee"},
    "free": {"bn": "বিনামূল্যে", "en": "Free"},
    "pay_now": {"bn": "এখন পেমেন্ট করুন", "en": "Pay Now"},
    "payment_processing": {"bn": "পেমেন্ট প্রক্রিয়াধীন...", "en": "Payment Processing..."},
    "payment_success": {"bn": "পেমেন্ট সফল ✅", "en": "Payment Successful ✅"},
    "payment_failed": {"bn": "পেমেন্ট ব্যর্থ ❌", "en": "Payment Failed ❌"},
    "receipt": {"bn": "রসিদ", "en": "Receipt"},
    "transaction_id": {"bn": "ট্রানজাকশন আইডি", "en": "Transaction ID"},
    "receipt_number": {"bn": "রসিদ নম্বর", "en": "Receipt Number"},
    "amount": {"bn": "পরিমাণ", "en": "Amount"},
    "sms_confirmation": {"bn": "এসএমএস নিশ্চিতকরণ পাঠানো হয়েছে", "en": "SMS Confirmation Sent"},
    
    # Appointment
    "appointment": {"bn": "অ্যাপয়েন্টমেন্ট", "en": "Appointment"},
    "select_date": {"bn": "তারিখ বেছে নিন", "en": "Select Date"},
    "select_time": {"bn": "সময় বেছে নিন", "en": "Select Time"},
    "book_appointment": {"bn": "অ্যাপয়েন্টমেন্ট বুক করুন", "en": "Book Appointment"},
    "appointment_confirmed": {"bn": "অ্যাপয়েন্টমেন্ট নিশ্চিত হয়েছে", "en": "Appointment Confirmed"},
    "reference": {"bn": "রেফারেন্স", "en": "Reference"},
    "no_slots": {"bn": "কোনো খালি সময় নেই", "en": "No Available Slots"},
    
    # Social Service Page
    "social_service_title": {"bn": "জরুরি সামাজিক সেবা", "en": "Emergency Social Service"},
    "no_login_needed": {"bn": "কোনো লগইন প্রয়োজন নেই", "en": "No Login Required"},
    "emergency": {"bn": "জরুরি", "en": "Emergency"},
    "nearest_hospitals": {"bn": "নিকটস্থ হাসপাতাল", "en": "Nearest Hospitals"},
    "nearest_pharmacies": {"bn": "নিকটস্থ ফার্মেসি", "en": "Nearest Pharmacies"},
    "nearest_police": {"bn": "নিকটস্থ থানা", "en": "Nearest Police Stations"},
    "distance": {"bn": "দূরত্ব", "en": "Distance"},
    "km": {"bn": "কিমি", "en": "km"},
    "call": {"bn": "কল করুন", "en": "Call"},
    "beds_available": {"bn": "বেড খালি", "en": "Beds Available"},
    "open_24h": {"bn": "২৪ ঘণ্টা খোলা", "en": "Open 24 Hours"},
    "enter_location": {"bn": "আপনার অবস্থান দিন", "en": "Enter Your Location"},
    "demo_location": {"bn": "ডেমো অবস্থান ব্যবহার করুন", "en": "Use Demo Location"},
    "emergency_contacts": {"bn": "জরুরি যোগাযোগ", "en": "Emergency Contacts"},
    "national_emergency": {"bn": "জাতীয় জরুরি নম্বর", "en": "National Emergency"},
    "fire_service": {"bn": "ফায়ার সার্ভিস", "en": "Fire Service"},
    "ambulance": {"bn": "অ্যাম্বুলেন্স", "en": "Ambulance"},
    
    # Heatmap Page
    "heatmap_title": {"bn": "সেবা ফিডব্যাক হিটম্যাপ", "en": "Service Feedback Heatmap"},
    "service_demand": {"bn": "সেবার চাহিদা", "en": "Service Demand"},
    "satisfaction": {"bn": "সন্তুষ্টি", "en": "Satisfaction"},
    "positive": {"bn": "ইতিবাচক", "en": "Positive"},
    "neutral": {"bn": "নিরপেক্ষ", "en": "Neutral"},
    "negative": {"bn": "নেতিবাচক", "en": "Negative"},
    "applications": {"bn": "আবেদন", "en": "Applications"},
    "peak_area": {"bn": "সর্বোচ্চ চাহিদার এলাকা", "en": "Peak Demand Area"},
    "nagarai_impact": {"bn": "নাগরআই এর প্রভাব", "en": "NagarAI Impact"},
    "users_served": {"bn": "সেবা প্রাপ্ত ব্যবহারকারী", "en": "Users Served"},
    "time_saved": {"bn": "সাশ্রয়িত সময়", "en": "Time Saved"},
    "success_rate": {"bn": "সফলতার হার", "en": "Success Rate"},
    "minutes": {"bn": "মিনিট", "en": "minutes"},
    "improvement": {"bn": "উন্নতি", "en": "Improvement"},
    "demo_data_label": {"bn": "ডেমো তথ্য", "en": "Demo Data"},
    
    # Security
    "security_notice": {
        "bn": "🔒 আপনার তথ্য সম্পূর্ণ নিরাপদ। কোনো ব্যক্তিगत তথ্য সংরক্ষণ করা হয় না।",
        "en": "🔒 Your data is completely secure. No personal information is stored."
    },
    "pii_redacted": {"bn": "ব্যক্তিगत তথ্য মুছে ফেলা হয়েছে", "en": "Personal information redacted"},
    "session_active": {"bn": "সক্রিয় সেশন", "en": "Active Session"},
    "session_expires": {"bn": "সেশন শেষ হবে", "en": "Session Expires"},
    
    # Validation Messages
    "error_name_required": {"bn": "নাম আবশ্যক", "en": "Name is required"},
    "error_name_short": {"bn": "নাম কমপক্ষে ৩ অক্ষরের হতে হবে", "en": "Name must be at least 3 characters"},
    "error_phone_invalid": {"bn": "সঠিক ১১ ডিজিটের ফোন নম্বর দিন", "en": "Enter a valid 11-digit phone number"},
    "error_nid_invalid": {"bn": "সঠিক জাতীয় পরিচয়পত্র নম্বর দিন", "en": "Enter a valid National ID number"},
    "error_email_invalid": {"bn": "সঠিক ইমেইল ঠিকানা দিন", "en": "Enter a valid email address"},
    "error_address_short": {"bn": "সম্পূর্ণ ঠিকানা দিন", "en": "Enter a complete address"},
    "error_dob_invalid": {"bn": "সঠিক তারিখ ফরম্যাট দিন (YYYY-MM-DD)", "en": "Enter date in YYYY-MM-DD format"},
    
    # Navigation
    "back_to_home": {"bn": "হোমে ফিরুন", "en": "Back to Home"},
    "language_toggle": {"bn": "English", "en": "বাংলা"},
}


def t(key: str, lang: str = "bn") -> str:
    """Translate a key to the specified language.
    
    Demo purpose: Every UI text call uses this function for bilingual support.
    
    Args:
        key: Translation key
        lang: Language code ('bn' for Bengali, 'en' for English)
        
    Returns:
        Translated string, falls back to English then key if missing
        
    Examples:
        >>> t("app_name", "bn")
        'নাগরআই'
        >>> t("app_name", "en")
        'NagarAI'
        >>> t("nonexistent_key")
        'nonexistent_key'
    """
    if key not in TRANSLATIONS:
        return key
    
    lang_dict = TRANSLATIONS[key]
    
    # Return requested language, fallback to English, then fallback to key
    return lang_dict.get(lang, lang_dict.get("en", key))


def get_available_languages() -> list:
    """Get list of supported language codes.
    
    Returns:
        List of language codes
        
    Examples:
        >>> langs = get_available_languages()
        >>> "bn" in langs
        True
        >>> "en" in langs
        True
    """
    return ["bn", "en"]


def detect_language_from_query(query: str) -> str:
    """Detect if query is primarily Bengali or English.
    
    Demo purpose: Auto-detect user's preferred language from input.
    
    Args:
        query: User's input text
        
    Returns:
        Language code ('bn' or 'en')
        
    Examples:
        >>> detect_language_from_query("আমি পাসপোর্ট চাই")
        'bn'
        >>> detect_language_from_query("I need a passport")
        'en'
    """
    if not query:
        return DEFAULT_LANG
    
    # Count Bengali Unicode characters
    bengali_chars = sum(1 for char in query if '\u0980' <= char <= '\u09FF')
    total_alpha = sum(1 for char in query if char.isalpha())
    
    if total_alpha == 0:
        return DEFAULT_LANG
    
    bengali_ratio = bengali_chars / total_alpha
    return "bn" if bengali_ratio > 0.3 else "en"
