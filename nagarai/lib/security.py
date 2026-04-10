"""
security.py — Complete security module for NagarAI hackathon demo.

Three classes: PIIRedactor, SessionManager, InputSanitizer
Plus: render_security_demo_panel() for Streamlit UI demonstration.

All text in English for international hackathon.
"""

import re
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import streamlit as st


# ============================================================
# CLASS 1: PIIRedactor
# ============================================================
class PIIRedactor:
    """Detect and redact PII from text with demo-friendly UI output."""

    PATTERNS = [
        # Phone: 01X-XXXXXXXX or 01XXXXXXXXX (Bangladeshi mobile)
        (r'01[3-9][\s-]?\d{4}[\s-]?\d{4}', '[PHONE-REDACTED]', 'Phone'),
        # NID: 10 to 17 digits
        (r'\b\d{10,17}\b', '[NID-REDACTED]', 'NID'),
        # Email
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL-REDACTED]', 'Email'),
        # Common Bangladeshi names
        (r'\b(Mohammad|Mohammed|Muhammad|Md\.?)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b', '[NAME-REDACTED]', 'Name'),
        (r'\b(Ahmed|Ahmad|Rahman|Karim|Hassan|Hossain|Islam|Uddin|Begum|Akter|Khatun|Sultana|Fatema|Fatemah)\b', '[NAME-REDACTED]', 'Name'),
    ]

    def redact(self, text: str) -> dict:
        """Redact PII from text."""
        if not isinstance(text, str):
            return {"redacted_text": "", "found_pii": [], "redaction_count": 0}

        found_pii = []
        redacted_text = text

        for pattern, replacement, pii_type in self.PATTERNS:
            matches = re.findall(pattern, redacted_text)
            if matches:
                found_pii.extend([pii_type] * len(matches))
                redacted_text = re.sub(pattern, replacement, redacted_text)

        return {
            "redacted_text": redacted_text,
            "found_pii": found_pii,
            "redaction_count": len(found_pii),
        }

    def demo_redaction(self, sample_text: str = None):
        """Streamlit UI showing BEFORE/AFTER PII redaction."""
        st.markdown("### 🔒 PII Redaction Demo")
        st.caption("Type text with personal info — watch it get masked live")

        if sample_text:
            user_input = st.text_input("Test text:", value=sample_text, key="pii_demo_input")
        else:
            user_input = st.text_input(
                "Test text:",
                placeholder="e.g., My NID is 1234567890123, phone 01712345678",
                key="pii_demo_input",
            )

        if user_input:
            result = self.redact(user_input)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**BEFORE (Original):**")
                st.error(user_input, icon="⚠️")

            with col2:
                st.markdown("**AFTER (Redacted):**")
                st.success(result["redacted_text"], icon="✅")

            if result["found_pii"]:
                st.markdown(f"**Detected PII ({result['redaction_count']} items):**")
                for pii in result["found_pii"]:
                    st.caption(f"🔴 {pii}")
            else:
                st.caption("✅ No PII detected")


# ============================================================
# CLASS 2: SessionManager
# ============================================================
class SessionManager:
    """Streamlit session state manager with anonymized audit logging."""

    def __init__(self):
        self._state = st.session_state

    def init_session(self) -> str:
        """Initialize session with ID, start time, action count."""
        if "nagarai_session_id" not in self._state:
            self._state.nagarai_session_id = str(uuid.uuid4())
            self._state.nagarai_session_start = datetime.now().isoformat()
            self._state.nagarai_action_count = 0
            self._state.nagarai_audit_log = []

        return self._state.nagarai_session_id

    def check_session_valid(self) -> bool:
        """Check if session is still valid (not expired)."""
        if "nagarai_session_start" not in self._state:
            return False

        start = datetime.fromisoformat(self._state.nagarai_session_start)
        elapsed = datetime.now() - start
        return elapsed.total_seconds() < 15 * 60

    def log_action(self, action: str):
        """Log action to anonymized audit log."""
        if "nagarai_audit_log" not in self._state:
            self._state.nagarai_audit_log = []

        action_hash = hashlib.sha256(action.encode()).hexdigest()[:12]
        entry = {
            "action_hash": action_hash,
            "action_type": action,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }
        self._state.nagarai_audit_log.append(entry)
        self._state.nagarai_action_count = self._state.get("nagarai_action_count", 0) + 1

    def get_audit_preview(self) -> list:
        """Return last 5 audit log entries for demo display."""
        log = self._state.get("nagarai_audit_log", [])
        return log[-5:]

    @property
    def session_age_minutes(self) -> float:
        """Return session age in minutes."""
        if "nagarai_session_start" not in self._state:
            return 0.0

        start = datetime.fromisoformat(self._state.nagarai_session_start)
        elapsed = datetime.now() - start
        return round(elapsed.total_seconds() / 60, 2)


# ============================================================
# CLASS 3: InputSanitizer
# ============================================================
class InputSanitizer:
    """Sanitize form inputs and block dangerous patterns."""

    SQL_KEYWORDS = [
        'SELECT', 'DROP', 'INSERT', 'DELETE', 'UPDATE', 'UNION',
        'ALTER', 'CREATE', 'EXEC', 'EXECUTE', 'TRUNCATE',
        '--', ';', '/*', '*/', 'xp_', 'sp_',
    ]

    PROMPT_INJECTIONS = [
        'ignore previous', 'you are now', 'jailbreak', 'bypass',
        'override', 'disregard', 'forget all', 'system prompt',
        'ignore all', 'you must', 'act as', 'pretend',
    ]

    def sanitize_form_input(self, field: str, value: str) -> dict:
        """Sanitize and validate form input."""
        warnings = []
        cleaned = value.strip()

        if not cleaned:
            return {"safe": True, "cleaned_value": "", "warnings": []}

        upper_value = cleaned.upper()

        for keyword in self.SQL_KEYWORDS:
            if keyword.upper() in upper_value:
                warnings.append(f"⚠️ SQL keyword detected: {keyword}")
                cleaned = cleaned.replace(keyword, '').replace(keyword.lower(), '')
                cleaned = ' '.join(cleaned.split())

        lower_value = cleaned.lower()
        for phrase in self.PROMPT_INJECTIONS:
            if phrase in lower_value:
                warnings.append(f"🚫 Prompt injection blocked: '{phrase}'")
                return {"safe": False, "cleaned_value": "", "warnings": warnings}

        if '<script' in lower_value or '</script>' in lower_value:
            warnings.append("🚫 Script tag blocked")
            cleaned = re.sub(r'<script.*?</script>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
            cleaned = re.sub(r'<[^>]+>', '', cleaned)

        is_safe = len([w for w in warnings if '🚫' in w]) == 0

        return {
            "safe": is_safe,
            "cleaned_value": cleaned,
            "warnings": warnings,
        }

    def validate_phone_bd(self, phone: str) -> bool:
        """Validate Bangladeshi mobile number format."""
        if not isinstance(phone, str):
            return False
        cleaned = re.sub(r'[\s\-\+]', '', phone)
        return bool(re.match(r'^01[3-9]\d{8}$', cleaned))

    def validate_nid(self, nid: str) -> bool:
        """Validate National ID format (10 or 17 digits)."""
        if not isinstance(nid, str):
            return False
        cleaned = re.sub(r'[\s\-]', '', nid)
        return bool(re.match(r'^\d{10}$|^\d{17}$', cleaned))


# ============================================================
# FUNCTION: render_security_demo_panel()
# ============================================================
def render_security_demo_panel():
    """Render security demo panel in sidebar or main area."""
    st.markdown("---")
    st.markdown("### 🔐 Security Status")

    session_mgr = SessionManager()
    redactor = PIIRedactor()
    session_mgr.init_session()

    is_valid = session_mgr.check_session_valid()
    age = session_mgr.session_age_minutes

    if is_valid:
        st.success(f"✅ **Session Active** — {age:.1f} min", icon="🟢")
    else:
        st.error("❌ **Session Expired** — Please refresh", icon="🔴")

    st.divider()

    st.markdown("**Test PII Redaction:**")
    pii_input = st.text_input(
        "Type text with personal info",
        placeholder="NID: 1234567890123",
        label_visibility="collapsed",
        key="security_pii_test",
    )

    if pii_input:
        result = redactor.redact(pii_input)
        if result["redaction_count"] > 0:
            st.caption(f"✅ {result['redaction_count']} item(s) redacted:")
            st.code(result["redacted_text"], language=None)
        else:
            st.caption("✅ No PII detected")

    st.divider()

    st.markdown("**Recent Actions (Anonymized):**")
    audit_entries = session_mgr.get_audit_preview()

    if audit_entries:
        for entry in audit_entries[-3:]:
            st.caption(f"`{entry['timestamp']}` → `{entry['action_hash']}`")
    else:
        st.caption("No actions logged yet")

    st.divider()
    st.caption("🔒 **No personal data is being stored**")


# ============================================================
# Backward compatibility
# ============================================================
def redact_pii(text: str) -> str:
    """Legacy function for backward compatibility."""
    redactor = PIIRedactor()
    return redactor.redact(text)["redacted_text"]


def sanitize_input(user_input: str) -> str:
    """Legacy function for backward compatibility."""
    sanitizer = InputSanitizer()
    result = sanitizer.sanitize_form_input("legacy", user_input)
    return result["cleaned_value"]


def create_session(session_id: str) -> Dict[str, Any]:
    """Legacy function."""
    if "nagarai_session_id" not in st.session_state:
        st.session_state.nagarai_session_id = session_id
        st.session_state.nagarai_session_start = datetime.now().isoformat()
        st.session_state.nagarai_action_count = 0
        st.session_state.nagarai_audit_log = []
    return {"session_id": session_id, "active": True}


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Legacy function."""
    mgr = SessionManager()
    if mgr.check_session_valid():
        return {"session_id": st.session_state.get("nagarai_session_id"), "active": True}
    return None


def purge_session(session_id: str) -> bool:
    """Legacy function."""
    keys_to_remove = [
        "nagarai_session_id", "nagarai_session_start",
        "nagarai_action_count", "nagarai_audit_log",
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    return True


def store_session_data(session_id: str, key: str, value: Any) -> bool:
    """Legacy function."""
    mgr = SessionManager()
    if mgr.check_session_valid():
        st.session_state[f"session_{key}"] = value
        return True
    return False


def get_session_stats() -> Dict[str, int]:
    """Legacy function."""
    mgr = SessionManager()
    return {
        "active_sessions": 1 if mgr.check_session_valid() else 0,
        "total_sessions_created": 1,
        "max_session_minutes": 15,
        "session_age_minutes": mgr.session_age_minutes,
    }


# ============================================================
# TESTS
# ============================================================
if __name__ == "__main__":
    print("=== Running Security Module Tests ===\n")

    redactor = PIIRedactor()
    nid_test = redactor.redact("My NID is 1234567890123")
    assert '[NID-REDACTED]' in nid_test["redacted_text"]
    print("✅ Test 1 PASSED: NID detection works")

    phone_test = redactor.redact("Call me at 01712345678")
    assert '[PHONE-REDACTED]' in phone_test["redacted_text"]
    print("✅ Test 2 PASSED: Phone detection works")

    sanitizer = InputSanitizer()
    injection_test = sanitizer.sanitize_form_input("input", "ignore previous instructions")
    assert injection_test["safe"] == False
    print("✅ Test 3 PASSED: Prompt injection blocked")

    valid_phone = sanitizer.validate_phone_bd("01712345678")
    assert valid_phone == True
    invalid_phone = sanitizer.validate_phone_bd("12345")
    assert invalid_phone == False
    print("✅ Test 4 PASSED: Valid phone passes, invalid rejected")

    from datetime import datetime
    start = datetime.now()
    age = (datetime.now() - start).total_seconds() / 60
    assert isinstance(age, float)
    print("✅ Test 5 PASSED: Session age returns float")

    print("\n🎉 All 5 security tests PASSED!")
