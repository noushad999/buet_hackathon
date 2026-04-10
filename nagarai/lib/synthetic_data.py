"""
synthetic_data.py — Augmented data loader for heatmap dashboard.

B2G analytics: adds computed fields, weekly tables, summary metrics.
Demo data — all synthetic, clearly labeled.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List


_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "heatmap_seed.json")


def _load_raw() -> Dict:
    """Load raw heatmap seed JSON."""
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "heatmap_data": [],
            "service_demand_summary": {},
            "nagarai_contribution": {},
        }


# Bengali digit conversion
_BN = "০১২৩৪৫৬৭৮৯"


def _bn(n: int) -> str:
    return "".join(_BN[int(d)] for d in str(n))


def _bn_month(n: int) -> str:
    months = [
        "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
        "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর",
    ]
    return months[n - 1] if 1 <= n <= 12 else ""


# ============================================================
# FUNCTION: load_heatmap_data()
# ============================================================
def load_heatmap_data() -> dict:
    """Load heatmap data with computed fields added.

    Adds:
    - nagarai_share_pct
    - time_saved_hours
    - satisfaction_trend

    Returns:
        Augmented data dict
    """
    raw = _load_raw()
    contrib = raw.get("nagarai_contribution", {})

    total = contrib.get("total_users_served", 0)
    nagarai = contrib.get("nagarai_users", int(total * 0.406))

    # Computed fields
    computed = {
        "nagarai_share_pct": round((nagarai / total * 100), 1) if total > 0 else 0,
        "time_saved_hours": round(nagarai * 1.57, 0),  # 97 min avg
        "satisfaction_trend": [3.8, 4.0, 4.1, 4.2],  # 4 weekly scores
    }

    raw["computed"] = computed
    return raw


# ============================================================
# FUNCTION: generate_weekly_table()
# ============================================================
def generate_weekly_table(service_id: str) -> List[Dict]:
    """Generate weekly application table for a service.

    Args:
        service_id: Service identifier

    Returns:
        List of 4 row dicts with Bengali column names
    """
    raw = _load_raw()
    demand = raw.get("service_demand_summary", {})
    svc = demand.get(service_id, {})

    total_apps = svc.get("total_applications", 1000)
    nagarai_pct = 0.40
    base = int(total_apps / 4)

    table = []
    for week in range(1, 5):
        apps = base + (week - 2) * 100  # Slight increase each week
        nagarai = int(apps * nagarai_pct)
        direct = apps - nagarai
        satisfaction = round(3.5 + week * 0.15, 1)

        table.append({
            "সপ্তাহ": f"সপ্তাহ {_bn(week)}",
            "মোট আবেদন": apps,
            "NagarAI মাধ্যমে": nagarai,
            "সরাসরি অফিসে": direct,
            "সন্তুষ্টি": f"{satisfaction}/5.0",
        })

    return table


# ============================================================
# FUNCTION: get_summary_metrics()
# ============================================================
def get_summary_metrics() -> dict:
    """Get across-all-services summary metrics.

    Returns:
        Dict with totals, savings, satisfaction, popular service, peak day
    """
    raw = _load_raw()
    contrib = raw.get("nagarai_contribution", {})
    demand = raw.get("service_demand_summary", {})

    total_queries = sum(s.get("total_applications", 0) for s in demand.values())
    nagarai_queries = contrib.get("nagarai_users", int(total_queries * 0.406))
    time_saved = nagarai_queries * 1.57
    taka_saved = time_saved * 50

    # Find most popular service
    most_popular_id = max(demand, key=lambda k: demand[k].get("total_applications", 0)) if demand else ""
    svc_data = demand.get(most_popular_id, {})

    # Service name mapping
    name_map = {
        "passport": "পাসপোর্ট নবায়ন",
        "trade_license": "ট্রেড লাইসেন্স",
        "birth_certificate": "জন্ম সনদ",
        "tin_certificate": "TIN সনদ",
        "land_deed": "জমির দলিল",
        "passport_new": "নতুন পাসপোর্ট",
        "trade_license_renewal": "ট্রেড লাইসেন্স নবায়ন",
        "nid_correction": "NID সংশোধন",
    }

    return {
        "total_queries_month": total_queries,
        "nagarai_queries_month": nagarai_queries,
        "time_saved_hours_month": round(time_saved),
        "taka_saved_estimate": round(taka_saved),
        "avg_satisfaction": round(svc_data.get("avg_satisfaction", 4.1), 1),
        "most_popular_service_bn": name_map.get(most_popular_id, most_popular_id),
        "peak_day": "মঙ্গলবার",
    }


# ============================================================
# FUNCTION: generate_heatmap_grid()
# ============================================================
def generate_heatmap_grid() -> tuple:
    """Generate 8 services × 4 weeks heatmap grid.

    Returns:
        (services, weeks, data_matrix)
    """
    raw = _load_raw()
    demand = raw.get("service_demand_summary", {})

    name_map = {
        "passport": "পাসপোর্ট",
        "trade_license": "ট্রেড লাইসেন্স",
        "birth_certificate": "জন্ম সনদ",
        "tin_certificate": "TIN সনদ",
        "land_deed": "জমির দলিল",
    }

    services = []
    data_matrix = []

    for svc_id, svc_data in demand.items():
        base = svc_data.get("total_applications", 5000)
        weekly = []
        for w in range(1, 5):
            val = base // 4 + (w - 2) * 500
            weekly.append(max(val, 1000))
        services.append(name_map.get(svc_id, svc_id))
        data_matrix.append(weekly)

    weeks = ["সপ্তাহ ১", "সপ্তাহ ২", "সপ্তাহ ৩", "সপ্তাহ ৪"]
    return services, weeks, data_matrix


# ============================================================
# Tests
# ============================================================
if __name__ == "__main__":
    print("=== Synthetic Data Test ===\n")

    # Test 1: load_heatmap_data
    data = load_heatmap_data()
    assert "computed" in data
    assert data["computed"]["nagarai_share_pct"] > 0
    print(f"✅ 1. load_heatmap_data: share={data['computed']['nagarai_share_pct']}%")

    # Test 2: weekly table
    table = generate_weekly_table("passport")
    assert len(table) == 4
    assert "সপ্তাহ" in table[0]
    print(f"✅ 2. Weekly table: {len(table)} rows")

    # Test 3: summary metrics
    metrics = get_summary_metrics()
    assert metrics["total_queries_month"] > 0
    assert metrics["taka_saved_estimate"] > 0
    print(f"✅ 3. Summary: {metrics['total_queries_month']} queries, ৳{metrics['taka_saved_estimate']:,} saved")

    # Test 4: heatmap grid
    services, weeks, matrix = generate_heatmap_grid()
    assert len(services) > 0
    assert len(weeks) == 4
    assert len(matrix) == len(services)
    print(f"✅ 4. Heatmap grid: {len(services)} services × {len(weeks)} weeks")

    print("\n🎉 All 4 synthetic data tests PASSED!")
