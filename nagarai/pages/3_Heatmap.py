"""
pages/3_Heatmap.py — Government analytics dashboard (B2G SaaS product).

All text in English for international hackathon.
"""

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

try:
    from i18n import t
    from synthetic_data import load_heatmap_data, generate_weekly_table, get_summary_metrics, generate_heatmap_grid
except ImportError as e:
    st.error(f"Module load error: {e}")
    st.stop()

st.set_page_config(
    page_title="Service Analytics — NagarAI",
    page_icon="📊",
    layout="wide",
)


def init_global_state():
    defaults = {"current_service": None, "form_step": 0, "form_answers": {}, "payment_done": False, "appointment_done": False, "demo_mode": True}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


@st.cache_data(ttl=300)
def load_data():
    return load_heatmap_data()


@st.cache_data(ttl=300)
def load_summary():
    return get_summary_metrics()


def initialize_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    init_global_state()


def render_header():
    st.warning("⚠️ Demo Data — Synthetic | All data is simulated for demonstration purposes", icon="⚠️")

    st.markdown("## 📊 Service Usage Analytics — Government Dashboard")
    st.caption("How many citizens used services through NagarAI")

    st.markdown(
        "<span style='background:#fbbf24; color:#78350f; padding:4px 12px; border-radius:8px; font-size:0.8rem; font-weight:600;'>"
        "📋 Demo Data | Synthetic</span>",
        unsafe_allow_html=True,
    )


def render_summary_metrics():
    metrics = load_summary()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Applications", value=f"{metrics['total_queries_month']:,}", delta="↑ 12%")
    with col2:
        st.metric(label="Via NagarAI", value=f"{metrics['nagarai_queries_month']:,}", delta="↑ 18%")
    with col3:
        st.metric(label="Time Saved", value=f"{metrics['time_saved_hours_month']:,} hours", delta="↑ 18%")
    with col4:
        st.metric(label="Estimated Cost Savings", value=f"BDT {metrics['taka_saved_estimate']:,}", delta="↑ 18%")


def render_heatmap_grid():
    import pandas as pd

    st.divider()
    st.markdown("### 🗺️ Monthly Service Demand Heatmap")

    services, weeks, matrix = generate_heatmap_grid()
    if not matrix:
        st.info("Heatmap data not available")
        return

    df = pd.DataFrame(matrix, index=services, columns=weeks)

    def color_heatmap(val):
        if val < 5000:
            return "background-color: #dbeafe; color: #1e3a5f"
        elif val < 15000:
            return "background-color: #93c5fd; color: #1e3a5f"
        elif val < 30000:
            return "background-color: #3b82f6; color: white"
        else:
            return "background-color: #1d4ed8; color: white"

    styled = df.style.map(color_heatmap)
    st.dataframe(styled, use_container_width=True)

    st.caption("📊 Darker blue = higher demand. Identify the busiest weeks.")


def render_service_drilldown():
    import pandas as pd

    raw = load_data()
    demand = raw.get("service_demand_summary", {})
    name_map = {
        "passport": "Passport",
        "trade_license": "Trade License",
        "birth_certificate": "Birth Certificate",
        "tin_certificate": "TIN Certificate",
        "land_deed": "Land Deed",
    }

    st.divider()
    st.markdown("### 🔍 Service Drill-Down")

    selected = st.selectbox("Select a service:", options=list(demand.keys()), format_func=lambda x: name_map.get(x, x))
    if not selected:
        return

    table = generate_weekly_table(selected)
    st.markdown(f"**Weekly Applications — {name_map.get(selected, selected)}**")
    df = pd.DataFrame(table)
    st.dataframe(df, use_container_width=True)

    st.markdown("**Weekly Trend:**")
    weekly_values = [row["Total Applications"] for row in table]
    st.bar_chart({"Applications": weekly_values}, height=200)

    svc = demand.get(selected, {})
    total = svc.get("total_applications", 0)
    nagarai_pct = 0.40
    nagarai_count = int(total * nagarai_pct)
    direct_count = total - nagarai_count

    pie_data = pd.DataFrame({"Method": ["Via NagarAI", "Direct Office"], "Applications": [nagarai_count, direct_count]})
    st.markdown("**NagarAI Contribution:**")
    st.bar_chart(pie_data.set_index("Method"), height=200)
    st.caption(f"NagarAI: {nagarai_count:,} ({nagarai_pct:.0%}) | Direct: {direct_count:,} ({1-nagarai_pct:.0%})")


def render_insights():
    st.divider()
    st.markdown("### 💡 Auto-Generated Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            "<div style='background:#fef2f2; border-left:4px solid #dc2626; padding:1rem; border-radius:8px;'>"
            "<b>🔴 Highest Demand: Passport Renewal</b><br>"
            "Peak in Week 3 → Additional staff needed</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            "<div style='background:f0fdf4; border-left:4px solid #16a34a; padding:1rem; border-radius:8px;'>"
            "<b>🟢 NagarAI Impact: 40.6% of applications processed digitally</b><br>"
            "Reduced office crowding</div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            "<div style='background:#eff6ff; border-left:4px solid #2563eb; padding:1rem; border-radius:8px;'>"
            "<b>📈 Trend: NID Correction demand rising</b><br>"
            "Expected in election years</div>",
            unsafe_allow_html=True,
        )


def render_b2g_value():
    import pandas as pd

    st.divider()
    st.info(
        "🏛️ **This dashboard helps government offices:**\n\n"
        "✅ Identify weeks that need extra staff\n"
        "✅ Spot services with low digital adoption\n"
        "✅ Track citizen satisfaction in real-time\n\n"
        "**NagarAI SaaS License: BDT 5-20 lakh/year/office**"
    )

    st.divider()
    st.markdown("### ⚡ Why NagarAI Wins")

    comparison = pd.DataFrame({
        "Feature": ["AI Assistant", "Guided Forms", "Emergency Services", "Analytics Dashboard", "No-Login Access"],
        "myGov": ["No ❌", "No ❌", "No ❌", "No ❌", "No ❌"],
        "NagarAI": ["Yes ✅", "Yes ✅", "Yes ✅", "Yes ✅", "Yes ✅"],
    })
    st.table(comparison)


def render_sidebar():
    lang = st.session_state.lang
    metrics = load_summary()

    st.sidebar.markdown("### 📊 Government Dashboard")
    st.sidebar.divider()
    st.sidebar.markdown("**📈 Impact:**")
    st.sidebar.caption(f"{metrics['total_queries_month']:,} applications/month")
    st.sidebar.caption(f"40.6% via NagarAI")
    st.sidebar.caption(f"BDT {metrics['taka_saved_estimate']:,} saved")

    st.sidebar.markdown("---")
    st.sidebar.caption("🎬 Demo Controls")
    if st.sidebar.button("↺ Reset All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
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

    render_header()
    render_summary_metrics()
    render_heatmap_grid()
    render_service_drilldown()
    render_insights()
    render_b2g_value()
    render_sidebar()


if __name__ == "__main__":
    main()
