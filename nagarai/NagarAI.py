"""
NagarAI.py — Landing page with Phase 9+10 enhancements.

Enhancements:
- Dramatic hero section (Phase 10 Enhancement 1)
- Live counter animation
- Bengali font support via Google Fonts
- Demo controls in sidebar
- Safe imports
"""

import streamlit as st
import sys
import os
import time

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

# STEP 1: Safe imports
try:
    from i18n import t, get_available_languages, detect_language_from_query
except ImportError as e:
    st.error(f"মডিউল লোড ত্রুটি: {e}")
    st.stop()

try:
    from security import get_session_stats, create_session, purge_session
except ImportError:
    pass


# Page configuration
st.set_page_config(
    page_title="নাগরআই | NagarAI — এক অ্যাপ, দুই সেবা",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# STEP 2: Global session state
def init_global_state():
    """Ensure global session state defaults."""
    defaults = {
        "current_service": None,
        "form_step": 0,
        "form_answers": {},
        "payment_done": False,
        "appointment_done": False,
        "demo_mode": True,
        "lang": "bn",
        "session_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# STEP 3: Initialize
init_global_state()

if st.session_state.session_id is None:
    st.session_state.session_id = "nagarai_demo_session"
    try:
        create_session(st.session_state.session_id)
    except Exception:
        pass


def render_header():
    """Phase 10 Enhancement 1: Dramatic hero section with live counter."""
    lang = st.session_state.lang

    # Google Fonts import for Bengali
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )

    # Hero section
    st.markdown("""
<div style='text-align:center; padding: 2rem 0;'>
  <h1 style='font-size:3rem; font-weight:700; color:#006a4e; font-family: "Noto Sans Bengali", Arial, sans-serif;'>নাগরআই</h1>
  <p style='font-size:1.3rem; color:#374151;'>এক অ্যাপ, দুই সেবা</p>
  <p style='font-size:0.9rem; color:#6B7280; margin-top:0.5rem;'>
    সরকারি সেবা সহজ করো | জরুরি সাহায্য তাৎক্ষণিক পাও
  </p>
</div>
""", unsafe_allow_html=True)

    # Language toggle
    col1, col2 = st.columns([4, 1])
    with col2:
        current_lang = st.session_state.lang
        new_lang = "en" if current_lang == "bn" else "bn"
        if st.button(t("language_toggle", current_lang), type="secondary", use_container_width=True):
            st.session_state.lang = new_lang
            st.rerun()

    # Live counter
    counter_placeholder = st.empty()
    counter_placeholder.info("📊 আজ পর্যন্ত: ৮৭,২৪০ জন NagarAI ব্যবহার করেছেন")


def render_service_cards():
    """Three main service navigation buttons."""
    lang = st.session_state.lang

    st.markdown(f"### {t('choose_service', lang)}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            f"🏛️ {t('govt_service', lang)}",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page("pages/1_Govt_Service.py")
        st.caption(t('govt_service_desc', lang))

    with col2:
        if st.button(
            f"🚨 {t('social_service', lang)}",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page("pages/2_Social_Service.py")
        st.caption(t('social_service_desc', lang))

    with col3:
        if st.button(
            f"📊 {t('view_heatmap', lang)}",
            type="secondary",
            use_container_width=True,
        ):
            st.switch_page("pages/3_Heatmap.py")
        st.caption(t('view_heatmap_desc', lang))


def render_security_footer():
    """Security notice and session stats."""
    lang = st.session_state.lang

    st.divider()
    st.info(t("security_notice", lang), icon="🔒")

    try:
        stats = get_session_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=t("session_active", lang), value=stats["active_sessions"])
        with col2:
            st.caption(f"{t('demo_data_label', lang)} | Impact Dhaka 2026")
    except Exception:
        st.caption(f"{t('demo_data_label', lang)} | Impact Dhaka 2026")


def render_sidebar():
    """Phase 9 Step 5: Demo controls."""
    lang = st.session_state.lang
    st.sidebar.markdown(f"### {t('app_name', lang)}")
    st.sidebar.caption("Demo Controls")

    if st.sidebar.button("↺ সব রিসেট করুন"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def main():
    """Main landing page."""
    # Load custom CSS
    css_path = os.path.join(os.path.dirname(__file__), "assets", "nagarai_style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_header()
    render_service_cards()
    render_security_footer()
    render_sidebar()


if __name__ == "__main__":
    main()
