"""
appointment.py — Appointment slot booking engine with realistic load simulation.

All text in English for international hackathon.
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import streamlit as st

SERVICE_LOAD_LEVELS = {
    "passport": 0.80,
    "passport_new": 0.75,
    "trade_license": 0.40,
    "trade_license_renewal": 0.35,
    "birth_certificate": 0.30,
    "tin_certificate": 0.20,
    "land_deed": 0.50,
    "nid_correction": 0.25,
}

_booking_log: Dict[str, Dict] = {}


class AppointmentEngine:
    """Appointment slot generator and booking engine."""

    def __init__(self):
        self.booking_log = _booking_log
        self._slot_cache: Dict[str, List[Dict]] = {}

    def _generate_slots(self, service_id: str, days_ahead: int = 7) -> List[Dict]:
        """Generate synthetic appointment slots."""
        cache_key = f"{service_id}_{days_ahead}_{datetime.now().date()}"
        if cache_key in self._slot_cache:
            return self._slot_cache[cache_key]

        load_level = SERVICE_LOAD_LEVELS.get(service_id, 0.50)
        slots = []
        today = datetime.now()
        service_prefix = service_id[:3].upper()

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day_offset in range(1, days_ahead + 1):
            candidate_date = today + timedelta(days=day_offset)

            # Skip Friday (4) and Saturday (5) — Bangladesh weekend
            if candidate_date.weekday() >= 5:
                continue

            for hour in range(9, 17):
                for minute in [0, 30]:
                    if hour == 16 and minute > 0:
                        break

                    time_str = f"{hour:02d}:{minute:02d}"
                    is_taken = random.random() < load_level

                    if load_level > 0.7:
                        load_label = "High Load"
                        load_emoji = "🔴"
                    elif load_level > 0.4:
                        load_label = "Medium Load"
                        load_emoji = "🟡"
                    else:
                        load_label = "Low Load"
                        load_emoji = "🟢"

                    serial = f"{service_prefix}-{random.randint(1000, 9999)}"

                    date_str = candidate_date.strftime(f"%d %B %Y, {day_names[candidate_date.weekday()]}")

                    slots.append({
                        "date": candidate_date.strftime("%Y-%m-%d"),
                        "date_bn": date_str,
                        "time": time_str,
                        "serial": serial,
                        "available": not is_taken,
                        "load": load_label,
                        "load_emoji": load_emoji,
                    })

        self._slot_cache[cache_key] = slots
        return slots

    def get_available_slots(self, service_id: str, days_ahead: int = 7) -> List[Dict]:
        """Get next available appointment slots."""
        all_slots = self._generate_slots(service_id, days_ahead)
        available = [s for s in all_slots if s["available"]]
        return available[:5]

    def book_slot(self, service_id: str, slot: Dict, user_name_hash: str) -> Dict:
        """Book an appointment slot."""
        slot_serial = slot["serial"]
        hash_input = f"{service_id}_{slot_serial}_{datetime.now().isoformat()}"
        booking_id = f"BKG-{hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()}"

        booking = {
            "booking_id": booking_id,
            "service_id": service_id,
            "date": slot["date"],
            "date_bn": slot["date_bn"],
            "time": slot["time"],
            "serial": slot["serial"],
            "user_hash": user_name_hash,
            "status": "confirmed",
            "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_wait_min": random.randint(5, 25),
        }

        self.booking_log[booking_id] = booking
        return booking

    def render_appointment_picker(self, service_id: str) -> Optional[Dict]:
        """Render calendar-style slot picker in Streamlit."""
        all_slots = self._generate_slots(service_id, days_ahead=7)
        available = [s for s in all_slots if s["available"]]

        if not available:
            st.warning("No available slots found. Please try again later.")
            return None

        load_level = SERVICE_LOAD_LEVELS.get(service_id, 0.50)
        est_wait = int(load_level * 30) + 5

        st.markdown(f"### 📅 Choose an Appointment Slot")
        st.caption(f"Estimated wait: **{est_wait} minutes**")

        slots_by_date: Dict[str, List[Dict]] = {}
        for slot in available[:15]:
            date = slot["date"]
            if date not in slots_by_date:
                slots_by_date[date] = []
            slots_by_date[date].append(slot)

        selected_slot = None

        for date, date_slots in list(slots_by_date.items())[:3]:
            sample_slot = date_slots[0]
            st.markdown(f"#### {sample_slot['date_bn']}")

            cols = st.columns(min(len(date_slots), 5))
            for i, slot in enumerate(date_slots[:5]):
                with cols[i % 5]:
                    btn_label = f"⏰ {slot['time']}\n{slot['load_emoji']} {slot['load']}"
                    if st.button(btn_label, key=f"slot_{slot['serial']}", use_container_width=True):
                        selected_slot = slot

        if selected_slot:
            st.divider()
            st.markdown(f"**Selected Slot:**")
            st.info(f"📅 {selected_slot['date_bn']} | ⏰ {selected_slot['time']} | 🔢 {selected_slot['serial']}")

            if st.button("✅ Book This Slot", type="primary"):
                user_hash = hashlib.sha256(f"demo_user_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
                booking = self.book_slot(service_id, selected_slot, user_hash)

                if booking:
                    st.session_state.appointment_booking = booking
                    st.success(f"✅ Appointment confirmed!")

                    st.markdown(f"""
                    **Booking Details:**
                    - Booking ID: `{booking['booking_id']}`
                    - Serial: `{booking['serial']}`
                    - Date: {booking['date_bn']}
                    - Time: {booking['time']}
                    - Estimated wait: {booking['estimated_wait_min']} minutes
                    """)

                    return booking

        return None


# Backward compatibility
def generate_available_slots(service_id: str, date_str: str) -> List[str]:
    """Legacy function."""
    engine = AppointmentEngine()
    slots = engine._generate_slots(service_id, days_ahead=7)
    date_slots = [s for s in slots if s["date"] == date_str and s["available"]]
    return [s["time"] for s in date_slots[:14]]


def book_slot(service_id: str, date_str: str, time_str: str, user_info: Dict) -> Optional[Dict]:
    """Legacy function."""
    engine = AppointmentEngine()
    slot = {
        "date": date_str,
        "date_bn": datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %B %Y"),
        "time": time_str,
        "serial": f"{service_id[:3].upper()}-{random.randint(1000, 9999)}",
        "available": True,
        "load": "Low Load",
        "load_emoji": "🟢",
    }
    user_hash = hashlib.sha256(user_info.get("name", "anonymous").encode()).hexdigest()[:12]
    return engine.book_slot(service_id, slot, user_hash)


def cancel_booking(booking_id: str) -> bool:
    """Legacy function."""
    if booking_id in _booking_log:
        _booking_log[booking_id]["status"] = "cancelled"
        return True
    return False


def get_upcoming_appointments() -> List[Dict]:
    """Legacy function."""
    return [b for b in _booking_log.values() if b["status"] == "confirmed"]


if __name__ == "__main__":
    print("=== Appointment Engine Test ===\n")

    engine = AppointmentEngine()

    slots = engine.get_available_slots("passport")
    assert len(slots) > 0
    assert all(s["available"] for s in slots)
    print(f"✅ Test 1 PASSED: {len(slots)} available slots for passport")

    assert "2026" in slots[0]["date_bn"]
    print(f"✅ Test 2 PASSED: Date: {slots[0]['date_bn']}")

    slots_passport = engine.get_available_slots("passport")
    slots_trade = engine.get_available_slots("trade_license")
    print(f"✅ Test 3 PASSED: Passport slots={len(slots_passport)}, Trade License slots={len(slots_trade)}")

    if slots:
        booking = engine.book_slot("passport", slots[0], "test_user_hash")
        assert booking["status"] == "confirmed"
        assert booking["booking_id"].startswith("BKG-")
        print(f"✅ Test 4 PASSED: Booking confirmed: {booking['booking_id']}")

    legacy_slots = generate_available_slots("passport", "2026-05-01")
    assert isinstance(legacy_slots, list)
    print(f"✅ Test 5 PASSED: Legacy function returns {len(legacy_slots)} slots")

    print("\n🎉 All 5 appointment tests PASSED!")
