"""
ai_engine.py - Complete AI engine for NagarAI hackathon demo.

Class: NagarAIEngine with intent detection, guided questions, validation, checklist.
Plus: Legacy functions for backward compatibility.
Plus: render_ai_chat_demo() for Streamlit UI demonstration.

Demo purpose: Show judges AI that "asks the right questions" — feels magical.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

import streamlit as st


# Load service knowledge base
_KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "services_kb.json")


def _load_kb() -> Dict:
    """Load service knowledge base from JSON file."""
    try:
        with open(_KB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"services": [], "intents": {}}


# ============================================================
# CLASS: NagarAIEngine — The brain of NagarAI
# ============================================================
class NagarAIEngine:
    """AI-powered intent detection and guided form system.

    Design principle: "The AI asks the right questions, the user gives the answers."
    No auto-fill. No assumptions. Guide → validate → confirm.
    """

    def __init__(self, services_kb: Dict = None):
        """Initialize engine with service knowledge base.

        Args:
            services_kb: Service KB dict (auto-loads from JSON if None)
        """
        self.services_kb = services_kb or _load_kb()

        # Guided questions for each service (4-6 questions per service)
        self.guided_questions = {
            "passport": [
                {
                    "step": 1,
                    "question_bn": "আপনার পুরনো পাসপোর্ট কি আছে?",
                    "field_name": "has_old_passport",
                    "input_type": "radio",
                    "options_bn": ["হ্যাঁ, আছে", "না, হারিয়ে গেছে", "মেয়াদ শেষ হয়েছে"],
                    "validation_rule": "required",
                    "help_text_bn": "পাসপোর্টের ধরন নির্ভর করে এই উত্তরের উপর",
                },
                {
                    "step": 2,
                    "question_bn": "পাসপোর্টের ধরন বেছে নিন:",
                    "field_name": "passport_type",
                    "input_type": "radio",
                    "options_bn": ["সাধারণ (৩ বছর)", "জরুরি (১ বছর)", "অফিসিয়াল"],
                    "validation_rule": "required",
                    "help_text_bn": "জরুরি পাসপোর্টে অতিরিক্ত ফি প্রযোজ্য",
                },
                {
                    "step": 3,
                    "question_bn": "আপনার জাতীয় পরিচয়পত্র (NID) নম্বর দিন:",
                    "field_name": "nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "১০ বা ১৭ ডিজিটের NID নম্বর",
                },
                {
                    "step": 4,
                    "question_bn": "আপনার মোবাইল নম্বর দিন:",
                    "field_name": "phone",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "phone_bd",
                    "help_text_bn": "SMS পাঠানো হবে এই নম্বরে",
                },
                {
                    "step": 5,
                    "question_bn": "আপনার জন্ম তারিখ (DD/MM/YYYY):",
                    "field_name": "dob",
                    "input_type": "date",
                    "options_bn": None,
                    "validation_rule": "date_format",
                    "help_text_bn": "দিন/মাস/বছর ফরম্যাটে লিখুন",
                },
            ],
            "trade_license": [
                {
                    "step": 1,
                    "question_bn": "ব্যবসার ধরন কী?",
                    "field_name": "business_type",
                    "input_type": "radio",
                    "options_bn": ["দোকান/অফিস", "কারখানা", "ই-কমার্স", "সেবা খাত", "অন্যান্য"],
                    "validation_rule": "required",
                    "help_text_bn": "ব্যবসার ধরন অনুযায়ী ফি ভিন্ন হয়",
                },
                {
                    "step": 2,
                    "question_bn": "ব্যবসার নাম কী?",
                    "field_name": "business_name",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "ট্রেড লাইসেন্সে এই নাম থাকবে",
                },
                {
                    "step": 3,
                    "question_bn": "ব্যবসার ঠিকানা দিন:",
                    "field_name": "business_address",
                    "input_type": "textarea",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "বাড়ি নম্বর, রোড, এলাকা, থানা",
                },
                {
                    "step": 4,
                    "question_bn": "আপনার NID নম্বর:",
                    "field_name": "nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "ব্যবসার মালিকের জাতীয় পরিচয়পত্র",
                },
                {
                    "step": 5,
                    "question_bn": "মোবাইল নম্বর:",
                    "field_name": "phone",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "phone_bd",
                    "help_text_bn": "যোগাযোগের জন্য ব্যবহৃত হবে",
                },
            ],
            "birth_certificate": [
                {
                    "step": 1,
                    "question_bn": "শিশুর পূর্ণ নাম:",
                    "field_name": "child_name",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "জন্ম সনদে এই নাম থাকবে",
                },
                {
                    "step": 2,
                    "question_bn": "জন্ম তারিখ (DD/MM/YYYY):",
                    "field_name": "birth_date",
                    "input_type": "date",
                    "options_bn": None,
                    "validation_rule": "date_format",
                    "help_text_bn": "দিন/মাস/বছর ফরম্যাটে",
                },
                {
                    "step": 3,
                    "question_bn": "জন্মস্থান (জেলা/থানা):",
                    "field_name": "birth_place",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "যে জেলায়/থানায় জন্ম হয়েছে",
                },
                {
                    "step": 4,
                    "question_bn": "অভিভাবকের NID নম্বর:",
                    "field_name": "parent_nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "বাবা বা মায়ের জাতীয় পরিচয়পত্র",
                },
                {
                    "step": 5,
                    "question_bn": "হাসপাতালের সনদ আছে কি?",
                    "field_name": "has_hospital_cert",
                    "input_type": "radio",
                    "options_bn": ["হ্যাঁ, আছে", "না, নেই"],
                    "validation_rule": "required",
                    "help_text_bn": "হাসপাতালে জন্ম হলে সনদ লাগবে",
                },
            ],
            "tin_certificate": [
                {
                    "step": 1,
                    "question_bn": "আপনার পূর্ণ নাম:",
                    "field_name": "name",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "TIN সনদে এই নাম থাকবে",
                },
                {
                    "step": 2,
                    "question_bn": "NID নম্বর:",
                    "field_name": "nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "জাতীয় পরিচয়পত্র নম্বর",
                },
                {
                    "step": 3,
                    "question_bn": "বার্ষিক আয় কত?",
                    "field_name": "annual_income",
                    "input_type": "radio",
                    "options_bn": ["৫ লাখের কম", "৫-১০ লাখ", "১০-২৫ লাখ", "২৫ লাখের বেশি"],
                    "validation_rule": "required",
                    "help_text_bn": "কর রেট আয়ের উপর নির্ভরশীল",
                },
                {
                    "step": 4,
                    "question_bn": "মোবাইল নম্বর:",
                    "field_name": "phone",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "phone_bd",
                    "help_text_bn": "OTP পাঠানো হবে",
                },
            ],
            "land_deed": [
                {
                    "step": 1,
                    "question_bn": "জমির অবস্থান (জেলা/থানা/মৌজা):",
                    "field_name": "land_location",
                    "input_type": "textarea",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "সম্পূর্ণ ঠিকানা দিন",
                },
                {
                    "step": 2,
                    "question_bn": "জমির পরিমাণ (শতাংশ/ডেসিমাল):",
                    "field_name": "land_area",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "খতিয়ানে উল্লিখিত পরিমাণ",
                },
                {
                    "step": 3,
                    "question_bn": "খতিয়ান নম্বর:",
                    "field_name": "khatian_no",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "ভূমি উন্নয়ন অফিস থেকে পাওয়া যাবে",
                },
                {
                    "step": 4,
                    "question_bn": "বিক্রেতার NID নম্বর:",
                    "field_name": "seller_nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "জমির মালিকের পরিচয়পত্র",
                },
                {
                    "step": 5,
                    "question_bn": "ক্রেতার NID নম্বর:",
                    "field_name": "buyer_nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "যিনি জমি কিনছেন",
                },
                {
                    "step": 6,
                    "question_bn": "দলিলের তারিখ (DD/MM/YYYY):",
                    "field_name": "deed_date",
                    "input_type": "date",
                    "options_bn": None,
                    "validation_rule": "date_format",
                    "help_text_bn": "দলিল সম্পাদনের তারিখ",
                },
            ],
        }

        # Checklist templates for each service
        self.checklist_templates = {
            "passport": {
                "required_docs": [
                    "জাতীয় পরিচয়পত্র (NID) কপি",
                    "শিক্ষাগত সনদের সত্যায়িত কপি",
                    "পাসপোর্ট সাইজের ছবি ৩ কপি",
                    "পুরনো পাসপোর্ট (যদি থাকে)",
                ],
                "optional_docs": [
                    "নাগরিকত্ব সনদ",
                    "পেশাগত পরিচয়পত্র",
                ],
                "estimated_fee": 5750,
                "fee_breakdown": [
                    {"item": "পাসপোর্ট ফি (সাধারণ)", "amount": 3450},
                    {"item": "ডেলিভারি চার্জ", "amount": 300},
                    {"item": "ভ্যাট/ট্যাক্স", "amount": 2000},
                ],
                "estimated_days": 21,
                "office_name_bn": "ইমিগ্রেশন অফিস, ঢাকা",
                "office_address_bn": "আগারগাঁও, শেরে বাংলা নগর, ঢাকা-১২০৭",
                "next_action_bn": "এখন অনলাইনে ফি পরিশোধ করুন",
            },
            "trade_license": {
                "required_docs": [
                    "ন্যাশনাল আইডি কার্ড",
                    "হালকা সনদ",
                    "ভাড়া চুক্তিনামা",
                    "ব্যবসার ছবি ২ কপি",
                ],
                "optional_docs": [
                    "ট্রেড লাইসেন্স নবায়ন ফর্ম",
                    "পূর্ব বছরের রিটার্ন",
                ],
                "estimated_fee": 1500,
                "fee_breakdown": [
                    {"item": "লাইসেন্স ফি", "amount": 1000},
                    {"item": "সার্ভিস চার্জ", "amount": 200},
                    {"item": "ভ্যাট", "amount": 300},
                ],
                "estimated_days": 7,
                "office_name_bn": "সিটি কর্পোরেশন অফিস",
                "office_address_bn": "স্থানীয় সিটি কর্পোরেশন, ঢাকা",
                "next_action_bn": "এখন আবেদন ফর্ম পূরণ করুন",
            },
            "birth_certificate": {
                "required_docs": [
                    "হাসপাতালের জন্ম সনদ",
                    "অভিভাবকের জাতীয় পরিচয়পত্র",
                    "ইউনিয়ন পরিষদ/পৌরসভা থেকে ফরম",
                ],
                "optional_docs": [
                    "ওয়াড কাউন্সিলরের সনদ",
                ],
                "estimated_fee": 0,
                "fee_breakdown": [
                    {"item": "জন্ম সনদ ফি", "amount": 0},
                    {"item": "সার্ভিস চার্জ", "amount": 0},
                ],
                "estimated_days": 14,
                "office_name_bn": "ইউনিয়ন পরিষদ/পৌরসভা অফিস",
                "office_address_bn": "স্থানীয় ইউনিয়ন পরিষদ কার্যালয়",
                "next_action_bn": "ফ্রি সেবা — সরাসরি অফিসে যান",
            },
            "tin_certificate": {
                "required_docs": [
                    "জাতীয় পরিচয়পত্র",
                    "মোবাইল নম্বর",
                ],
                "optional_docs": [
                    "ই-মেইল ঠিকানা",
                ],
                "estimated_fee": 0,
                "fee_breakdown": [
                    {"item": "TIN রেজিস্ট্রেশন ফি", "amount": 0},
                ],
                "estimated_days": 1,
                "office_name_bn": "জাতীয় রাজস্ব বোর্ড (NBR)",
                "office_address_bn": "সেগুনবাগিচা, ঢাকা-১০০০",
                "next_action_bn": "এখন ই-টিন রেজিস্ট্রেশন করুন",
            },
            "land_deed": {
                "required_docs": [
                    "খতিয়ান",
                    "নামজারি কাগজ",
                    "দলিলের কপি",
                    "উভয় পক্ষের NID কপি",
                    "খাজনা পরিশোধ রসিদ",
                ],
                "optional_docs": [
                    "মিউটেশন কপি",
                    "অনাপত্তি সনদ",
                ],
                "estimated_fee": 5000,
                "fee_breakdown": [
                    {"item": "রেজিস্ট্রেশন ফি", "amount": 3000},
                    {"item": "স্ট্যাম্প পেপার", "amount": 1000},
                    {"item": "সার্ভিস চার্জ", "amount": 1000},
                ],
                "estimated_days": 30,
                "office_name_bn": "সাব-রেজিস্ট্রার অফিস",
                "office_address_bn": "স্থানীয় সাব-রেজিস্ট্রার কার্যালয়",
                "next_action_bn": "সাব-রেজিস্ট্রার অফিসে যান",
            },
        }

    # ============================================================
    # METHOD 1: detect_intent — Understand user's service need
    # ============================================================
    def detect_intent(self, user_input: str) -> dict:
        """Detect which government service the user is asking about.

        Args:
            user_input: Raw Bengali or English text from user

        Returns:
            Dict with detected_service, confidence, service_data,
            clarification_needed, clarification_question_bn

        Example:
            >>> engine = NagarAIEngine()
            >>> result = engine.detect_intent("আমি পাসপোর্ট নবায়ন করতে চাই")
            >>> result["detected_service"] == "passport"
            True
        """
        if not isinstance(user_input, str) or not user_input.strip():
            return {
                "detected_service": None,
                "confidence": 0.0,
                "service_data": None,
                "clarification_needed": True,
                "clarification_question_bn": "আপনি কোন সেবার জন্য আবেদন করতে চান?",
            }

        kb = self.services_kb
        query_lower = user_input.lower()

        # Special case handling BEFORE keyword matching
        # Case 1: Lost passport → new, not renewal
        if ("হারিয়ে গেছে" in query_lower or "lost" in query_lower) and (
            "পাসপোর্ট" in query_lower or "passport" in query_lower
        ):
            service_data = self._get_service_by_id("passport")
            return {
                "detected_service": "passport",
                "confidence": 0.92,
                "service_data": service_data,
                "clarification_needed": False,
                "clarification_question_bn": None,
            }

        # Case 2: NID correction
        if ("সংশোধন" in query_lower or "correction" in query_lower) and (
            "NID" in query_upper if (query_upper := query_lower.upper()) else False
        ):
            return {
                "detected_service": "nid_correction",
                "confidence": 0.85,
                "service_data": {"id": "nid_correction", "name_bn": "NID সংশোধন", "name_en": "NID Correction"},
                "clarification_needed": True,
                "clarification_question_bn": "আপনার NID-এ কোন তথ্য সংশোধন করতে চান?",
            }

        # Case 3: New application variant
        is_new_application = "নতুন" in query_lower or "new" in query_lower

        # Score each service
        scores = {}
        for service_id, keywords in kb.get("intents", {}).items():
            score = 0
            for kw in keywords:
                if kw.lower() in query_lower:
                    score += 1
            if score > 0:
                # Boost score for "new" applications
                if is_new_application:
                    score += 0.5
                scores[service_id] = score

        if not scores:
            return {
                "detected_service": None,
                "confidence": 0.0,
                "service_data": None,
                "clarification_needed": True,
                "clarification_question_bn": "আপনি কোন সেবার জন্য আবেদন করতে চান? (যেমন: পাসপোর্ট, ট্রেড লাইসেন্স, জন্ম সনদ)",
            }

        # Find best match
        best_service = max(scores, key=scores.get)
        max_score = scores[best_service]
        total_keywords = len(kb.get("intents", {}).get(best_service, []))
        confidence = min(max_score / total_keywords, 1.0)

        # Clarification needed if confidence < 0.5
        clarification_needed = confidence < 0.5
        clarification_question = None
        if clarification_needed:
            service_data = self._get_service_by_id(best_service)
            service_name = service_data.get("name_bn", best_service) if service_data else best_service
            clarification_question = f"আপনি কি **{service_name}**-এর জন্য আবেদন করতে চান?"

        service_data = self._get_service_by_id(best_service)

        return {
            "detected_service": best_service,
            "confidence": round(confidence, 2),
            "service_data": service_data,
            "clarification_needed": clarification_needed,
            "clarification_question_bn": clarification_question,
        }

    def _get_service_by_id(self, service_id: str) -> Optional[Dict]:
        """Get service data from KB by ID."""
        for service in self.services_kb.get("services", []):
            if service["id"] == service_id:
                return service
        return None

    # ============================================================
    # METHOD 2: get_guided_questions — Step-by-step question flow
    # ============================================================
    def get_guided_questions(self, service_id: str) -> list:
        """Get step-by-step guided questions for a service.

        Args:
            service_id: Service identifier

        Returns:
            List of question dicts with step, question_bn, field_name, etc.

        Example:
            >>> engine = NagarAIEngine()
            >>> questions = engine.get_guided_questions("passport")
            >>> len(questions) >= 4
            True
            >>> questions[0]["step"] == 1
            True
        """
        return self.guided_questions.get(service_id, [])

    # ============================================================
    # METHOD 3: validate_field — Validate user answer
    # ============================================================
    def validate_field(self, field_name: str, value: str, service_id: str = None) -> dict:
        """Validate a single field value.

        Args:
            field_name: Field name (e.g., "phone", "nid")
            value: User's input value
            service_id: Optional service context

        Returns:
            Dict with valid flag, message_bn, suggestion_bn

        Example:
            >>> engine = NagarAIEngine()
            >>> result = engine.validate_field("phone", "01712345678")
            >>> result["valid"] == True
            True
        """
        if not isinstance(value, str) or not value.strip():
            return {
                "valid": False,
                "message_bn": "এই ঘরে তথ্য দিন",
                "suggestion_bn": None,
            }

        value = value.strip()

        # Phone validation
        if field_name == "phone":
            cleaned = re.sub(r'[\s\-\+]', '', value)
            is_valid = bool(re.match(r'^01[3-9]\d{8}$', cleaned))
            return {
                "valid": is_valid,
                "message_bn": "সঠিক ১১ ডিজিটের ফোন নম্বর দিন (01XXXXXXXXX)" if not is_valid else "✅ ফোন নম্বর সঠিক",
                "suggestion_bn": "উদাহরণ: 01712345678" if not is_valid else None,
            }

        # NID validation
        if field_name in ("nid", "parent_nid", "seller_nid", "buyer_nid"):
            cleaned = re.sub(r'[\s\-]', '', value)
            is_valid = bool(re.match(r'^\d{10}$|^\d{17}$', cleaned))
            return {
                "valid": is_valid,
                "message_bn": "সঠিক NID নম্বর দিন (১০ বা ১৭ ডিজিট)" if not is_valid else "✅ NID নম্বর সঠিক",
                "suggestion_bn": "উদাহরণ: 1234567890" if not is_valid else None,
            }

        # Date validation (DD/MM/YYYY)
        if field_name in ("dob", "birth_date", "deed_date"):
            # Try DD/MM/YYYY or YYYY-MM-DD
            date_patterns = [r'^\d{2}/\d{2}/\d{4}$', r'^\d{4}-\d{2}-\d{2}$']
            is_valid = any(re.match(p, value) for p in date_patterns)

            if is_valid:
                # Further validate actual date
                try:
                    separator = '/' if '/' in value else '-'
                    parts = value.split(separator)
                    if len(parts[0]) == 4:  # YYYY-MM-DD
                        datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                    else:  # DD/MM/YYYY
                        datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                except (ValueError, IndexError):
                    is_valid = False

            return {
                "valid": is_valid,
                "message_bn": "সঠিক তারিখ ফরম্যাট দিন (DD/MM/YYYY)" if not is_valid else "✅ তারিখ সঠিক",
                "suggestion_bn": "উদাহরণ: 15/04/1990" if not is_valid else None,
            }

        # Required field check
        if not value:
            return {
                "valid": False,
                "message_bn": "এই ঘরে তথ্য দিন",
                "suggestion_bn": None,
            }

        # Default: valid
        return {
            "valid": True,
            "message_bn": "✅ তথ্য সঠিক",
            "suggestion_bn": None,
        }

    # ============================================================
    # METHOD 4: generate_checklist — Personalized checklist
    # ============================================================
    def generate_checklist(self, service_id: str, user_answers: dict = None) -> dict:
        """Generate personalized checklist based on user answers.

        Args:
            service_id: Service identifier
            user_answers: Dict of user's answers to guided questions

        Returns:
            Dict with required_docs, optional_docs, estimated_fee,
            fee_breakdown, estimated_days, office info, next_action

        Example:
            >>> engine = NagarAIEngine()
            >>> checklist = engine.generate_checklist("passport")
            >>> "required_docs" in checklist
            True
            >>> checklist["estimated_fee"] > 0
            True
        """
        template = self.checklist_templates.get(service_id, {})

        if not template:
            return {
                "required_docs": [],
                "optional_docs": [],
                "estimated_fee": 0,
                "fee_breakdown": [],
                "estimated_days": 0,
                "office_name_bn": "অফিস তথ্য পাওয়া যায়নি",
                "office_address_bn": "",
                "next_action_bn": "সেবার তথ্য পাওয়া যায়নি",
            }

        # Personalize based on user answers
        required_docs = template.get("required_docs", []).copy()
        optional_docs = template.get("optional_docs", []).copy()

        # Example personalization: if user said they lost old passport
        if user_answers:
            if user_answers.get("has_old_passport") == "না, হারিয়ে গেছে":
                required_docs.append("জিডি (সাধারণ ডায়েরি) কপি")
            if user_answers.get("passport_type") == "জরুরি (১ বছর)":
                # Update fee for urgent passport
                template = template.copy()
                template["estimated_fee"] = 8500
                template["estimated_days"] = 7
                template["fee_breakdown"] = [
                    {"item": "পাসপোর্ট ফি (জরুরি)", "amount": 6000},
                    {"item": "ডেলিভারি চার্জ", "amount": 500},
                    {"item": "ভ্যাট/ট্যাক্স", "amount": 2000},
                ]

        return {
            "required_docs": required_docs,
            "optional_docs": optional_docs,
            "estimated_fee": template.get("estimated_fee", 0),
            "fee_breakdown": template.get("fee_breakdown", []),
            "estimated_days": template.get("estimated_days", 0),
            "office_name_bn": template.get("office_name_bn", ""),
            "office_address_bn": template.get("office_address_bn", ""),
            "next_action_bn": template.get("next_action_bn", ""),
        }


# ============================================================
# FUNCTION: render_ai_chat_demo — Streamlit chat UI
# ============================================================
def render_ai_chat_demo(engine: NagarAIEngine = None):
    """Render AI chat demo in Streamlit.

    Shows:
    - Text input with Bengali placeholder
    - On submit: detected intent with confidence bar
    - First guided question
    - On each answer: next question
    - After all questions: personalized checklist
    """
    if engine is None:
        engine = NagarAIEngine()

    st.markdown("### 🤖 নাগরআই এসিস্ট্যান্ট")
    st.caption("আপনার কাজের কথা বলুন — AI আপনাকে গাইড করবে")

    # Initialize chat state
    if "chat_step" not in st.session_state:
        st.session_state.chat_step = "input"  # input → questions → checklist
        st.session_state.chat_service = None
        st.session_state.chat_questions = []
        st.session_state.chat_answers = {}
        st.session_state.chat_current_q = 0

    # Step 1: User types their need
    if st.session_state.chat_step == "input":
        user_input = st.text_input(
            "আপনার কাজের কথা বলুন",
            placeholder="যেমন: পাসপোর্ট নবায়ন করতে চাই",
            key="chat_user_input",
        )

        if user_input and st.button("➡️ জমা দিন", type="primary"):
            # Detect intent
            result = engine.detect_intent(user_input)

            if result["detected_service"]:
                st.session_state.chat_service = result["detected_service"]

                # Show confidence bar
                st.success(f"✅ সেবা সনাক্ত হয়েছে: **{result['service_data']['name_bn']}**")
                st.progress(result["confidence"])
                st.caption(f"Confidence: {result['confidence']:.0%}")

                # Load questions
                questions = engine.get_guided_questions(result["detected_service"])
                st.session_state.chat_questions = questions
                st.session_state.chat_step = "questions"
                st.session_state.chat_current_q = 0
                st.rerun()
            else:
                st.warning(result.get("clarification_question_bn", "আবার চেষ্টা করুন"))

    # Step 2: Guided questions
    elif st.session_state.chat_step == "questions":
        questions = st.session_state.chat_questions
        current_q = st.session_state.chat_current_q

        if current_q < len(questions):
            q = questions[current_q]

            st.markdown(f"**প্রশ্ন {q['step']}: {q['question_bn']}**")
            st.caption(q.get("help_text_bn", ""))

            answer = None
            if q["input_type"] == "radio" and q.get("options_bn"):
                answer = st.radio(
                    q["question_bn"],
                    options=q["options_bn"],
                    key=f"chat_q_{current_q}",
                )
            elif q["input_type"] == "textarea":
                answer = st.text_area(q["question_bn"], key=f"chat_q_{current_q}")
            else:
                answer = st.text_input(q["question_bn"], key=f"chat_q_{current_q}")

            if answer and st.button("✅ উত্তর দিন", type="primary"):
                # Validate
                validation = engine.validate_field(q["field_name"], answer)

                if validation["valid"]:
                    st.session_state.chat_answers[q["field_name"]] = answer
                    st.session_state.chat_current_q += 1

                    if validation["message_bn"]:
                        st.success(validation["message_bn"])

                    st.rerun()
                else:
                    st.error(validation["message_bn"])
                    if validation.get("suggestion_bn"):
                        st.caption(f"💡 {validation['suggestion_bn']}")

            # Show progress
            st.progress((current_q + 1) / len(questions))
            st.caption(f"প্রশ্ন {current_q + 1}/{len(questions)}")
        else:
            # All questions answered → show checklist
            st.session_state.chat_step = "checklist"
            st.rerun()

    # Step 3: Checklist
    elif st.session_state.chat_step == "checklist":
        service_id = st.session_state.chat_service
        answers = st.session_state.chat_answers

        checklist = engine.generate_checklist(service_id, answers)

        st.markdown("### 📋 আপনার ব্যক্তিগত চেকলিস্ট")

        st.markdown("**📄 প্রয়োজনীয় কাগজপত্র:**")
        for doc in checklist["required_docs"]:
            st.markdown(f"✅ {doc}")

        if checklist["optional_docs"]:
            st.markdown("**📎 ঐচ্ছিক কাগজপত্র:**")
            for doc in checklist["optional_docs"]:
                st.markdown(f"🔹 {doc}")

        col1, col2, col3 = st.columns(3)
        col1.metric("আনুমানিক ফি", f"৳{checklist['estimated_fee']}")
        col2.metric("সময়", f"{checklist['estimated_days']} দিন")
        col3.metric("অফিস", checklist["office_name_bn"])

        st.info(f"👉 **পরবর্তী ধাপ:** {checklist['next_action_bn']}")

        # Reset button
        if st.button("🔄 নতুন আবেদন"):
            st.session_state.chat_step = "input"
            st.session_state.chat_service = None
            st.session_state.chat_questions = []
            st.session_state.chat_answers = {}
            st.session_state.chat_current_q = 0
            st.rerun()


# ============================================================
# Legacy functions for backward compatibility
# ============================================================
def detect_intent(user_query: str) -> Optional[str]:
    """Legacy function — wraps NagarAIEngine.detect_intent."""
    engine = NagarAIEngine()
    result = engine.detect_intent(user_query)
    return result["detected_service"]


def get_service_info(service_id: str) -> Optional[Dict]:
    """Legacy function — get service data from KB."""
    engine = NagarAIEngine()
    return engine._get_service_by_id(service_id)


def validate_form_field(field_name: str, value: str) -> tuple:
    """Legacy function — wraps NagarAIEngine.validate_field."""
    engine = NagarAIEngine()
    result = engine.validate_field(field_name, value)
    return (result["valid"], result["message_bn"] if not result["valid"] else "")


def get_form_fields_for_service(service_id: str) -> List[Dict]:
    """Legacy function — get form fields for service."""
    engine = NagarAIEngine()
    questions = engine.get_guided_questions(service_id)
    fields = []
    for q in questions:
        fields.append({
            "name": q["field_name"],
            "label_bn": q["question_bn"],
            "type": q["input_type"],
            "required": q.get("validation_rule") == "required",
            "options": q.get("options_bn", []),
        })
    return fields


def suggest_next_step(service_id: str, completed_fields: List[str]) -> Optional[str]:
    """Legacy function — suggest next field to complete."""
    engine = NagarAIEngine()
    questions = engine.get_guided_questions(service_id)
    for q in questions:
        if q["field_name"] not in completed_fields:
            return f"এবার আপনার {q['question_bn']} দিন"
    return None


# ============================================================
# TESTS
# ============================================================
if __name__ == "__main__":
    print("=== Running AI Engine Tests ===\n")

    engine = NagarAIEngine()

    # Test 1: Intent detection works
    result1 = engine.detect_intent("আমি পাসপোর্ট নবায়ন করতে চাই")
    assert result1["detected_service"] == "passport", f"Test 1 FAILED: Got {result1['detected_service']}"
    assert result1["confidence"] > 0, "Test 1 FAILED: Confidence is 0"
    print("✅ Test 1 PASSED: Intent detection works")

    # Test 2: Guided questions returned
    questions = engine.get_guided_questions("passport")
    assert len(questions) >= 4, f"Test 2 FAILED: Got {len(questions)} questions"
    assert questions[0]["step"] == 1, "Test 2 FAILED: First step not 1"
    print("✅ Test 2 PASSED: Guided questions returned")

    # Test 3: Field validation works
    result3a = engine.validate_field("phone", "01712345678")
    assert result3a["valid"] == True, "Test 3a FAILED: Valid phone rejected"
    result3b = engine.validate_field("phone", "12345")
    assert result3b["valid"] == False, "Test 3b FAILED: Invalid phone accepted"
    print("✅ Test 3 PASSED: Field validation works")

    # Test 4: Checklist generated
    checklist = engine.generate_checklist("passport")
    assert "required_docs" in checklist, "Test 4 FAILED: No required_docs"
    assert checklist["estimated_fee"] > 0, "Test 4 FAILED: Fee is 0"
    assert "office_name_bn" in checklist, "Test 4 FAILED: No office info"
    print("✅ Test 4 PASSED: Checklist generated")

    # Test 5: Special case — lost passport
    result5 = engine.detect_intent("পাসপোর্ট হারিয়ে গেছে, নতুন চাই")
    assert result5["detected_service"] == "passport", f"Test 5 FAILED: Got {result5['detected_service']}"
    assert result5["confidence"] > 0.8, "Test 5 FAILED: Low confidence for lost passport"
    print("✅ Test 5 PASSED: Lost passport special case handled")

    print("\n🎉 All 5 AI engine tests PASSED!")
