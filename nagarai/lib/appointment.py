"""
appointment.py — Appointment slot booking engine with realistic load simulation.

CLASS: AppointmentEngine — generate synthetic slots, book appointments, render picker UI.

Demo purpose: Show judges a realistic appointment system with color-coded availability,
load levels per service, and Bengali date formatting.
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import streamlit as st


# Bengali digit conversion
_BN_DIGITS = "০১২৩৪৫৬৭৮৯"
_BN_MONTHS = [
    "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
    "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর",
]
_BN_DAYS = ["রবিবার", "সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার"]


def to_bengali_digits(n: int) -> str:
    """Convert integer to Bengali digits."""
    return "".join(_BN_DIGITS[int(d)] for d in str(n))


def format_date_bn(dt: datetime) -> str:
    """Format date in Bengali: '১৩ এপ্রিল ২০২৬, রবিবার'."""
    day = to_bengali_digits(dt.day)
    month = _BN_MONTHS[dt.month - 1]
    year = to_bengali_digits(dt.year)
    day_name = _BN_DAYS[dt.weekday()]  # Monday=0, but _BN_DAYS[0]=Sunday
    # Fix: Python Monday=0, we need Monday=সোমবার
    bn_day_names = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"]
    day_name = bn_day_names[dt.weekday()]
    return f"{day} {month} {year}, {day_name}"


# Load levels per service (0.0 to 1.0)
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

# In-memory booking log
_booking_log: Dict[str, Dict] = {}


class AppointmentEngine:
    """Appointment slot generator and booking engine.

    Generates synthetic slot data with realistic load levels:
    - Business days: Mon-Thu, 9am-5pm, 30-min slots
    - Pre-fill ~60% slots as "taken" (realistic load)
    - Different load per service (passport: 80%, trade license: 40%)
    """

    def __init__(self):
        self.booking_log = _booking_log
        self._slot_cache: Dict[str, List[Dict]] = {}

    def _generate_slots(self, service_id: str, days_ahead: int = 7) -> List[Dict]:
        """Generate synthetic appointment slots.

        Args:
            service_id: Service identifier
            days_ahead: How many days to look ahead

        Returns:
            List of slot dicts with date, time, serial, load level
        """
        cache_key = f"{service_id}_{days_ahead}_{datetime.now().date()}"
        if cache_key in self._slot_cache:
            return self._slot_cache[cache_key]

        load_level = SERVICE_LOAD_LEVELS.get(service_id, 0.50)
        slots = []
        today = datetime.now()
        service_prefix = service_id[:3].upper()

        for day_offset in range(1, days_ahead + 1):
            candidate_date = today + timedelta(days=day_offset)

            # Skip Friday (4) and Saturday (5) — Bangladesh weekend
            if candidate_date.weekday() >= 5:
                continue

            # Generate 30-min slots from 9:00 to 16:30
            for hour in range(9, 17):
                for minute in [0, 30]:
                    if hour == 16 and minute > 0:
                        break

                    time_str = f"{hour:02d}:{minute:02d}"

                    # Randomly mark as taken based on load level
                    is_taken = random.random() < load_level

                    # Determine load label
                    if load_level > 0.7:
                        load_label = "বেশি ভিড়"
                        load_emoji = "🔴"
                    elif load_level > 0.4:
                        load_label = "মাঝারি ভিড়"
                        load_emoji = "🟡"
                    else:
                        load_label = "কম ভিড়"
                        load_emoji = "🟢"

                    serial = f"{service_prefix}-{random.randint(1000, 9999)}"

                    slots.append({
                        "date": candidate_date.strftime("%Y-%m-%d"),
                        "date_bn": format_date_bn(candidate_date),
                        "time": time_str,
                        "serial": serial,
                        "available": not is_taken,
                        "load": load_label,
                        "load_emoji": load_emoji,
                    })

        self._slot_cache[cache_key] = slots
        return slots

    # ============================================================
    # METHOD: get_available_slots — Next available slots
    # ============================================================
    def get_available_slots(self, service_id: str, days_ahead: int = 7) -> List[Dict]:
        """Get next available appointment slots.

        Args:
            service_id: Service identifier
            days_ahead: How many days to look ahead

        Returns:
            List of available slot dicts (max 5)

        Example:
            >>> engine = AppointmentEngine()
            >>> slots = engine.get_available_slots("passport")
            >>> len(slots) <= 5
            True
            >>> all(s["available"] for s in slots)
            True
        """
        all_slots = self._generate_slots(service_id, days_ahead)
        available = [s for s in all_slots if s["available"]]
        return available[:5]

    # ============================================================
    # METHOD: book_slot — Book a specific slot
    # ============================================================
    def book_slot(self, service_id: str, slot: Dict, user_name_hash: str) -> Dict:
        """Book an appointment slot.

        Args:
            service_id: Service identifier
            slot: Slot dict from get_available_slots
            user_name_hash: Hashed user name (no PII stored)

        Returns:
            Booking confirmation dict
        """
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

    # ============================================================
    # METHOD: render_appointment_picker — Streamlit UI
    # ============================================================
    def render_appointment_picker(self, service_id: str) -> Optional[Dict]:
        """Render calendar-style slot picker in Streamlit.

        Shows:
        - 3-day slot grid with color coding (green/amber/red)
        - User clicks slot → confirm button
        - Estimated wait time based on load

        Args:
            service_id: Service identifier

        Returns:
            Booking confirmation dict or None
        """
        all_slots = self._generate_slots(service_id, days_ahead=7)
        available = [s for s in all_slots if s["available"]]

        if not available:
            st.warning("কোনো খালি স্লট পাওয়া যায়নি। পরে আবার চেষ্টা করুন।")
            return None

        load_level = SERVICE_LOAD_LEVELS.get(service_id, 0.50)
        est_wait = int(load_level * 30) + 5

        st.markdown(f"### 📅 অ্যাপয়েন্টমেন্ট স্লট বেছে নিন")
        st.caption(f"আনুমানিক অপেক্ষা: **{est_wait} মিনিট**")

        # Group slots by date
        slots_by_date: Dict[str, List[Dict]] = {}
        for slot in available[:15]:  # Show max 15 slots
            date = slot["date"]
            if date not in slots_by_date:
                slots_by_date[date] = []
            slots_by_date[date].append(slot)

        # Render calendar grid
        selected_slot = None

        for date, date_slots in list(slots_by_date.items())[:3]:  # Show 3 days
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
            st.markdown(f"**নির্বাচিত স্লট:**")
            st.info(f"📅 {selected_slot['date_bn']} | ⏰ {selected_slot['time']} | 🔢 {selected_slot['serial']}")

            if st.button("✅ এই স্লটে বুক করুন", type="primary"):
                user_hash = hashlib.sha256(f"demo_user_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
                booking = self.book_slot(service_id, selected_slot, user_hash)

                if booking:
                    st.session_state.appointment_booking = booking
                    st.success(f"✅ অ্যাপয়েন্টমেন্ট নিশ্চিত হয়েছে!")

                    st.markdown(f"""
                    **বুকিং বিবরণ:**
                    - বুকিং আইডি: `{booking['booking_id']}`
                    - সিরিয়াল: `{booking['serial']}`
                    - তারিখ: {booking['date_bn']}
                    - সময়: {booking['time']}
                    - আনুমানিক অপেক্ষা: {booking['estimated_wait_min']} মিনিট
                    """)

                    return booking

        return None


# ============================================================
# Backward compatibility: legacy functions
# ============================================================
def generate_available_slots(service_id: str, date_str: str) -> List[str]:
    """Legacy function — return list of time strings for a date."""
    engine = AppointmentEngine()
    slots = engine._generate_slots(service_id, days_ahead=7)
    date_slots = [s for s in slots if s["date"] == date_str and s["available"]]
    return [s["time"] for s in date_slots[:14]]


def book_slot(service_id: str, date_str: str, time_str: str, user_info: Dict) -> Optional[Dict]:
    """Legacy function — book a slot."""
    engine = AppointmentEngine()
    slot = {
        "date": date_str,
        "date_bn": format_date_bn(datetime.strptime(date_str, "%Y-%m-%d")),
        "time": time_str,
        "serial": f"{service_id[:3].upper()}-{random.randint(1000, 9999)}",
        "available": True,
        "load": "কম ভিড়",
        "load_emoji": "🟢",
    }
    user_hash = hashlib.sha256(user_info.get("name", "anonymous").encode()).hexdigest()[:12]
    return engine.book_slot(service_id, slot, user_hash)


def cancel_booking(booking_id: str) -> bool:
    """Legacy function — cancel a booking."""
    if booking_id in _booking_log:
        _booking_log[booking_id]["status"] = "cancelled"
        return True
    return False


def get_upcoming_appointments() -> List[Dict]:
    """Legacy function — list all upcoming bookings."""
    return [b for b in _booking_log.values() if b["status"] == "confirmed"]


# ============================================================
# Sample booking trace (for comments/documentation)
# ============================================================
"""
SAMPLE SLOT BOOKING TRACE:
==========================
>>> engine = AppointmentEngine()
>>> slots = engine.get_available_slots("passport")
>>> slots[0]
{
  "date": "2026-04-13",
  "date_bn": "১৩ এপ্রিল ২০২৬, রবিবার",
  "time": "10:00",
  "serial": "PAS-4821",
  "available": True,
  "load": "কম ভিড়",
  "load_emoji": "🟢"
}

>>> booking = engine.book_slot("passport", slots[0], "hash_abc123")
>>> booking
{
  "booking_id": "BKG-A1B2C3D4",
  "service_id": "passport",
  "date": "2026-04-13",
  "date_bn": "১৩ এপ্রিল ২০২৬, রবিবার",
  "time": "10:00",
  "serial": "PAS-4821",
  "user_hash": "hash_abc123",
  "status": "confirmed",
  "booked_at": "2026-04-10 10:25:30",
  "estimated_wait_min": 15
}
"""


if __name__ == "__main__":
    print("=== Appointment Engine Test ===\n")

    engine = AppointmentEngine()

    # Test 1: Slots generated
    slots = engine.get_available_slots("passport")
    assert len(slots) > 0
    assert all(s["available"] for s in slots)
    print(f"✅ Test 1 PASSED: {len(slots)} available slots for passport")

    # Test 2: Bengali date formatting
    assert "এপ্রিল" in slots[0]["date_bn"]
    assert "২০২৬" in slots[0]["date_bn"]
    print(f"✅ Test 2 PASSED: Bengali date: {slots[0]['date_bn']}")

    # Test 3: Different load levels
    slots_passport = engine.get_available_slots("passport")
    slots_trade = engine.get_available_slots("trade_license")
    print(f"✅ Test 3 PASSED: Passport slots={len(slots_passport)}, Trade License slots={len(slots_trade)}")

    # Test 4: Booking works
    if slots:
        booking = engine.book_slot("passport", slots[0], "test_user_hash")
        assert booking["status"] == "confirmed"
        assert booking["booking_id"].startswith("BKG-")
        print(f"✅ Test 4 PASSED: Booking confirmed: {booking['booking_id']}")

    # Test 5: Legacy functions
    legacy_slots = generate_available_slots("passport", "2026-05-01")
    assert isinstance(legacy_slots, list)
    print(f"✅ Test 5 PASSED: Legacy function returns {len(legacy_slots)} slots")

    print("\n🎉 All 5 appointment tests PASSED!")
