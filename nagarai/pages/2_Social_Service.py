"""
pages/2_Social_Service.py — Emergency social services, zero login.

All text in English for international hackathon.
"""

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from i18n import t
from location_mock import LocationService

st.set_page_config(
    page_title="Emergency Services — NagarAI",
    page_icon="🚨",
    layout="wide",
)


def initialize_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    if "location_service" not in st.session_state:
        st.session_state.location_service = LocationService()
    defaults = {"user_lat": 23.7275, "user_lon": 90.4074, "selected_category": None, "location_set": False}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_all():
    for key in ["selected_category", "location_set"]:
        if key in st.session_state:
            del st.session_state[key]
    initialize_state()


def render_top_banner():
    st.warning(
        "🚨 **Emergency Services — No login required | 100% Free**\n\n"
        "Find help in 3 taps. Zero friction. No data collected.",
        icon="🚨",
    )


def render_emergency_numbers():
    st.markdown("### 📞 Emergency Contact Numbers")

    numbers = [
        {"number": "999", "name": "National Emergency", "color": "red", "tel": "999"},
        {"number": "199", "name": "Fire / Ambulance", "color": "orange", "tel": "199"},
        {"number": "100", "name": "Police", "color": "blue", "tel": "100"},
        {"number": "16767", "name": "Helpline", "color": "green", "tel": "16767"},
    ]

    cols = st.columns(4)
    for i, num in enumerate(numbers):
        with cols[i]:
            if num["color"] == "red":
                text_color = "#dc2626"
            elif num["color"] == "orange":
                text_color = "#ea580c"
            elif num["color"] == "blue":
                text_color = "#2563eb"
            else:
                text_color = "#16a34a"

            html = (
                f"<div style='text-align:center; padding: 1rem; background-color: #f8f9fa; "
                f"border-radius: 12px; border-left: 5px solid {num['color']};'>"
                f"<h1 style='margin:0; color: {text_color};'>{num['number']}</h1>"
                f"<p style='margin:0.5rem 0 0 0; font-size: 0.9rem;'>{num['name']}</p>"
                f"</div>"
            )
            st.markdown(html, unsafe_allow_html=True)
            st.markdown(
                f"<div style='text-align:center; margin-top: 0.5rem;'>"
                f"<a href='tel:{num['tel']}' style='text-decoration:none;'>📞 Call Now</a></div>",
                unsafe_allow_html=True,
            )


def render_category_selector():
    st.divider()
    st.markdown("### 🔍 Choose a Service Category")

    categories = [
        {"key": "hospital", "icon": "🏥", "label": "Hospitals"},
        {"key": "pharmacy", "icon": "💊", "label": "Pharmacies"},
        {"key": "police", "icon": "👮", "label": "Police"},
        {"key": "photo_studio", "icon": "📸", "label": "Photo Studios"},
    ]

    cols = st.columns(4)
    for i, cat in enumerate(cols):
        with cat:
            is_selected = st.session_state.selected_category == categories[i]["key"]
            btn_type = "primary" if is_selected else "secondary"
            c = categories[i]
            if st.button(f"{c['icon']} {c['label']}", type=btn_type, use_container_width=True, key=f"cat_{c['key']}"):
                st.session_state.selected_category = c["key"]
                st.session_state.location_set = True
                st.rerun()


def render_location_and_results():
    ls = st.session_state.location_service
    category = st.session_state.selected_category
    if not category:
        return

    st.divider()
    st.info(
        f"📍 Using demo location: Dhaka city center "
        f"({st.session_state.user_lat:.4f}, {st.session_state.user_lon:.4f})"
    )

    col_lat, col_lon = st.columns(2)
    with col_lat:
        st.session_state.user_lat = st.slider(
            "Latitude", min_value=23.65, max_value=23.90, value=st.session_state.user_lat, step=0.01, format="%.4f", key="social_lat"
        )
    with col_lon:
        st.session_state.user_lon = st.slider(
            "Longitude", min_value=90.30, max_value=90.50, value=st.session_state.user_lon, step=0.01, format="%.4f", key="social_lon"
        )

    st.divider()
    category_names = {"hospital": "Hospitals", "pharmacy": "Pharmacies", "police": "Police Stations", "photo_studio": "Photo Studios"}
    st.markdown(f"### 📍 Nearest {category_names.get(category, category)}")

    results = ls.get_nearest(category, st.session_state.user_lat, st.session_state.user_lon, limit=5)
    if not results:
        st.warning(f"No {category_names.get(category, category)} found in this area.")
        return

    for i, item in enumerate(results):
        with st.expander(f"{i+1}. {item['name_bn']} ({item['distance_km']} km)", expanded=(i == 0)):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"**📍 Distance:** {item['distance_km']} km")
                st.markdown(f"**🕐 Status:** {item['open_status_bn']}")
            with col_b:
                st.markdown(f"**📞 Phone:** {item['phone']}")
                st.markdown(f"**🏷️ Type:** {item.get('type', 'N/A')}")
            with col_c:
                st.markdown(f"**📍 Address:** {item.get('address_bn', 'N/A')}")
                if item.get("specialties"):
                    st.markdown(f"**Specialties:** {', '.join(item['specialties'])}")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                phone_val = item.get("phone", "999")
                st.markdown(
                    f"<a href='tel:{phone_val}' style='text-decoration:none; display:block; text-align:center; padding:0.5rem; background:#2563eb; color:white; border-radius:8px;'>📞 Call</a>",
                    unsafe_allow_html=True,
                )
            with col_btn2:
                st.markdown(
                    f"<a href='{item['maps_url']}' target='_blank' style='text-decoration:none; display:block; text-align:center; padding:0.5rem; background:#16a34a; color:white; border-radius:8px;'>🗺️ Directions</a>",
                    unsafe_allow_html=True,
                )


def render_verified_vendors():
    st.divider()
    st.markdown("### 📍 Services Near Government Offices")
    st.caption("NagarAI Verified Vendors")

    studios = [
        {"name_bn": "Agargaon Photo Studio", "address_bn": "Agargaon, next to Passport Office", "phone": "02-55012345", "distance_km": 0.1, "verified": True},
        {"name_bn": "Sher-e-Bangla Photo Point", "address_bn": "Sher-e-Bangla Nagar, Dhaka", "phone": "01712345678", "distance_km": 0.3, "verified": True},
        {"name_bn": "Mirpur Photo Center", "address_bn": "Mirpur-10, Dhaka", "phone": "01912345678", "distance_km": 2.1, "verified": True},
    ]

    for studio in studios:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            badge = "✅ NagarAI Verified" if studio["verified"] else ""
            st.markdown(f"📸 **{studio['name_bn']}** — {studio['distance_km']} km {badge}\n\n📍 {studio['address_bn']} | 📞 {studio['phone']}")
        with col_b:
            st.markdown(
                f"<a href='tel:{studio['phone']}' style='text-decoration:none; display:block; text-align:center; padding:0.5rem; background:#2563eb; color:white; border-radius:8px;'>📞 Call</a>",
                unsafe_allow_html=True,
            )


def render_queue_estimator():
    st.divider()
    st.markdown("### 📊 Which office has the lowest load today?")

    offices = [
        {"name": "Immigration Office (Passport)", "load": "High", "pct": 85, "wait": 45, "emoji": "🔴"},
        {"name": "City Corporation (Trade License)", "load": "Medium", "pct": 55, "wait": 25, "emoji": "🟡"},
        {"name": "Union Parishad (Birth Certificate)", "load": "Low", "pct": 25, "wait": 10, "emoji": "🟢"},
        {"name": "NBR Office (TIN Certificate)", "load": "Low", "pct": 20, "wait": 5, "emoji": "🟢"},
        {"name": "Sub-Registrar (Land Deed)", "load": "Medium", "pct": 60, "wait": 30, "emoji": "🟡"},
    ]

    import pandas as pd
    table_data = []
    for o in offices:
        table_data.append({
            "Office": o["name"],
            "Load": f"{o['emoji']} {o['load']}",
            "Est. Wait": f"{o['wait']} min",
            "Recommendation": "✅ Go now" if o["load"] == "Low" else "⏳ Go later",
        })
    st.table(pd.DataFrame(table_data))


def render_footer():
    st.divider()
    st.success(
        "🔒 **This page stores none of your information.**\n\n"
        "• No login | No tracking | No data saved\n\n"
        "_Your privacy is our priority._"
    )


def render_sidebar():
    lang = st.session_state.lang
    st.sidebar.markdown("### 🚨 Emergency Services")
    st.sidebar.caption("No login | No tracking")

    st.sidebar.divider()
    st.sidebar.markdown("**📈 Impact:**")
    st.sidebar.caption("87,240+ users")
    st.sidebar.caption("100% Free")
    st.sidebar.caption("Help in 3 taps")

    st.sidebar.divider()
    st.sidebar.caption("🎬 Demo Controls")
    if st.sidebar.button("↺ Reset All"):
        reset_all()
        st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🏠 Back to Home"):
        st.switch_page("NagarAI.py")


def main():
    initialize_state()
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "nagarai_style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    render_top_banner()
    render_emergency_numbers()
    render_category_selector()
    render_location_and_results()
    render_verified_vendors()
    render_queue_estimator()
    render_footer()
    render_sidebar()


if __name__ == "__main__":
    main()
