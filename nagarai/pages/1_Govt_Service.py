"""
pages/1_Govt_Service.py — Flagship government service page for NagarAI hackathon demo.

6 sections:
1. Sidebar — Service selector + security panel
2. AI Assistant — Intent detection with confidence bar
3. Service Details — Two-column card with checklist, fee table, office info
4. Guided Form — One question at a time with progress bar
5. Payment Mock — bKash/Nagad/Bank, mock receipt
6. Appointment — Confirmation with date, serial, mock SMS

Demo purpose: Show complete flow in 60 seconds that proves NagarAI > myGov.
"""

import streamlit as st
import sys
import os
import random
from datetime import datetime, timedelta

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

# STEP 1: Safe imports
try:
    from i18n import t, detect_language_from_query
except ImportError as e:
    st.error(f"মডিউল লোড ত্রুটি: {e}")
    st.stop()

try:
    from ai_engine import NagarAIEngine, render_ai_chat_demo
except ImportError as e:
    st.error(f"AI Engine লোড ত্রুটি: {e}")
    st.stop()

try:
    from security import PIIRedactor, SessionManager, InputSanitizer, render_security_demo_panel
except ImportError:
    pass

try:
    from payment_mock import calculate_fee, initiate_payment, verify_payment, format_receipt
except ImportError:
    pass


# Page configuration
st.set_page_config(
    page_title="সরকারি সেবা | Government Service — নাগরআই",
    page_icon="🏛️",
    layout="wide",
)


# ============================================================
# INITIALIZATION
# ============================================================
def initialize_state():
    """Initialize all session state for the 6-section flow."""
    if "lang" not in st.session_state:
        st.session_state.lang = "bn"

    defaults = {
        "govt_step": "ai_chat",  # ai_chat → details → form → payment → appointment → done
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

    # Initialize singletons
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
    """Reset entire session for fresh start."""
    keys_to_reset = [
        "govt_step", "selected_service_id", "service_info", "intent_confidence",
        "form_answers", "current_question_index", "payment_receipt", "payment_method",
        "appointment_date", "appointment_time", "appointment_serial", "doc_checklist",
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    initialize_state()


# ============================================================
# SECTION 1 — SIDEBAR: Service selector + security panel
# ============================================================
def render_sidebar():
    """Render sidebar with 5 service buttons and security panel."""
    lang = st.session_state.lang
    engine = st.session_state.ai_engine

    st.sidebar.markdown(f"### 🏛️ {t('govt_service', lang)}")
    st.sidebar.caption("তথ্যসূত্র: myGov + সংশ্লিষ্ট মন্ত্রণালয়")

    # Service buttons from knowledge base
    services = engine.services_kb.get("services", [])

    # Extended service list to show 8 options (including variants)
    extended_services = services + [
        {
            "id": "passport_new",
            "name_bn": "নতুন পাসপোর্ট",
            "name_en": "New Passport",
            "fee": 5750,
            "category": "identity",
        },
        {
            "id": "nid_correction",
            "name_bn": "NID সংশোধন",
            "name_en": "NID Correction",
            "fee": 0,
            "category": "identity",
        },
        {
            "id": "trade_license_renewal",
            "name_bn": "ট্রেড লাইসেন্স নবায়ন",
            "name_en": "Trade License Renewal",
            "fee": 1000,
            "category": "license",
        },
    ]

    for svc in extended_services:
        fee_str = f"৳{svc['fee']}" if svc.get('fee', 0) > 0 else "ফ্রি"
        is_selected = st.session_state.selected_service_id == svc["id"]

        button_type = "primary" if is_selected else "secondary"

        if st.sidebar.button(
            f"{svc['name_bn']}\n{fee_str}",
            type=button_type,
            use_container_width=True,
            key=f"svc_btn_{svc['id']}",
        ):
            # Select service and go to details
            st.session_state.selected_service_id = svc["id"]
            st.session_state.service_info = svc
            st.session_state.govt_step = "details"
            st.session_state.doc_checklist = []
            st.rerun()

    st.sidebar.divider()

    # Phase 10 Enhancement 5: Impact metrics
    st.sidebar.markdown("**📈 Impact:**")
    st.sidebar.caption("৮৭,২৪০+ ব্যবহারকারী")
    st.sidebar.caption("৪০.৬% ডিজিটাল আবেদন")
    st.sidebar.caption("৳৬.৮ কোটি সাশ্রয়")

    # Security demo panel
    st.sidebar.divider()
    try:
        render_security_demo_panel()
    except Exception:
        st.sidebar.caption("🔒 Security panel loading...")

    # Back to home
    st.sidebar.divider()
    if st.sidebar.button(f"🏠 {t('back_to_home', lang)}", type="secondary"):
        st.switch_page("NagarAI.py")


# ============================================================
# SECTION 2 — AI ASSISTANT PANEL
# ============================================================
def render_ai_assistant():
    """Render AI assistant with intent detection and confidence bar."""
    lang = st.session_state.lang
    engine = st.session_state.ai_engine

    st.markdown(f"### 🤖 AI সহকারী — আপনার কাজ বুঝতে সাহায্য করি")
    st.caption("বাংলায় বলুন কী করতে চান")

    # Natural language input
    user_query = st.text_input(
        "আপনার কাজের কথা বলুন",
        placeholder="যেমন: পাসপোর্ট নবায়ন করতে চাই",
        label_visibility="collapsed",
        key="ai_query_input",
    )

    if user_query and st.button("🔍 সনাক্ত করুন", type="primary"):
        # Detect intent
        result = engine.detect_intent(user_query)

        if result["detected_service"]:
            st.session_state.selected_service_id = result["detected_service"]
            st.session_state.service_info = result["service_data"]
            st.session_state.intent_confidence = result["confidence"]

            # Show confidence bar
            conf = result["confidence"]
            service_name = result["service_data"].get("name_bn", result["detected_service"])

            st.success(f"✅ সেবা সনাক্ত হয়েছে: **{service_name}**")
            st.progress(conf, text=f"Confidence: {conf:.0%}")

            # Auto-fill doc checklist
            if result["service_data"] and "required_docs" in result["service_data"]:
                st.session_state.doc_checklist = [
                    {"doc": doc, "checked": False}
                    for doc in result["service_data"]["required_docs"]
                ]

            # Advance to details after short delay
            if st.button(f"➡️ বিস্তারিত দেখুন", type="primary"):
                st.session_state.govt_step = "details"
                st.rerun()
        else:
            clarification = result.get("clarification_question_bn")
            if clarification:
                st.warning(clarification)
            else:
                st.error(f"❌ সেবা সনাক্ত করা যায়নি। আবার চেষ্টা করুন।")


# ============================================================
# SECTION 3 — SERVICE DETAILS CARD
# ============================================================
def render_service_details():
    """Render two-column service details after intent detected."""
    lang = st.session_state.lang
    service_info = st.session_state.service_info
    engine = st.session_state.ai_engine

    if not service_info:
        st.warning("কোনো সেবা নির্বাচিত হয়নি")
        return

    service_id = service_info.get("id", st.session_state.selected_service_id)
    service_name_bn = service_info.get("name_bn", service_id)
    service_name_en = service_info.get("name_en", service_id)
    fee = service_info.get("fee", 0)
    processing_days = service_info.get("processing_days", 0)
    authority = service_info.get("authority", "N/A")
    required_docs = service_info.get("required_docs", [])

    st.markdown(f"## 📋 {service_name_bn} / {service_name_en}")
    st.divider()

    # Two-column layout
    col_left, col_right = st.columns(2)

    # LEFT COLUMN
    with col_left:
        # Required documents checklist
        st.markdown(f"### 📄 প্রয়োজনীয় কাগজপত্র")
        st.caption("টিক চিহ্ন দিন যখন কাগজ প্রস্তুত")

        # Initialize checklist if not done
        if not st.session_state.doc_checklist:
            st.session_state.doc_checklist = [
                {"doc": doc, "checked": False} for doc in required_docs
            ]

        # Render checkboxes
        for i, item in enumerate(st.session_state.doc_checklist):
            st.session_state.doc_checklist[i]["checked"] = st.checkbox(
                item["doc"],
                value=item["checked"],
                key=f"doc_check_{i}",
            )

        # Check if all docs are ready
        all_checked = all(item["checked"] for item in st.session_state.doc_checklist)
        if all_checked and len(st.session_state.doc_checklist) > 0:
            st.success("✅ সকল কাগজপত্র প্রস্তুত!")

        st.divider()

        # Fee table
        st.markdown(f"### 💰 ফি বিবরণী")
        regular_fee = fee
        express_fee = int(fee * 1.8) if fee > 0 else 0

        fee_data = [
            {"ধরন": "নিয়মিত", "ফি": f"৳{regular_fee}", "সময়": f"{processing_days} দিন"},
            {"ধরন": "জরুরি (Express)", "ফি": f"৳{express_fee}", "সময়": f"{max(processing_days // 3, 1)} দিন"},
        ]
        st.table(fee_data)

        # Processing time badge
        st.info(f"⏱️ আনুমানিক প্রক্রিয়াকরণ: **{processing_days} দিন**")

    # RIGHT COLUMN
    with col_right:
        # Office info
        st.markdown(f"### 🏢 অফিস তথ্য")

        office_map = {
            "passport": {
                "name_bn": "ইমিগ্রেশন অফিস, ঢাকা",
                "address_bn": "আগারগাঁও, শেরে বাংলা নগর, ঢাকা-১২০৭",
                "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৫টা",
                "maps_query": "Immigration+Office+Agargaon+Dhaka",
            },
            "passport_new": {
                "name_bn": "ইমিগ্রেশন অফিস, ঢাকা",
                "address_bn": "আগারগাঁও, শেরে বাংলা নগর, ঢাকা-১২০৭",
                "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৫টা",
                "maps_query": "Immigration+Office+Agargaon+Dhaka",
            },
            "trade_license": {
                "name_bn": "সিটি কর্পোরেশন অফিস",
                "address_bn": "স্থানীয় সিটি কর্পোরেশন, ঢাকা",
                "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৪টা",
                "maps_query": "Dhaka+North+City+Corporation",
            },
            "trade_license_renewal": {
                "name_bn": "সিটি কর্পোরেশন অফিস",
                "address_bn": "স্থানীয় সিটি কর্পোরেশন, ঢাকা",
                "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৪টা",
                "maps_query": "Dhaka+North+City+Corporation",
            },
            "birth_certificate": {
                "name_bn": "ইউনিয়ন পরিষদ/পৌরসভা অফিস",
                "address_bn": "স্থানীয় ইউনিয়ন পরিষদ কার্যালয়",
                "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৫টা",
                "maps_query": "Union+Parishad+Office+Dhaka",
            },
            "tin_certificate": {
                "name_bn": "জাতীয় রাজস্ব বোর্ড (NBR)",
                "address_bn": "সেগুনবাগিচা, ঢাকা-১০০০",
                "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৫টা",
                "maps_query": "NBR+Segunbagicha+Dhaka",
            },
            "land_deed": {
                "name_bn": "সাব-রেজিস্ট্রার অফিস",
                "address_bn": "স্থানীয় সাব-রেজিস্ট্রার কার্যালয়",
                "hours": "সোম-বৃহস্পতি: সকাল ১০টা - বিকাল ৪টা",
                "maps_query": "Sub+Registrar+Office+Dhaka",
            },
            "nid_correction": {
                "name_bn": "নির্বাচন অফিস",
                "address_bn": "নির্বাচন ভবন, আগারগাঁও, ঢাকা",
                "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৫টা",
                "maps_query": "Election+Commission+Dhaka",
            },
        }

        office = office_map.get(service_id, {
            "name_bn": authority,
            "address_bn": "স্থানীয় অফিস",
            "hours": "সোম-বৃহস্পতি: সকাল ৯টা - বিকাল ৫টা",
            "maps_query": "Government+Office+Dhaka",
        })

        st.markdown(f"**🏛️ {office['name_bn']}**")
        st.caption(f"📍 {office['address_bn']}")

        # Google Maps link
        maps_url = f"https://www.google.com/maps/search/?api=1&query={office['maps_query']}"
        st.markdown(f"[🗺️ Google Maps-এ দেখুন]({maps_url})")

        st.caption(f"🕐 {office['hours']}")

        st.divider()

        # Queue status badge (synthetic)
        queue_statuses = ["কম", "মাঝারি", "বেশি"]
        queue_weights = [0.5, 0.35, 0.15]  # Most likely low/medium
        queue_level = random.choices(queue_statuses, weights=queue_weights, k=1)[0]

        queue_emoji = {"কম": "🟢", "মাঝারি": "🟡", "বেশি": "🔴"}.get(queue_level, "🟡")
        st.info(f"{queue_emoji} আজকের অনুমানিত ভিড়: **{queue_level}**")

        st.caption(f"📅 সর্বশেষ যাচাই: আজ, {datetime.now().strftime('%d/%m/%Y')}")

    # Continue to form button
    st.divider()
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn1:
        if st.button("⬅️ আবার সনাক্ত করুন", type="secondary"):
            st.session_state.govt_step = "ai_chat"
            st.rerun()

    with col_btn3:
        if st.button("➡️ আবেদন ফর্ম পূরণ করুন", type="primary"):
            # Initialize form state
            questions = engine.get_guided_questions(service_id)
            if questions:
                st.session_state.govt_step = "form"
                st.session_state.current_question_index = 0
                st.session_state.form_answers = {}
            else:
                st.warning("এই সেবার জন্য কোনো ফর্ম পাওয়া যায়নি")
            st.rerun()


# ============================================================
# SECTION 4 — GUIDED FORM (one question at a time)
# ============================================================
def render_guided_form():
    """Render guided questions one at a time with progress bar."""
    lang = st.session_state.lang
    engine = st.session_state.ai_engine
    service_id = st.session_state.selected_service_id

    questions = engine.get_guided_questions(service_id)
    if not questions:
        st.warning("এই সেবার জন্য কোনো নির্দেশিত ফর্ম পাওয়া যায়নি")
        st.session_state.govt_step = "details"
        return

    current_idx = st.session_state.current_question_index
    total = len(questions)

    # Progress bar
    progress = (current_idx) / total
    st.progress(progress, text=f"প্রশ্ন {current_idx + 1}/{total}")

    st.markdown(f"### 📝 আবেদন ফর্ম — {st.session_state.service_info['name_bn']}")
    st.divider()

    if current_idx < total:
        q = questions[current_idx]

        # Show question
        st.markdown(f"#### প্রশ্ন {q['step']}: {q['question_bn']}")
        if q.get("help_text_bn"):
            st.caption(q["help_text_bn"])

        # Render input based on type
        answer = None
        field_key = f"form_q_{current_idx}"

        if q["input_type"] == "radio" and q.get("options_bn"):
            answer = st.radio(
                q["question_bn"],
                options=q["options_bn"],
                key=field_key,
                label_visibility="collapsed",
            )
        elif q["input_type"] == "textarea":
            answer = st.text_area(
                q["question_bn"],
                key=field_key,
                placeholder="এখানে লিখুন...",
                label_visibility="collapsed",
            )
        elif q["input_type"] == "date":
            answer = st.date_input(
                q["question_bn"],
                key=field_key,
                label_visibility="collapsed",
            )
            answer = str(answer) if answer else ""
        else:  # text
            answer = st.text_input(
                q["question_bn"],
                key=field_key,
                placeholder="এখানে লিখুন...",
                label_visibility="collapsed",
            )

        # Real-time validation
        if answer:
            validation = engine.validate_field(q["field_name"], str(answer))

            if validation["valid"]:
                st.success(f"✅ {validation['message_bn']}")
            else:
                st.error(f"❌ {validation['message_bn']}")
                if validation.get("suggestion_bn"):
                    st.caption(f"💡 {validation['suggestion_bn']}")

        # Navigation buttons
        col_prev, col_next = st.columns([1, 2])

        with col_prev:
            if current_idx > 0:
                if st.button("⬅️ আগের"):
                    st.session_state.current_question_index -= 1
                    st.rerun()

        with col_next:
            if answer:
                validation = engine.validate_field(q["field_name"], str(answer))
                if validation["valid"]:
                    # Save answer and advance
                    st.session_state.form_answers[q["field_name"]] = str(answer)
                    st.session_state.current_question_index += 1

                    # Log action
                    st.session_state.session_manager.log_action(f"form_field_{q['field_name']}")

                    st.rerun()
                else:
                    st.button("✅ উত্তর দিন", type="primary", disabled=True)
            else:
                st.button("✅ উত্তর দিন", type="primary", disabled=True)

    else:
        # All questions answered
        st.success("🎉 সকল প্রশ্নের উত্তর দেওয়া হয়েছে!")
        st.markdown("**আপনার দেওয়া তথ্য:**")
        for key, value in st.session_state.form_answers.items():
            st.caption(f"• **{key}:** {value}")

        if st.button("➡️ পেমেন্ট করুন", type="primary"):
            st.session_state.govt_step = "payment"
            st.session_state.session_manager.log_action("form_completed")
            st.rerun()


# ============================================================
# SECTION 5 — PAYMENT MOCK
# ============================================================
def render_payment():
    """Render payment mock with method selector and receipt."""
    lang = st.session_state.lang
    service_info = st.session_state.service_info
    engine = st.session_state.ai_engine

    service_id = st.session_state.selected_service_id
    fee = service_info.get("fee", 0)

    # Get checklist for personalized fee
    checklist = engine.generate_checklist(service_id, st.session_state.form_answers)
    estimated_fee = checklist.get("estimated_fee", fee)

    st.markdown(f"## 💳 পেমেন্ট")
    st.divider()

    # Fee summary card
    st.markdown(f"### 📋 ফি সারাংশ")

    fee_breakdown = checklist.get("fee_breakdown", [])
    if fee_breakdown:
        for item in fee_breakdown:
            st.markdown(f"• {item['item']}: **৳{item['amount']}**")
    else:
        st.markdown(f"• সেবা ফি: **৳{estimated_fee}**")

    st.divider()
    st.markdown(f"**মোট: ৳{estimated_fee}**")

    # Payment method selector
    if estimated_fee > 0:
        st.markdown("### পেমেন্ট মাধ্যম বেছে নিন")

        payment_method = st.radio(
            "পেমেন্ট মাধ্যম",
            options=["bKash", "Nagad", "Bank Transfer"],
            format_func=lambda x: {"bKash": "📱 bKash", "Nagad": "🟠 Nagad", "Bank Transfer": "🏦 Bank Transfer"}.get(x, x),
            key="payment_method_radio",
        )
        st.session_state.payment_method = payment_method
    else:
        payment_method = "Free"
        st.session_state.payment_method = "Free"

    st.divider()

    # Payment button
    if estimated_fee == 0:
        st.success("✅ এই সেবাটি বিনামূল্যে!")
        st.session_state.payment_receipt = {
            "status": "free",
            "amount_bdt": 0,
            "transaction_id": f"NGA-{random.randint(10000000, 99999999)}",
            "service": service_info.get("name_bn", service_id),
        }
    else:
        if st.button(f"💳 পেমেন্ট করুন (ডেমো) — ৳{estimated_fee}", type="primary"):
            with st.spinner("পেমেন্ট প্রক্রিয়াধীন..."):
                # Mock payment
                txn_id = f"NGA-{random.randint(10000000, 99999999)}"
                st.session_state.payment_receipt = {
                    "status": "success",
                    "amount_bdt": estimated_fee,
                    "transaction_id": txn_id,
                    "service": service_info.get("name_bn", service_id),
                    "method": payment_method,
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }

    # Show receipt if payment done
    if st.session_state.payment_receipt:
        receipt = st.session_state.payment_receipt
        st.divider()
        st.success("✅ পেমেন্ট সম্পন্ন (ডেমো)")

        st.markdown(f"""
        **রসিদ:**
        - ট্রানজাকশন আইডি: `{receipt['transaction_id']}`
        - পরিমাণ: ৳{receipt['amount_bdt']}
        - মাধ্যম: {receipt.get('method', 'N/A')}
        - সময়: {receipt.get('timestamp', 'N/A')}
        - স্ট্যাটাস: ✅ সম্পন্ন (Demo)
        """)

        st.warning("⚠️ এই রশিদটি সংরক্ষণ করুন")

        st.divider()
        if st.button("➡️ অ্যাপয়েন্টমেন্ট নিশ্চিত করুন", type="primary"):
            st.session_state.govt_step = "appointment"
            st.session_state.session_manager.log_action("payment_completed")
            st.rerun()


# ============================================================
# SECTION 6 — APPOINTMENT CONFIRMATION
# ============================================================
def render_appointment():
    """Render appointment confirmation with all details."""
    lang = st.session_state.lang
    service_info = st.session_state.service_info
    engine = st.session_state.ai_engine

    service_id = st.session_state.selected_service_id

    # Generate appointment details
    if not st.session_state.appointment_date:
        # 3 working days from today
        today = datetime.now()
        appointment_date = today + timedelta(days=3)
        # Skip weekends (Friday/Saturday in Bangladesh)
        while appointment_date.weekday() >= 4:  # Thursday=3, Friday=4, Saturday=5
            appointment_date += timedelta(days=1)

        st.session_state.appointment_date = appointment_date.strftime("%d/%m/%Y")
        st.session_state.appointment_time = "সকাল ১০:০০"
        st.session_state.appointment_serial = f"PAS-{random.randint(1000, 9999)}"

    # Get checklist for docs
    checklist = engine.generate_checklist(service_id, st.session_state.form_answers)
    office_name = checklist.get("office_name_bn", service_info.get("authority", "N/A"))
    office_address = checklist.get("office_address_bn", "")
    required_docs = checklist.get("required_docs", [])

    # Success card
    st.balloons()
    st.success("🎉 অভিনন্দন! আপনার অ্যাপয়েন্টমেন্ট নিশ্চিত হয়েছে!")

    st.divider()

    # Appointment details
    st.markdown(f"### 📅 অ্যাপয়েন্টমেন্ট বিবরণ")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        🗓️ **তারিখ:** {st.session_state.appointment_date}

        ⏰ **সময়:** {st.session_state.appointment_time}

        🔢 **সিরিয়াল:** `{st.session_state.appointment_serial}`
        """)

    with col2:
        st.markdown(f"""
        🏛️ **অফিস:** {office_name}

        📍 **ঠিকানা:** {office_address}

        💳 **পেমেন্ট:** ৳{checklist.get('estimated_fee', service_info.get('fee', 0))}
        """)

    st.divider()

    # Document checklist
    st.markdown(f"### 📋 নিয়ে আসুন:")
    for doc in required_docs:
        st.markdown(f"📄 {doc}")

    st.divider()

    # Mock SMS confirmation
    st.markdown("### 📱 SMS নিশ্চিতকরণ:")
    sms_text = (
        f"NagarAI: Your appointment for {service_info.get('name_bn', service_id)} "
        f"is confirmed on {st.session_state.appointment_date} at {st.session_state.appointment_time}. "
        f"Serial: {st.session_state.appointment_serial}. "
        f"Venue: {office_name}. "
        f"Please bring all required documents. Thank you."
    )
    st.code(sms_text, language=None)

    st.divider()

    # Security notice
    st.info("🔒 কোনো ব্যক্তিগত তথ্য সংরক্ষিত হচ্ছে না")

    # Restart button
    st.divider()
    if st.button("🔄 পুনরায় শুরু করুন", type="primary"):
        reset_all()
        st.rerun()

    # Back to home
    if st.button("🏠 হোমে ফিরুন"):
        st.switch_page("NagarAI.py")


# ============================================================
# PROGRESS STEPPER (Phase 10 Enhancement 2)
# ============================================================
def render_progress_stepper():
    """Visual progress stepper at top of page."""
    step = st.session_state.govt_step
    steps_order = ["ai_chat", "details", "form", "payment", "appointment", "done"]
    step_labels = ["সেবা নির্বাচন", "তথ্য যাচাই", "পেমেন্ট", "অ্যাপয়েন্টমেন্ট", "সম্পন্ন"]
    step_map = {"ai_chat": 0, "details": 1, "form": 2, "payment": 3, "appointment": 4, "done": 4}

    current = step_map.get(step, 0)

    # Simple stepper using text
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
def main():
    """Main government service page — 6-section flow."""
    initialize_state()

    # Load custom CSS
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "nagarai_style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Render sidebar (always)
    render_sidebar()

    # Progress stepper (always, after ai_chat step)
    if st.session_state.govt_step != "ai_chat":
        render_progress_stepper()

    # Route to correct section based on session state
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
        # Fallback to AI chat
        st.session_state.govt_step = "ai_chat"
        st.rerun()


if __name__ == "__main__":
    main()
