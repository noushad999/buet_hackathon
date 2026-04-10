"""
synthetic_data.py — Augmented data loader for heatmap dashboard.

All text in English for international hackathon.
"""

import json
import os
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


def load_heatmap_data() -> dict:
    """Load heatmap data with computed fields added."""
    raw = _load_raw()
    contrib = raw.get("nagarai_contribution", {})

    total = contrib.get("total_users_served", 0)
    nagarai = contrib.get("nagarai_users", int(total * 0.406))

    computed = {
        "nagarai_share_pct": round((nagarai / total * 100), 1) if total > 0 else 0,
        "time_saved_hours": round(nagarai * 1.57, 0),
        "satisfaction_trend": [3.8, 4.0, 4.1, 4.2],
    }

    raw["computed"] = computed
    return raw


def generate_weekly_table(service_id: str) -> List[Dict]:
    """Generate weekly application table for a service."""
    raw = _load_raw()
    demand = raw.get("service_demand_summary", {})
    svc = demand.get(service_id, {})

    total_apps = svc.get("total_applications", 1000)
    nagarai_pct = 0.40
    base = int(total_apps / 4)

    table = []
    for week in range(1, 5):
        apps = base + (week - 2) * 100
        nagarai = int(apps * nagarai_pct)
        direct = apps - nagarai
        satisfaction = round(3.5 + week * 0.15, 1)

        table.append({
            "Week": f"Week {week}",
            "Total Applications": apps,
            "Via NagarAI": nagarai,
            "Direct Office": direct,
            "Satisfaction": f"{satisfaction}/5.0",
        })

    return table


def get_summary_metrics() -> dict:
    """Get across-all-services summary metrics."""
    raw = _load_raw()
    contrib = raw.get("nagarai_contribution", {})
    demand = raw.get("service_demand_summary", {})

    total_queries = sum(s.get("total_applications", 0) for s in demand.values())
    nagarai_queries = contrib.get("nagarai_users", int(total_queries * 0.406))
    time_saved = nagarai_queries * 1.57
    taka_saved = time_saved * 50

    most_popular_id = max(demand, key=lambda k: demand[k].get("total_applications", 0)) if demand else ""
    svc_data = demand.get(most_popular_id, {})

    name_map = {
        "passport": "Passport Renewal",
        "trade_license": "Trade License",
        "birth_certificate": "Birth Certificate",
        "tin_certificate": "TIN Certificate",
        "land_deed": "Land Deed",
        "passport_new": "New Passport",
        "trade_license_renewal": "Trade License Renewal",
        "nid_correction": "NID Correction",
    }

    return {
        "total_queries_month": total_queries,
        "nagarai_queries_month": nagarai_queries,
        "time_saved_hours_month": round(time_saved),
        "taka_saved_estimate": round(taka_saved),
        "avg_satisfaction": round(svc_data.get("avg_satisfaction", 4.1), 1),
        "most_popular_service_bn": name_map.get(most_popular_id, most_popular_id),
        "peak_day": "Tuesday",
    }


def generate_heatmap_grid() -> tuple:
    """Generate services x weeks heatmap grid."""
    raw = _load_raw()
    demand = raw.get("service_demand_summary", {})

    name_map = {
        "passport": "Passport",
        "trade_license": "Trade License",
        "birth_certificate": "Birth Certificate",
        "tin_certificate": "TIN Certificate",
        "land_deed": "Land Deed",
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

    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    return services, weeks, data_matrix


if __name__ == "__main__":
    print("=== Synthetic Data Test ===\n")

    data = load_heatmap_data()
    assert "computed" in data
    assert data["computed"]["nagarai_share_pct"] > 0
    print(f"✅ 1. load_heatmap_data: share={data['computed']['nagarai_share_pct']}%")

    table = generate_weekly_table("passport")
    assert len(table) == 4
    assert "Week" in table[0]
    print(f"✅ 2. Weekly table: {len(table)} rows")

    metrics = get_summary_metrics()
    assert metrics["total_queries_month"] > 0
    assert metrics["taka_saved_estimate"] > 0
    print(f"✅ 3. Summary: {metrics['total_queries_month']} queries, BDT {metrics['taka_saved_estimate']:,} saved")

    services, weeks, matrix = generate_heatmap_grid()
    assert len(services) > 0
    assert len(weeks) == 4
    assert len(matrix) == len(services)
    print(f"✅ 4. Heatmap grid: {len(services)} services x {len(weeks)} weeks")

    print("\n🎉 All 4 synthetic data tests PASSED!")
