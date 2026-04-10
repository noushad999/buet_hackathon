"""
NagarAI.py — Landing page for international hackathon demo.

All text in English.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

try:
    from i18n import t
except ImportError as e:
    st.error(f"Module load error: {e}")
    st.stop()

try:
    from security import get_session_stats, create_session
except ImportError:
    pass

st.set_page_config(
    page_title="NagarAI — One App, Two Services",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def init_global_state():
    defaults = {
        "current_service": None,
        "form_step": 0,
        "form_answers": {},
        "payment_done": False,
        "appointment_done": False,
        "demo_mode": True,
        "lang": "en",
        "session_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_global_state()

if st.session_state.session_id is None:
    st.session_state.session_id = "nagarai_demo_session"
    try:
        create_session(st.session_state.session_id)
    except Exception:
        pass


def render_header():
    st.markdown("""
<div style='text-align:center; padding: 2rem 0;'>
  <h1 style='font-size:3rem; font-weight:700; color:#006a4e;'>NagarAI</h1>
  <p style='font-size:1.3rem; color:#374151;'>One App, Two Services</p>
  <p style='font-size:0.9rem; color:#6B7280; margin-top:0.5rem;'>
    Simplify government services | Get emergency help instantly
  </p>
</div>
""", unsafe_allow_html=True)

    st.info("📊 Over 87,240 citizens have used NagarAI so far")


def render_service_cards():
    st.markdown(f"### {t('choose_service', 'en')}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"🏛️ {t('govt_service', 'en')}", type="primary", use_container_width=True):
            st.switch_page("pages/1_Govt_Service.py")
        st.caption(t('govt_service_desc', 'en'))

    with col2:
        if st.button(f"🚨 {t('social_service', 'en')}", type="primary", use_container_width=True):
            st.switch_page("pages/2_Social_Service.py")
        st.caption(t('social_service_desc', 'en'))

    with col3:
        if st.button(f"📊 {t('view_heatmap', 'en')}", type="secondary", use_container_width=True):
            st.switch_page("pages/3_Heatmap.py")
        st.caption(t('view_heatmap_desc', 'en'))


def render_security_footer():
    st.divider()
    st.info(t("security_notice", "en"), icon="🔒")

    try:
        stats = get_session_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label=t("session_active", "en"), value=stats["active_sessions"])
        with col2:
            st.caption(f"{t('demo_data_label', 'en')} | Impact Dhaka 2026")
    except Exception:
        st.caption(f"{t('demo_data_label', 'en')} | Impact Dhaka 2026")


def render_sidebar():
    st.sidebar.markdown("### NagarAI")
    st.sidebar.caption("Demo Controls")
    if st.sidebar.button("↺ Reset All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def main():
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
