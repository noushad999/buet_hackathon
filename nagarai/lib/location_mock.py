"""
location_mock.py — Location service with haversine distance, realistic mock data.

All text in English for international hackathon.
"""

import json
import os
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import streamlit as st

_EMERGENCY_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "emergency_db.json")


def _load_emergency_db() -> Dict:
    """Load emergency services database from JSON file."""
    try:
        with open(_EMERGENCY_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "hospitals": [],
            "pharmacies": [],
            "police_stations": [],
            "emergency_contacts": {},
            "photo_studios": [],
        }


class LocationService:
    """Geo nearest-search using Haversine formula."""

    def __init__(self):
        self._db = _load_emergency_db()

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coords in km."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _enrich_location(self, item: Dict, user_lat: float, user_lon: float) -> Dict:
        """Add distance, open status, maps URL to a location item."""
        dist = self.haversine(user_lat, user_lon, item["lat"], item["lon"])

        hour = datetime.now().hour
        is_24h = item.get("open_24h", False)

        if is_24h:
            open_now = True
            open_status_bn = "Open Now (24 Hours)"
        else:
            open_hour = item.get("open_hour", 9)
            close_hour = item.get("close_hour", 17)
            open_now = open_hour <= hour < close_hour
            if open_now:
                open_status_bn = f"Open Now (closes at {close_hour}:00)"
            else:
                open_status_bn = f"Closed (opens at {open_hour}:00)"

        maps_url = f"https://maps.google.com/?q={item['lat']},{item['lon']}"

        return {
            **item,
            "distance_km": round(dist, 2),
            "open_now": open_now,
            "open_status_bn": open_status_bn,
            "maps_url": maps_url,
        }

    def get_nearest(self, category: str, user_lat: float, user_lon: float, limit: int = 3) -> List[Dict]:
        """Get nearest services by category."""
        category_map = {
            "hospital": "hospitals",
            "pharmacy": "pharmacies",
            "police": "police_stations",
            "photo_studio": "photo_studios",
        }

        db_key = category_map.get(category)
        if not db_key:
            return []

        items = self._db.get(db_key, [])
        if not items:
            return []

        results = []
        for item in items:
            try:
                enriched = self._enrich_location(item, user_lat, user_lon)
                results.append(enriched)
            except (KeyError, TypeError):
                continue

        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

    @staticmethod
    def mock_user_location() -> Tuple[float, float]:
        """Return Dhaka city center coordinates for demo."""
        return (23.7275, 90.4074)

    def get_emergency_contacts(self) -> Dict:
        """Get national emergency contact numbers."""
        return self._db.get("emergency_contacts", {})


# Backward compatibility
def find_nearest_hospitals(user_lat: float, user_lon: float, limit: int = 3) -> List[Dict]:
    ls = LocationService()
    return ls.get_nearest("hospital", user_lat, user_lon, limit)


def find_nearest_pharmacies(user_lat: float, user_lon: float, limit: int = 3) -> List[Dict]:
    ls = LocationService()
    return ls.get_nearest("pharmacy", user_lat, user_lon, limit)


def find_nearest_police(user_lat: float, user_lon: float, limit: int = 3) -> List[Dict]:
    ls = LocationService()
    return ls.get_nearest("police", user_lat, user_lon, limit)


def get_emergency_contacts() -> Dict:
    ls = LocationService()
    return ls.get_emergency_contacts()


if __name__ == "__main__":
    print("=== Location Service Test ===\n")

    ls = LocationService()

    hospitals = ls.get_nearest("hospital", 23.7390, 90.3950, limit=3)
    assert len(hospitals) > 0
    assert "distance_km" in hospitals[0]
    print(f"✅ Test 1 PASSED: {len(hospitals)} hospitals found")

    pharmacies = ls.get_nearest("pharmacy", 23.7390, 90.3950, limit=3)
    assert len(pharmacies) > 0
    print(f"✅ Test 2 PASSED: {len(pharmacies)} pharmacies found")

    police = ls.get_nearest("police", 23.7390, 90.3950, limit=3)
    assert len(police) > 0
    print(f"✅ Test 3 PASSED: {len(police)} police stations found")

    lat, lon = ls.mock_user_location()
    assert 23.0 < lat < 24.0
    assert 90.0 < lon < 91.0
    print(f"✅ Test 4 PASSED: Mock location ({lat}, {lon})")

    contacts = ls.get_emergency_contacts()
    assert "national_emergency" in contacts
    print(f"✅ Test 5 PASSED: Emergency contacts loaded (999)")

    dist = ls.haversine(23.7390, 90.3950, 23.7262, 90.3988)
    assert 0.5 < dist < 3.0
    print(f"✅ Test 6 PASSED: Distance = {dist:.2f} km")

    h = hospitals[0]
    assert "open_status_bn" in h
    assert "maps_url" in h
    print(f"✅ Test 7 PASSED: Open status: {h['open_status_bn']}")

    print("\n🎉 All 7 location tests PASSED!")
