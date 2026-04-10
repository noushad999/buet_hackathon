"""
ai_engine.py — Complete AI engine for NagarAI hackathon demo.

Class: NagarAIEngine with intent detection, guided questions, validation, checklist.
All text in English for international hackathon.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

import streamlit as st


_KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "services_kb.json")


def _load_kb() -> Dict:
    """Load service knowledge base from JSON file."""
    try:
        with open(_KB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"services": [], "intents": {}}


class NagarAIEngine:
    """AI-powered intent detection and guided form system."""

    def __init__(self, services_kb: Dict = None):
        self.services_kb = services_kb or _load_kb()

        self.guided_questions = {
            "passport": [
                {
                    "step": 1,
                    "question_bn": "Do you have your old passport?",
                    "field_name": "has_old_passport",
                    "input_type": "radio",
                    "options_bn": ["Yes, I have it", "No, it is lost", "It has expired"],
                    "validation_rule": "required",
                    "help_text_bn": "Passport type depends on this answer",
                },
                {
                    "step": 2,
                    "question_bn": "Choose passport type:",
                    "field_name": "passport_type",
                    "input_type": "radio",
                    "options_bn": ["Regular (3 years)", "Urgent (1 year)", "Official"],
                    "validation_rule": "required",
                    "help_text_bn": "Urgent passport requires additional fee",
                },
                {
                    "step": 3,
                    "question_bn": "Enter your National ID (NID) number:",
                    "field_name": "nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "10 or 17 digit NID number",
                },
                {
                    "step": 4,
                    "question_bn": "Enter your mobile number:",
                    "field_name": "phone",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "phone_bd",
                    "help_text_bn": "SMS will be sent to this number",
                },
                {
                    "step": 5,
                    "question_bn": "Enter your date of birth (DD/MM/YYYY):",
                    "field_name": "dob",
                    "input_type": "date",
                    "options_bn": None,
                    "validation_rule": "date_format",
                    "help_text_bn": "DD/MM/YYYY format",
                },
            ],
            "trade_license": [
                {
                    "step": 1,
                    "question_bn": "What type of business?",
                    "field_name": "business_type",
                    "input_type": "radio",
                    "options_bn": ["Shop/Office", "Factory", "E-commerce", "Service", "Other"],
                    "validation_rule": "required",
                    "help_text_bn": "Fee varies by business type",
                },
                {
                    "step": 2,
                    "question_bn": "What is the business name?",
                    "field_name": "business_name",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "This name will appear on the license",
                },
                {
                    "step": 3,
                    "question_bn": "Enter business address:",
                    "field_name": "business_address",
                    "input_type": "textarea",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "House number, road, area, thana",
                },
                {
                    "step": 4,
                    "question_bn": "Enter your NID number:",
                    "field_name": "nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "Business owner's National ID",
                },
                {
                    "step": 5,
                    "question_bn": "Enter mobile number:",
                    "field_name": "phone",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "phone_bd",
                    "help_text_bn": "Used for communication",
                },
            ],
            "birth_certificate": [
                {
                    "step": 1,
                    "question_bn": "Child's full name:",
                    "field_name": "child_name",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "This name will appear on the birth certificate",
                },
                {
                    "step": 2,
                    "question_bn": "Date of birth (DD/MM/YYYY):",
                    "field_name": "birth_date",
                    "input_type": "date",
                    "options_bn": None,
                    "validation_rule": "date_format",
                    "help_text_bn": "DD/MM/YYYY format",
                },
                {
                    "step": 3,
                    "question_bn": "Place of birth (district/thana):",
                    "field_name": "birth_place",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "District/thana where birth occurred",
                },
                {
                    "step": 4,
                    "question_bn": "Parent's NID number:",
                    "field_name": "parent_nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "Father or mother's National ID",
                },
                {
                    "step": 5,
                    "question_bn": "Do you have the hospital birth certificate?",
                    "field_name": "has_hospital_cert",
                    "input_type": "radio",
                    "options_bn": ["Yes, I have it", "No, I don't"],
                    "validation_rule": "required",
                    "help_text_bn": "Required if born in a hospital",
                },
            ],
            "tin_certificate": [
                {
                    "step": 1,
                    "question_bn": "Your full name:",
                    "field_name": "name",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "This name will appear on the TIN certificate",
                },
                {
                    "step": 2,
                    "question_bn": "NID number:",
                    "field_name": "nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "National ID number",
                },
                {
                    "step": 3,
                    "question_bn": "What is your annual income?",
                    "field_name": "annual_income",
                    "input_type": "radio",
                    "options_bn": ["Below 5 lakh", "5-10 lakh", "10-25 lakh", "Above 25 lakh"],
                    "validation_rule": "required",
                    "help_text_bn": "Tax rate depends on income",
                },
                {
                    "step": 4,
                    "question_bn": "Mobile number:",
                    "field_name": "phone",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "phone_bd",
                    "help_text_bn": "OTP will be sent here",
                },
            ],
            "land_deed": [
                {
                    "step": 1,
                    "question_bn": "Land location (district/thana/mouza):",
                    "field_name": "land_location",
                    "input_type": "textarea",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "Complete address",
                },
                {
                    "step": 2,
                    "question_bn": "Land area (katha/decimal):",
                    "field_name": "land_area",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "Amount as shown in khatian",
                },
                {
                    "step": 3,
                    "question_bn": "Khatian number:",
                    "field_name": "khatian_no",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "required",
                    "help_text_bn": "Available from Land Development Office",
                },
                {
                    "step": 4,
                    "question_bn": "Seller's NID number:",
                    "field_name": "seller_nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "Land owner's ID",
                },
                {
                    "step": 5,
                    "question_bn": "Buyer's NID number:",
                    "field_name": "buyer_nid",
                    "input_type": "text",
                    "options_bn": None,
                    "validation_rule": "nid_format",
                    "help_text_bn": "Person purchasing the land",
                },
                {
                    "step": 6,
                    "question_bn": "Deed date (DD/MM/YYYY):",
                    "field_name": "deed_date",
                    "input_type": "date",
                    "options_bn": None,
                    "validation_rule": "date_format",
                    "help_text_bn": "Date of deed execution",
                },
            ],
        }

        self.checklist_templates = {
            "passport": {
                "required_docs": [
                    "National ID (NID) copy",
                    "Attested copy of educational certificate",
                    "3 passport-size photos",
                    "Old passport (if available)",
                ],
                "optional_docs": [
                    "Citizenship certificate",
                    "Professional ID card",
                ],
                "estimated_fee": 5750,
                "fee_breakdown": [
                    {"item": "Passport fee (Regular)", "amount": 3450},
                    {"item": "Delivery charge", "amount": 300},
                    {"item": "VAT/Tax", "amount": 2000},
                ],
                "estimated_days": 21,
                "office_name_bn": "Immigration Office, Dhaka",
                "office_address_bn": "Agargaon, Sher-e-Bangla Nagar, Dhaka-1207",
                "next_action_bn": "Proceed to online payment",
            },
            "trade_license": {
                "required_docs": [
                    "National ID card",
                    "Clearance certificate",
                    "Rent agreement",
                    "2 photos of business",
                ],
                "optional_docs": [
                    "License renewal form",
                    "Previous year's return",
                ],
                "estimated_fee": 1500,
                "fee_breakdown": [
                    {"item": "License fee", "amount": 1000},
                    {"item": "Service charge", "amount": 200},
                    {"item": "VAT", "amount": 300},
                ],
                "estimated_days": 7,
                "office_name_bn": "City Corporation Office",
                "office_address_bn": "Local City Corporation, Dhaka",
                "next_action_bn": "Fill the application form",
            },
            "birth_certificate": {
                "required_docs": [
                    "Hospital birth certificate",
                    "Parent's National ID",
                    "Form from Union Parishad/Municipality",
                ],
                "optional_docs": [
                    "Ward Councilor certificate",
                ],
                "estimated_fee": 0,
                "fee_breakdown": [
                    {"item": "Birth certificate fee", "amount": 0},
                    {"item": "Service charge", "amount": 0},
                ],
                "estimated_days": 14,
                "office_name_bn": "Union Parishad / Municipality Office",
                "office_address_bn": "Local Union Parishad Office",
                "next_action_bn": "Free service — visit the office directly",
            },
            "tin_certificate": {
                "required_docs": [
                    "National ID card",
                    "Mobile number",
                ],
                "optional_docs": [
                    "Email address",
                ],
                "estimated_fee": 0,
                "fee_breakdown": [
                    {"item": "TIN registration fee", "amount": 0},
                ],
                "estimated_days": 1,
                "office_name_bn": "National Board of Revenue (NBR)",
                "office_address_bn": "Segunbagicha, Dhaka-1000",
                "next_action_bn": "Proceed to e-TIN registration",
            },
            "land_deed": {
                "required_docs": [
                    "Khatian (land record)",
                    "Mutation document",
                    "Deed copy",
                    "Both parties' NID copies",
                    "Land tax payment receipt",
                ],
                "optional_docs": [
                    "Mutation copy",
                    "No-Objection Certificate",
                ],
                "estimated_fee": 5000,
                "fee_breakdown": [
                    {"item": "Registration fee", "amount": 3000},
                    {"item": "Stamp paper", "amount": 1000},
                    {"item": "Service charge", "amount": 1000},
                ],
                "estimated_days": 30,
                "office_name_bn": "Sub-Registrar Office",
                "office_address_bn": "Local Sub-Registrar Office",
                "next_action_bn": "Visit the Sub-Registrar Office",
            },
        }

    def detect_intent(self, user_input: str) -> dict:
        """Detect which government service the user is asking about."""
        if not isinstance(user_input, str) or not user_input.strip():
            return {
                "detected_service": None,
                "confidence": 0.0,
                "service_data": None,
                "clarification_needed": True,
                "clarification_question_bn": "Which service would you like to apply for?",
            }

        kb = self.services_kb
        query_lower = user_input.lower()

        # Special case: Lost passport → new, not renewal
        if ("lost" in query_lower or "harano" in query_lower) and (
            "passport" in query_lower
        ):
            service_data = self._get_service_by_id("passport")
            return {
                "detected_service": "passport",
                "confidence": 0.92,
                "service_data": service_data,
                "clarification_needed": False,
                "clarification_question_bn": None,
            }

        # Special case: NID correction
        if ("correction" in query_lower or "correction" in query_lower) and (
            "NID" in user_input or "nid" in query_lower
        ):
            return {
                "detected_service": "nid_correction",
                "confidence": 0.85,
                "service_data": {"id": "nid_correction", "name_bn": "NID Correction", "name_en": "NID Correction"},
                "clarification_needed": True,
                "clarification_question_bn": "Which information do you want to correct in your NID?",
            }

        # Score each service
        scores = {}
        for service_id, keywords in kb.get("intents", {}).items():
            score = 0
            for kw in keywords:
                if kw.lower() in query_lower:
                    score += 1
            if score > 0:
                scores[service_id] = score

        if not scores:
            return {
                "detected_service": None,
                "confidence": 0.0,
                "service_data": None,
                "clarification_needed": True,
                "clarification_question_bn": "Which service would you like? (e.g., passport, trade license, birth certificate)",
            }

        best_service = max(scores, key=scores.get)
        max_score = scores[best_service]
        total_keywords = len(kb.get("intents", {}).get(best_service, []))
        confidence = min(max_score / total_keywords, 1.0)

        clarification_needed = confidence < 0.5
        clarification_question = None
        if clarification_needed:
            service_data = self._get_service_by_id(best_service)
            service_name = service_data.get("name_bn", best_service) if service_data else best_service
            clarification_question = f"Are you applying for **{service_name}**?"

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

    def get_guided_questions(self, service_id: str) -> list:
        """Get step-by-step guided questions for a service."""
        return self.guided_questions.get(service_id, [])

    def validate_field(self, field_name: str, value: str, service_id: str = None) -> dict:
        """Validate a single field value."""
        if not isinstance(value, str) or not value.strip():
            return {
                "valid": False,
                "message_bn": "Please fill in this field",
                "suggestion_bn": None,
            }

        value = value.strip()

        if field_name == "phone":
            cleaned = re.sub(r'[\s\-\+]', '', value)
            is_valid = bool(re.match(r'^01[3-9]\d{8}$', cleaned))
            return {
                "valid": is_valid,
                "message_bn": "Enter a valid 11-digit phone number (01XXXXXXXXX)" if not is_valid else "✅ Phone number is valid",
                "suggestion_bn": "Example: 01712345678" if not is_valid else None,
            }

        if field_name in ("nid", "parent_nid", "seller_nid", "buyer_nid"):
            cleaned = re.sub(r'[\s\-]', '', value)
            is_valid = bool(re.match(r'^\d{10}$|^\d{17}$', cleaned))
            return {
                "valid": is_valid,
                "message_bn": "Enter a valid NID number (10 or 17 digits)" if not is_valid else "✅ NID number is valid",
                "suggestion_bn": "Example: 1234567890" if not is_valid else None,
            }

        if field_name in ("dob", "birth_date", "deed_date"):
            date_patterns = [r'^\d{2}/\d{2}/\d{4}$', r'^\d{4}-\d{2}-\d{2}$']
            is_valid = any(re.match(p, value) for p in date_patterns)

            if is_valid:
                try:
                    separator = '/' if '/' in value else '-'
                    parts = value.split(separator)
                    if len(parts[0]) == 4:
                        datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                    else:
                        datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                except (ValueError, IndexError):
                    is_valid = False

            return {
                "valid": is_valid,
                "message_bn": "Enter a valid date (DD/MM/YYYY)" if not is_valid else "✅ Date is valid",
                "suggestion_bn": "Example: 15/04/1990" if not is_valid else None,
            }

        if not value:
            return {
                "valid": False,
                "message_bn": "Please fill in this field",
                "suggestion_bn": None,
            }

        return {
            "valid": True,
            "message_bn": "✅ Valid",
            "suggestion_bn": None,
        }

    def generate_checklist(self, service_id: str, user_answers: dict = None) -> dict:
        """Generate personalized checklist based on user answers."""
        template = self.checklist_templates.get(service_id, {})

        if not template:
            return {
                "required_docs": [],
                "optional_docs": [],
                "estimated_fee": 0,
                "fee_breakdown": [],
                "estimated_days": 0,
                "office_name_bn": "Office information not available",
                "office_address_bn": "",
                "next_action_bn": "Service information not available",
            }

        required_docs = template.get("required_docs", []).copy()
        optional_docs = template.get("optional_docs", []).copy()

        if user_answers:
            if user_answers.get("has_old_passport") == "No, it is lost":
                required_docs.append("General Diary (GD) copy")
            if user_answers.get("passport_type") == "Urgent (1 year)":
                template = template.copy()
                template["estimated_fee"] = 8500
                template["estimated_days"] = 7
                template["fee_breakdown"] = [
                    {"item": "Passport fee (Urgent)", "amount": 6000},
                    {"item": "Delivery charge", "amount": 500},
                    {"item": "VAT/Tax", "amount": 2000},
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
# FUNCTION: render_ai_chat_demo
# ============================================================
def render_ai_chat_demo(engine: NagarAIEngine = None):
    """Render AI chat demo in Streamlit."""
    if engine is None:
        engine = NagarAIEngine()

    st.markdown("### 🤖 NagarAI Assistant")
    st.caption("Tell us what you need — AI will guide you")

    if "chat_step" not in st.session_state:
        st.session_state.chat_step = "input"
        st.session_state.chat_service = None
        st.session_state.chat_questions = []
        st.session_state.chat_answers = {}
        st.session_state.chat_current_q = 0

    if st.session_state.chat_step == "input":
        user_input = st.text_input(
            "Tell us what you need",
            placeholder="e.g., I want to renew my passport",
            key="chat_user_input",
        )

        if user_input and st.button("➡️ Submit", type="primary"):
            result = engine.detect_intent(user_input)

            if result["detected_service"]:
                st.session_state.chat_service = result["detected_service"]
                st.success(f"✅ Service detected: **{result['service_data']['name_bn']}**")
                st.progress(result["confidence"])
                st.caption(f"Confidence: {result['confidence']:.0%}")

                questions = engine.get_guided_questions(result["detected_service"])
                st.session_state.chat_questions = questions
                st.session_state.chat_step = "questions"
                st.session_state.chat_current_q = 0
                st.rerun()
            else:
                st.warning(result.get("clarification_question_bn", "Try again"))

    elif st.session_state.chat_step == "questions":
        questions = st.session_state.chat_questions
        current_q = st.session_state.chat_current_q

        if current_q < len(questions):
            q = questions[current_q]
            st.markdown(f"**Question {q['step']}: {q['question_bn']}**")
            st.caption(q.get("help_text_bn", ""))

            answer = None
            if q["input_type"] == "radio" and q.get("options_bn"):
                answer = st.radio(q["question_bn"], options=q["options_bn"], key=f"chat_q_{current_q}")
            elif q["input_type"] == "textarea":
                answer = st.text_area(q["question_bn"], key=f"chat_q_{current_q}")
            else:
                answer = st.text_input(q["question_bn"], key=f"chat_q_{current_q}")

            if answer and st.button("✅ Submit Answer", type="primary"):
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

            st.progress((current_q + 1) / len(questions))
            st.caption(f"Question {current_q + 1}/{len(questions)}")
        else:
            st.session_state.chat_step = "checklist"
            st.rerun()

    elif st.session_state.chat_step == "checklist":
        service_id = st.session_state.chat_service
        answers = st.session_state.chat_answers
        checklist = engine.generate_checklist(service_id, answers)

        st.markdown("### 📋 Your Personalized Checklist")
        st.markdown("**📄 Required Documents:**")
        for doc in checklist["required_docs"]:
            st.markdown(f"✅ {doc}")

        if checklist["optional_docs"]:
            st.markdown("**📎 Optional Documents:**")
            for doc in checklist["optional_docs"]:
                st.markdown(f"🔹 {doc}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Estimated Fee", f"৳{checklist['estimated_fee']}")
        col2.metric("Processing Time", f"{checklist['estimated_days']} days")
        col3.metric("Office", checklist["office_name_bn"])

        st.info(f"👉 **Next Step:** {checklist['next_action_bn']}")

        if st.button("🔄 New Application"):
            st.session_state.chat_step = "input"
            st.session_state.chat_service = None
            st.session_state.chat_questions = []
            st.session_state.chat_answers = {}
            st.session_state.chat_current_q = 0
            st.rerun()


# ============================================================
# Legacy functions
# ============================================================
def detect_intent(user_query: str) -> Optional[str]:
    """Legacy function."""
    engine = NagarAIEngine()
    result = engine.detect_intent(user_query)
    return result["detected_service"]


def get_service_info(service_id: str) -> Optional[Dict]:
    """Legacy function."""
    engine = NagarAIEngine()
    return engine._get_service_by_id(service_id)


def validate_form_field(field_name: str, value: str) -> tuple:
    """Legacy function."""
    engine = NagarAIEngine()
    result = engine.validate_field(field_name, value)
    return (result["valid"], result["message_bn"] if not result["valid"] else "")


def get_form_fields_for_service(service_id: str) -> List[Dict]:
    """Legacy function."""
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
    """Legacy function."""
    engine = NagarAIEngine()
    questions = engine.get_guided_questions(service_id)
    for q in questions:
        if q["field_name"] not in completed_fields:
            return f"Next: {q['question_bn']}"
    return None


if __name__ == "__main__":
    print("=== Running AI Engine Tests ===\n")

    engine = NagarAIEngine()

    result1 = engine.detect_intent("passport renewal")
    assert result1["detected_service"] == "passport"
    assert result1["confidence"] > 0
    print("✅ Test 1 PASSED: Intent detection works")

    questions = engine.get_guided_questions("passport")
    assert len(questions) >= 4
    assert questions[0]["step"] == 1
    print("✅ Test 2 PASSED: Guided questions returned")

    result3a = engine.validate_field("phone", "01712345678")
    assert result3a["valid"] == True
    result3b = engine.validate_field("phone", "12345")
    assert result3b["valid"] == False
    print("✅ Test 3 PASSED: Field validation works")

    checklist = engine.generate_checklist("passport")
    assert "required_docs" in checklist
    assert checklist["estimated_fee"] > 0
    assert "office_name_bn" in checklist
    print("✅ Test 4 PASSED: Checklist generated")

    result5 = engine.detect_intent("passport lost, need new one")
    assert result5["detected_service"] == "passport"
    assert result5["confidence"] > 0.8
    print("✅ Test 5 PASSED: Lost passport special case handled")

    print("\n🎉 All 5 AI engine tests PASSED!")
