"""
pages/1_Govt_Service.py — Government service application flow.

6 sections: AI chat → Service details → Guided form → Payment → Appointment
All text in English for international hackathon.
"""

import streamlit as st
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

try:
    from i18n import t
except ImportError as e:
    st.error(f"Module load error: {e}")
    st.stop()

try:
    from ai_engine import NagarAIEngine
except ImportError as e:
    st.error(f"AI Engine error: {e}")
    st.stop()

try:
    from security import PIIRedactor, SessionManager, InputSanitizer, render_security_demo_panel
except ImportError:
    pass

try:
    from payment_mock import calculate_fee
except ImportError:
    pass

st.set_page_config(
    page_title="Government Service — NagarAI",
    page_icon="🏛️",
    layout="wide",
)


def initialize_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    defaults = {
        "govt_step": "ai_chat",
        "selected_service_id": None,
        "service_info": None,
        "intent_confidence": 0.0,
        "form_answers": {},
        "current_question_index": 0,
        "payment_receipt": None,
        "payment_method": None,
        "appointment_date": None,
        "appointment_time": None,
        "appointment_serial": None,
        "doc_checklist": [],
        "session_manager": None,
        "ai_engine": None,
        "pii_redactor": None,
        "input_sanitizer": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if st.session_state.session_manager is None:
        st.session_state.session_manager = SessionManager()
        st.session_state.session_manager.init_session()
    if st.session_state.ai_engine is None:
        st.session_state.ai_engine = NagarAIEngine()
    if st.session_state.pii_redactor is None:
        st.session_state.pii_redactor = PIIRedactor()
    if st.session_state.input_sanitizer is None:
        st.session_state.input_sanitizer = InputSanitizer()


def reset_all():
    keys = ["govt_step", "selected_service_id", "service_info", "intent_confidence",
            "form_answers", "current_question_index", "payment_receipt", "payment_method",
            "appointment_date", "appointment_time", "appointment_serial", "doc_checklist"]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    initialize_state()


def render_sidebar():
    lang = st.session_state.lang
    engine = st.session_state.ai_engine

    st.sidebar.markdown(f"### 🏛️ Government Service")
    st.sidebar.caption("Source: myGov + relevant ministries")

    extended_services = engine.services_kb.get("services", []) + [
        {"id": "passport_new", "name_bn": "New Passport", "fee": 5750},
        {"id": "nid_correction", "name_bn": "NID Correction", "fee": 0},
        {"id": "trade_license_renewal", "name_bn": "Trade License Renewal", "fee": 1000},
    ]

    for svc in extended_services:
        fee_str = f"BDT {svc['fee']}" if svc.get('fee', 0) > 0 else "Free"
        is_selected = st.session_state.selected_service_id == svc["id"]
        btn_type = "primary" if is_selected else "secondary"

        if st.sidebar.button(f"{svc['name_bn']}\n{fee_str}", type=btn_type, use_container_width=True, key=f"svc_btn_{svc['id']}"):
            st.session_state.selected_service_id = svc["id"]
            st.session_state.service_info = svc
            st.session_state.govt_step = "details"
            st.session_state.doc_checklist = []
            st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown("**📈 Impact:**")
    st.sidebar.caption("87,240+ users")
    st.sidebar.caption("40.6% digital applications")
    st.sidebar.caption("BDT 6.8 crore saved")

    st.sidebar.divider()
    try:
        render_security_demo_panel()
    except Exception:
        st.sidebar.caption("🔒 Security panel loading...")

    st.sidebar.divider()
    if st.sidebar.button("🏠 Back to Home", type="secondary"):
        st.switch_page("NagarAI.py")


def render_ai_assistant():
    engine = st.session_state.ai_engine

    st.markdown("### 🤖 AI Assistant — Let us help you find the right service")
    st.caption("Describe what you need in any language")

    user_query = st.text_input(
        "What service do you need?",
        placeholder="e.g., I want to renew my passport",
        label_visibility="collapsed",
        key="ai_query_input",
    )

    if user_query and st.button("🔍 Detect Service", type="primary"):
        result = engine.detect_intent(user_query)

        if result["detected_service"]:
            st.session_state.selected_service_id = result["detected_service"]
            st.session_state.service_info = result["service_data"]
            st.session_state.intent_confidence = result["confidence"]

            conf = result["confidence"]
            service_name = result["service_data"].get("name_bn", result["detected_service"])

            st.success(f"✅ Service detected: **{service_name}**")
            st.progress(conf, text=f"Confidence: {conf:.0%}")

            if result["service_data"] and "required_docs" in result["service_data"]:
                st.session_state.doc_checklist = [
                    {"doc": doc, "checked": False}
                    for doc in result["service_data"]["required_docs"]
                ]

            if st.button("➡️ View Details", type="primary"):
                st.session_state.govt_step = "details"
                st.rerun()
        else:
            clarification = result.get("clarification_question_bn")
            if clarification:
                st.warning(clarification)
            else:
                st.error("❌ Service not detected. Please try again.")


def render_progress_stepper():
    step = st.session_state.govt_step
    step_labels = ["Select Service", "Verify Details", "Payment", "Appointment", "Complete"]
    step_map = {"ai_chat": 0, "details": 1, "form": 2, "payment": 3, "appointment": 4, "done": 4}
    current = step_map.get(step, 0)

    stepper_html = ""
    for i, label in enumerate(step_labels):
        if i <= current:
            stepper_html += f"<span style='color:#006a4e; font-weight:700;'>● {label}</span>"
        else:
            stepper_html += f"<span style='color:#d1d5db;'>○ {label}</span>"
        if i < len(step_labels) - 1:
            stepper_html += " → "

    st.markdown(
        f"<div style='padding: 0.5rem 1rem; background: #f9fafb; border-radius: 8px; "
        f"text-align: center; font-size: 0.9rem;'>{stepper_html}</div>",
        unsafe_allow_html=True,
    )


def render_service_details():
    service_info = st.session_state.service_info
    engine = st.session_state.ai_engine

    if not service_info:
        st.warning("No service selected")
        return

    service_id = service_info.get("id", st.session_state.selected_service_id)
    service_name = service_info.get("name_bn", service_id)
    fee = service_info.get("fee", 0)
    processing_days = service_info.get("processing_days", 0)
    required_docs = service_info.get("required_docs", [])

    st.markdown(f"## 📋 {service_name}")
    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📄 Required Documents")
        st.caption("Check off documents as you gather them")

        if not st.session_state.doc_checklist:
            st.session_state.doc_checklist = [
                {"doc": doc, "checked": False} for doc in required_docs
            ]

        for i, item in enumerate(st.session_state.doc_checklist):
            st.session_state.doc_checklist[i]["checked"] = st.checkbox(
                item["doc"], value=item["checked"], key=f"doc_check_{i}"
            )

        all_checked = all(item["checked"] for item in st.session_state.doc_checklist)
        if all_checked and len(st.session_state.doc_checklist) > 0:
            st.success("✅ All documents ready!")

        st.divider()
        st.markdown("### 💰 Fee Structure")
        regular_fee = fee
        express_fee = int(fee * 1.8) if fee > 0 else 0

        fee_data = [
            {"Type": "Regular", "Fee": f"BDT {regular_fee}", "Processing": f"{processing_days} days"},
            {"Type": "Express", "Fee": f"BDT {express_fee}", "Processing": f"{max(processing_days // 3, 1)} days"},
        ]
        st.table(fee_data)
        st.info(f"⏱️ Estimated processing: **{processing_days} days**")

    with col_right:
        st.markdown("### 🏢 Office Information")

        office_map = {
            "passport": {"name": "Immigration Office, Dhaka", "address": "Agargaon, Sher-e-Bangla Nagar, Dhaka-1207", "hours": "Mon-Thu: 9AM - 5PM", "maps": "Immigration+Office+Agargaon+Dhaka"},
            "trade_license": {"name": "City Corporation Office", "address": "Local City Corporation, Dhaka", "hours": "Mon-Thu: 9AM - 4PM", "maps": "Dhaka+North+City+Corporation"},
            "birth_certificate": {"name": "Union Parishad / Municipality", "address": "Local Union Parishad Office", "hours": "Mon-Thu: 9AM - 5PM", "maps": "Union+Parishad+Dhaka"},
            "tin_certificate": {"name": "National Board of Revenue (NBR)", "address": "Segunbagicha, Dhaka-1000", "hours": "Mon-Thu: 9AM - 5PM", "maps": "NBR+Segunbagicha+Dhaka"},
            "land_deed": {"name": "Sub-Registrar Office", "address": "Local Sub-Registrar Office", "hours": "Mon-Thu: 10AM - 4PM", "maps": "Sub+Registrar+Office+Dhaka"},
        }

        office = office_map.get(service_id, {"name": "Government Office", "address": "Local Office", "hours": "Mon-Thu: 9AM - 5PM", "maps": "Government+Office+Dhaka"})

        st.markdown(f"**🏛️ {office['name']}**")
        st.caption(f"📍 {office['address']}")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={office['maps']}"
        st.markdown(f"[🗺️ View on Google Maps]({maps_url})")
        st.caption(f"🕐 {office['hours']}")

        st.divider()
        st.info(f"🟡 Today's estimated crowd: **Medium**")
        st.caption(f"📅 Last verified: Today, {datetime.now().strftime('%d/%m/%Y')}")

    st.divider()
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("⬅️ Detect Again", type="secondary"):
            st.session_state.govt_step = "ai_chat"
            st.rerun()
    with col_btn3:
        if st.button("➡️ Fill Application Form", type="primary"):
            questions = engine.get_guided_questions(service_id)
            if questions:
                st.session_state.govt_step = "form"
                st.session_state.current_question_index = 0
                st.session_state.form_answers = {}
            else:
                st.warning("No application form available for this service")
            st.rerun()


def render_guided_form():
    engine = st.session_state.ai_engine
    service_id = st.session_state.selected_service_id

    questions = engine.get_guided_questions(service_id)
    if not questions:
        st.warning("No guided form available for this service")
        st.session_state.govt_step = "details"
        return

    current_idx = st.session_state.current_question_index
    total = len(questions)
    progress = current_idx / total
    st.progress(progress, text=f"Question {current_idx + 1}/{total}")

    st.markdown(f"### 📝 Application Form — {st.session_state.service_info['name_bn']}")
    st.divider()

    if current_idx < total:
        q = questions[current_idx]
        st.markdown(f"#### Question {q['step']}: {q['question_bn']}")
        if q.get("help_text_bn"):
            st.caption(q["help_text_bn"])

        answer = None
        field_key = f"form_q_{current_idx}"

        if q["input_type"] == "radio" and q.get("options_bn"):
            answer = st.radio(q["question_bn"], options=q["options_bn"], key=field_key, label_visibility="collapsed")
        elif q["input_type"] == "textarea":
            answer = st.text_area(q["question_bn"], key=field_key, placeholder="Type here...", label_visibility="collapsed")
        elif q["input_type"] == "date":
            answer = st.date_input(q["question_bn"], key=field_key, label_visibility="collapsed")
            answer = str(answer) if answer else ""
        else:
            answer = st.text_input(q["question_bn"], key=field_key, placeholder="Type here...", label_visibility="collapsed")

        if answer:
            validation = engine.validate_field(q["field_name"], str(answer))
            if validation["valid"]:
                st.success(f"✅ {validation['message_bn']}")
            else:
                st.error(f"❌ {validation['message_bn']}")
                if validation.get("suggestion_bn"):
                    st.caption(f"💡 {validation['suggestion_bn']}")

        col_prev, col_next = st.columns([1, 2])
        with col_prev:
            if current_idx > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.current_question_index -= 1
                    st.rerun()
        with col_next:
            if answer:
                validation = engine.validate_field(q["field_name"], str(answer))
                if validation["valid"]:
                    st.session_state.form_answers[q["field_name"]] = str(answer)
                    st.session_state.current_question_index += 1
                    st.session_state.session_manager.log_action(f"form_field_{q['field_name']}")
                    st.rerun()
                else:
                    st.button("✅ Submit", type="primary", disabled=True)
            else:
                st.button("✅ Submit", type="primary", disabled=True)
    else:
        st.success("🎉 All questions answered!")
        st.markdown("**Your responses:**")
        for key, value in st.session_state.form_answers.items():
            st.caption(f"• **{key}:** {value}")

        if st.button("➡️ Proceed to Payment", type="primary"):
            st.session_state.govt_step = "payment"
            st.session_state.session_manager.log_action("form_completed")
            st.rerun()


def render_payment():
    service_info = st.session_state.service_info
    engine = st.session_state.ai_engine
    service_id = st.session_state.selected_service_id

    fee = service_info.get("fee", 0)
    checklist = engine.generate_checklist(service_id, st.session_state.form_answers)
    estimated_fee = checklist.get("estimated_fee", fee)

    st.markdown("## 💳 Payment")
    st.divider()

    st.markdown("### 📋 Fee Summary")
    fee_breakdown = checklist.get("fee_breakdown", [])
    if fee_breakdown:
        for item in fee_breakdown:
            st.markdown(f"• {item['item']}: **BDT {item['amount']}**")
    else:
        st.markdown(f"• Service fee: **BDT {estimated_fee}**")

    st.divider()
    st.markdown(f"**Total: BDT {estimated_fee}**")

    if estimated_fee > 0:
        st.markdown("### Choose payment method")
        payment_method = st.radio(
            "Payment method",
            options=["bKash", "Nagad", "Bank Transfer"],
            format_func=lambda x: {"bKash": "📱 bKash", "Nagad": "🟠 Nagad", "Bank Transfer": "🏦 Bank Transfer"}.get(x, x),
            key="payment_method_radio",
        )
        st.session_state.payment_method = payment_method
    else:
        payment_method = "Free"
        st.session_state.payment_method = "Free"

    st.divider()

    if estimated_fee == 0:
        st.success("✅ This service is free!")
        st.session_state.payment_receipt = {"status": "free", "amount_bdt": 0, "transaction_id": f"NGA-{random.randint(10000000, 99999999)}", "service": service_info.get("name_bn", service_id)}
    else:
        if st.button(f"💳 Pay Now (Demo) — BDT {estimated_fee}", type="primary"):
            with st.spinner("Processing payment..."):
                txn_id = f"NGA-{random.randint(10000000, 99999999)}"
                st.session_state.payment_receipt = {
                    "status": "success", "amount_bdt": estimated_fee,
                    "transaction_id": txn_id, "service": service_info.get("name_bn", service_id),
                    "method": payment_method, "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }

    if st.session_state.payment_receipt:
        receipt = st.session_state.payment_receipt
        st.divider()
        st.success("✅ Payment Complete (Demo)")

        st.markdown(f"""
        **Receipt:**
        - Transaction ID: `{receipt['transaction_id']}`
        - Amount: BDT {receipt['amount_bdt']}
        - Method: {receipt.get('method', 'N/A')}
        - Time: {receipt.get('timestamp', 'N/A')}
        - Status: ✅ Complete (Demo)
        """)
        st.warning("⚠️ Please save this receipt")

        st.divider()
        if st.button("➡️ Confirm Appointment", type="primary"):
            st.session_state.govt_step = "appointment"
            st.session_state.session_manager.log_action("payment_completed")
            st.rerun()


def render_appointment():
    service_info = st.session_state.service_info
    engine = st.session_state.ai_engine
    service_id = st.session_state.selected_service_id

    if not st.session_state.appointment_date:
        today = datetime.now()
        appt = today + timedelta(days=3)
        while appt.weekday() >= 4:
            appt += timedelta(days=1)
        st.session_state.appointment_date = appt.strftime("%d/%m/%Y")
        st.session_state.appointment_time = "10:00 AM"
        st.session_state.appointment_serial = f"PAS-{random.randint(1000, 9999)}"

    checklist = engine.generate_checklist(service_id, st.session_state.form_answers)
    office_name = checklist.get("office_name_bn", service_info.get("authority", "N/A"))
    office_address = checklist.get("office_address_bn", "")
    required_docs = checklist.get("required_docs", [])

    st.balloons()
    st.success("🎉 Congratulations! Your appointment is confirmed!")

    st.divider()
    st.markdown("### 📅 Appointment Details")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        🗓️ **Date:** {st.session_state.appointment_date}
        ⏰ **Time:** {st.session_state.appointment_time}
        🔢 **Serial:** `{st.session_state.appointment_serial}`
        """)
    with col2:
        st.markdown(f"""
        🏛️ **Office:** {office_name}
        📍 **Address:** {office_address}
        💳 **Payment:** BDT {checklist.get('estimated_fee', service_info.get('fee', 0))}
        """)

    st.divider()
    st.markdown("### 📋 Please bring:")
    for doc in required_docs:
        st.markdown(f"📄 {doc}")

    st.divider()
    st.markdown("### 📱 SMS Confirmation:")
    sms_text = (
        f"NagarAI: Your appointment for {service_info.get('name_bn', service_id)} "
        f"is confirmed on {st.session_state.appointment_date} at {st.session_state.appointment_time}. "
        f"Serial: {st.session_state.appointment_serial}. Venue: {office_name}. "
        f"Please bring all required documents. Thank you."
    )
    st.code(sms_text, language=None)

    st.divider()
    st.info("🔒 No personal data is being stored")

    st.divider()
    if st.button("🔄 Start Over", type="primary"):
        reset_all()
        st.rerun()

    if st.button("🏠 Back to Home"):
        st.switch_page("NagarAI.py")


def main():
    initialize_state()
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "nagarai_style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_sidebar()

    if st.session_state.govt_step != "ai_chat":
        render_progress_stepper()

    step = st.session_state.govt_step
    if step == "ai_chat":
        render_ai_assistant()
    elif step == "details":
        render_service_details()
    elif step == "form":
        render_guided_form()
    elif step == "payment":
        render_payment()
    elif step == "appointment":
        render_appointment()
    else:
        st.session_state.govt_step = "ai_chat"
        st.rerun()


if __name__ == "__main__":
    main()
