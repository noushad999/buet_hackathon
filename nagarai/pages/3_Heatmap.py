"""
pages/3_Heatmap.py — Government analytics dashboard (B2G SaaS product).

Phase 8 + Phase 9: Full analytics dashboard with synthetic data, demo disclaimer,
summary metrics, heatmap grid, service drill-down, insights, B2G value proposition.

All imports wrapped in try/except. All data cached. Demo disclaimer at top.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

# STEP 1: Safe imports
try:
    from i18n import t
    from synthetic_data import load_heatmap_data, generate_weekly_table, get_summary_metrics, generate_heatmap_grid
except ImportError as e:
    st.error(f"মডিউল লোড ত্রুটি: {e}")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="সেবা ব্যবহার বিশ্লেষণ | Government Dashboard — নাগরআই",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# STEP 2: Global session state
# ============================================================
def init_global_state():
    """Ensure global session state defaults."""
    defaults = {
        "current_service": None,
        "form_step": 0,
        "form_answers": {},
        "payment_done": False,
        "appointment_done": False,
        "demo_mode": True,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ============================================================
# STEP 3: Cached data loader
# ============================================================
@st.cache_data(ttl=300)
def load_data():
    """Cached heatmap data loader."""
    return load_heatmap_data()


@st.cache_data(ttl=300)
def load_summary():
    """Cached summary metrics."""
    return get_summary_metrics()


# ============================================================
# INIT
# ============================================================
def initialize_state():
    """Initialize page session state."""
    if "lang" not in st.session_state:
        st.session_state.lang = "bn"
    init_global_state()


# ============================================================
# HEADER
# ============================================================
def render_header():
    """Header with title, subtitle, demo badge."""
    lang = st.session_state.lang

    # Disclaimer
    st.warning("⚠️ Demo Data — Synthetic | সমস্ত তথ্য ডেমো উদ্দেশ্যে তৈরি", icon="⚠️")

    st.markdown("## 📊 সেবা ব্যবহার বিশ্লেষণ — সরকারি অফিস ড্যাশবোর্ড")
    st.caption("NagarAI-এর মাধ্যমে কতজন নাগরিক সেবা নিলেন তার হিসাব")

    # Demo badge
    st.markdown(
        "<span style='background:#fbbf24; color:#78350f; padding:4px 12px; "
        "border-radius:8px; font-size:0.8rem; font-weight:600;'>"
        "📋 Demo Data | Synthetic</span>",
        unsafe_allow_html=True,
    )


# ============================================================
# SECTION 1 — Summary metric cards
# ============================================================
def render_summary_metrics():
    """4 summary metric cards with deltas."""
    lang = st.session_state.lang
    metrics = load_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="মোট আবেদন",
            value=f"{metrics['total_queries_month']:,}",
            delta="↑ 12%",
        )

    with col2:
        st.metric(
            label="NagarAI মাধ্যমে",
            value=f"{metrics['nagarai_queries_month']:,}",
            delta="↑ 18%",
        )

    with col3:
        st.metric(
            label="সাশ্রয়কৃত সময়",
            value=f"{metrics['time_saved_hours_month']:,} ঘণ্টা",
            delta="↑ 18%",
        )

    with col4:
        st.metric(
            label="আনুমানিক টাকা সাশ্রয়",
            value=f"৳{metrics['taka_saved_estimate']:,}",
            delta="↑ 18%",
        )


# ============================================================
# SECTION 2 — Heatmap grid (centerpiece)
# ============================================================
def render_heatmap_grid():
    """Styled heatmap grid: 8 services × 4 weeks."""
    lang = st.session_state.lang

    st.divider()
    st.markdown("### 🗺️ মাসিক সেবা চাহিদা হিটম্যাপ")

    services, weeks, matrix = generate_heatmap_grid()

    if not matrix:
        st.info("হিটম্যাপ ডাটা পাওয়া যায়নি")
        return

    # Build styled table
    import pandas as pd

    df = pd.DataFrame(matrix, index=services, columns=weeks)

    # Color function
    def color_heatmap(val):
        if val < 5000:
            return "background-color: #dbeafe; color: #1e3a5f"
        elif val < 15000:
            return "background-color: #93c5fd; color: #1e3a5f"
        elif val < 30000:
            return "background-color: #3b82f6; color: white"
        else:
            return "background-color: #1d4ed8; color: white"

    styled = df.style.applymap(color_heatmap)
    st.dataframe(styled, use_container_width=True)

    st.caption("📊 সবচেয়ে ব্যস্ত সপ্তাহ চিহ্নিত — গাঢ় নীল = বেশি চাহিদা")


# ============================================================
# SECTION 3 — Service drill-down
# ============================================================
def render_service_drilldown():
    """Select a service to see weekly trend bar chart + table + pie."""
    lang = st.session_state.lang
    raw = load_data()
    demand = raw.get("service_demand_summary", {})

    name_map = {
        "passport": "পাসপোর্ট",
        "trade_license": "ট্রেড লাইসেন্স",
        "birth_certificate": "জন্ম সনদ",
        "tin_certificate": "TIN সনদ",
        "land_deed": "জমির দলিল",
    }

    st.divider()
    st.markdown("### 🔍 সেবা অনুযায়ী বিশ্লেষণ")

    selected = st.selectbox(
        "সেবা বেছে নিন:",
        options=list(demand.keys()),
        format_func=lambda x: name_map.get(x, x),
    )

    if not selected:
        return

    # Weekly table
    table = generate_weekly_table(selected)
    st.markdown(f"**সাপ্তাহিক আবেদন — {name_map.get(selected, selected)}**")

    import pandas as pd
    df = pd.DataFrame(table)
    st.dataframe(df, use_container_width=True)

    # Bar chart of weekly trend
    st.markdown("**সাপ্তাহিক ট্রেন্ড:**")
    weekly_values = [row["মোট আবেদন"] for row in table]
    st.bar_chart({"আবেদন": weekly_values}, height=200)

    # NagarAI contribution pie chart
    svc = demand.get(selected, {})
    total = svc.get("total_applications", 0)
    nagarai_pct = 0.40
    nagarai_count = int(total * nagarai_pct)
    direct_count = total - nagarai_count

    pie_data = pd.DataFrame({
        "মাধ্যম": ["NagarAI", "সরাসরি অফিস"],
        "আবেদন": [nagarai_count, direct_count],
    })
    st.markdown("**NagarAI অবদান:**")
    st.bar_chart(pie_data.set_index("মাধ্যম"), height=200)
    st.caption(f"NagarAI: {nagarai_count:,} ({nagarai_pct:.0%}) | সরাসরি: {direct_count:,} ({1-nagarai_pct:.0%})")


# ============================================================
# SECTION 4 — Insights panel
# ============================================================
def render_insights():
    """3 auto-generated insight cards."""
    st.divider()
    st.markdown("### 💡 স্বয়ংক্রিয় অন্তর্দৃষ্টি")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            "<div style='background:#fef2f2; border-left:4px solid #dc2626; "
            "padding:1rem; border-radius:8px;'>"
            "<b>🔴 সর্বোচ্চ চাহিদা: পাসপোর্ট নবায়ন</b><br>"
            "সপ্তাহ ৩-এ পিক → অতিরিক্ত স্টাফ প্রয়োজন</div>",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            "<div style='background:f0fdf4; border-left:4px solid #16a34a; "
            "padding:1rem; border-radius:8px;'>"
            "<b>🟢 NagarAI প্রভাব: ৪০.৬% আবেদন ডিজিটালি</b><br>"
            "অফিস ভিড় কমেছে</div>",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            "<div style='background:#eff6ff; border-left:4px solid #2563eb; "
            "padding:1rem; border-radius:8px;'>"
            "<b>📈 ট্রেন্ড: NID সংশোধন চাহিদা বেশি</b><br>"
            "নির্বাচনী বছরে স্বাভাবিক</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# SECTION 5 — B2G value proposition
# ============================================================
def render_b2g_value():
    """Bottom box showing why govt should buy NagarAI."""
    st.divider()
    st.info(
        "🏛️ **এই ড্যাশবোর্ড সরকারি অফিসগুলোকে সাহায্য করে:**\n\n"
        "✅ কোন সপ্তাহে অতিরিক্ত স্টাফ দরকার\n"
        "✅ কোন সেবায় ডিজিটাল গ্রহণ কম\n"
        "✅ নাগরিক সন্তুষ্টি রিয়েল-টাইম ট্র্যাক\n\n"
        "**NagarAI SaaS লাইসেন্স: ৳৫-২০ লক্ষ/বছর/অফিস**"
    )

    # Comparison table (Phase 10 Enhancement 4)
    st.divider()
    st.markdown("### ⚡ কেন NagarAI জিতে যায়")

    comparison = {
        "ফিচার": ["AI সহকারী", "বাংলায় গাইড", "জরুরি সেবা", "হিটম্যাপ অ্যানালিটিক্স", "লগইন ছাড়া সেবা"],
        "myGov": ["নেই ❌", "নেই ❌", "নেই ❌", "নেই ❌", "নেই ❌"],
        "NagarAI": ["আছে ✅", "আছে ✅", "আছে ✅", "আছে ✅", "আছে ✅"],
    }
    import pandas as pd
    st.table(pd.DataFrame(comparison))


# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar():
    """Sidebar with impact metrics, demo controls, back button."""
    lang = st.session_state.lang
    metrics = load_summary()

    st.sidebar.markdown("### 📊 সরকারি ড্যাশবোর্ড")

    # Phase 10 Enhancement 5: Pitch metrics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📈 Impact:**")
    st.sidebar.caption(f"{metrics['total_queries_month']:,} আবেদন/মাস")
    st.sidebar.caption(f"৪০.৬% NagarAI মাধ্যমে")
    st.sidebar.caption(f"৳{metrics['taka_saved_estimate']:,} সাশ্রয়")

    # Demo controls
    st.sidebar.markdown("---")
    st.sidebar.caption("🎬 Demo Controls")
    if st.sidebar.button("↺ সব রিসেট করুন"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Back to home
    st.sidebar.divider()
    if st.sidebar.button(f"🏠 {t('back_to_home', lang)}"):
        st.switch_page("NagarAI.py")


# ============================================================
# MAIN
# ============================================================
def main():
    """Main heatmap dashboard."""
    initialize_state()

    # Load custom CSS
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
