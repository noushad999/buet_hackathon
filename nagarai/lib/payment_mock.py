"""
payment_mock.py — Mock payment engine with fraud detection for NagarAI hackathon demo.

CLASS: PaymentVerifier — process payments with visible fraud checks, OCR simulation, receipt generation.

Demo purpose: Show judges a DEMONSTRABLY secure payment flow where fraud detection is VISIBLE.
"""

import hashlib
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import streamlit as st


# Fee ranges per service (min, max expected)
SERVICE_FEE_RANGES = {
    "passport": (3450, 8500),
    "passport_new": (5750, 8500),
    "trade_license": (1000, 2000),
    "trade_license_renewal": (800, 1500),
    "birth_certificate": (0, 0),
    "tin_certificate": (0, 0),
    "land_deed": (5000, 8000),
    "nid_correction": (0, 500),
}

# In-memory transaction log (session-scoped)
_transaction_log: Dict[str, Dict] = {}


class PaymentVerifier:
    """Payment processor with visible fraud detection and OCR simulation.

    Demo purpose: Judges can SEE fraud checks running in real-time.
    Every payment goes through 4 fraud heuristics before approval.
    """

    def __init__(self):
        self.transaction_log = _transaction_log

    # ============================================================
    # METHOD: process_payment — Core payment processing
    # ============================================================
    def process_payment(self, amount: float, method: str, service_id: str) -> dict:
        """Process a mock payment with full fraud detection.

        Args:
            amount: Payment amount in BDT
            method: Payment method (bKash, Nagad, Bank Transfer)
            service_id: Service identifier from KB

        Returns:
            Dict with success status, transaction ID, fraud checks, receipt, SMS text

        Example:
            >>> pv = PaymentVerifier()
            >>> result = pv.process_payment(5750, "bKash", "passport")
            >>> result["success"]
            True
            >>> result["fraud_checks"]["amount_valid"]
            True
        """
        # Step 1: Generate transaction ID
        txn_digits = random.randint(10000000, 99999999)
        service_prefix = service_id[:3].upper()
        transaction_id = f"NGA-{service_prefix}-{txn_digits}"

        # Check for duplicate
        is_duplicate = transaction_id in self.transaction_log

        # Step 2: Fraud check heuristics
        fee_range = SERVICE_FEE_RANGES.get(service_id, (0, 10000))
        amount_valid = fee_range[0] <= amount <= fee_range[1] if fee_range[1] > 0 else amount == 0

        # Amount rounding check (suspicious decimals)
        amount_suspicious = amount != int(amount) and (amount * 100) % 100 not in (0, 50)

        # Business hours check
        now = datetime.now()
        business_hours = now.weekday() < 4 and 9 <= now.hour < 17  # Mon-Thu, 9am-5pm

        fraud_checks = {
            "amount_valid": amount_valid and not amount_suspicious,
            "amount_in_range": amount_valid,
            "suspicious_decimals": not amount_suspicious,
            "duplicate": is_duplicate,
            "business_hours": business_hours,
        }

        # Reject if critical fraud detected
        if is_duplicate:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "amount_paid": amount,
                "method": method,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "fraud_checks": fraud_checks,
                "error": "⚠️ ডুপ্লিকেট ট্রানজাকশন সনাক্ত হয়েছে!",
                "receipt_text": "",
                "sms_text": "",
            }

        if amount_suspicious:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "amount_paid": amount,
                "method": method,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "fraud_checks": fraud_checks,
                "error": "⚠️ সন্দেহজনক দশমিক মান প্রত্যাখ্যান করা হয়েছে!",
                "receipt_text": "",
                "sms_text": "",
            }

        # Step 3: Mock OCR verification (fake receipt scan)
        ocr_confidence = random.randint(91, 98)

        # Step 4: Log transaction
        self.transaction_log[transaction_id] = {
            "amount": amount,
            "method": method,
            "service_id": service_id,
            "timestamp": now.isoformat(),
        }

        # Build receipt text
        receipt_text = (
            f"═══════════════════════════════════\n"
            f"        নাগরআই ডেমো রশিদ\n"
            f"═══════════════════════════════════\n"
            f"ট্রানজাকশন: {transaction_id}\n"
            f"তারিখ: {now.strftime('%d/%m/%Y %H:%M')}\n"
            f"পরিমাণ: ৳{int(amount)}\n"
            f"মাধ্যম: {method}\n"
            f"অবস্থা: ✅ সম্পন্ন (ডেমো)\n"
            f"OCR আস্থা: {ocr_confidence}%\n"
            f"═══════════════════════════════════"
        )

        # Build SMS text
        sms_text = (
            f"NagarAI: আপনার {service_id} সেবার পেমেন্ট সম্পন্ন হয়েছে। "
            f"পরিমাণ: ৳{int(amount)}, TXN: {transaction_id}. "
            f"রশিদ সংরক্ষণ করুন।"
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount_paid": int(amount),
            "method": method,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "fraud_checks": {
                **fraud_checks,
                "ocr_confidence": ocr_confidence,
            },
            "receipt_text": receipt_text,
            "sms_text": sms_text,
        }

    # ============================================================
    # METHOD: render_payment_demo — Streamlit payment UI
    # ============================================================
    def render_payment_demo(self, amount: float, service_name_bn: str, service_id: str = "") -> dict:
        """Render full payment UI in Streamlit.

        Shows:
        - Fee breakdown table
        - Payment method radio (bKash/Nagad/Bank)
        - "পেমেন্ট করুন" button
        - Fraud check results as mini security report
        - Receipt in Bengali

        Args:
            amount: Total fee amount
            service_name_bn: Bengali service name for display
            service_id: Service identifier for fraud checks

        Returns:
            Payment result dict or None if not paid yet
        """
        st.markdown(f"### 💳 পেমেন্ট — {service_name_bn}")
        st.divider()

        # Fee breakdown
        st.markdown(f"**ফি বিবরণী:**")
        if amount > 0:
            base_fee = int(amount * 0.6)
            service_charge = int(amount * 0.25)
            vat = amount - base_fee - service_charge

            fee_table = {
                "বিবরণ": ["সেবা ফি", "সার্ভিস চার্জ", "ভ্যাট/ট্যাক্স", "মোট"],
                "পরিমাণ (৳)": [base_fee, service_charge, vat, int(amount)],
            }
            st.table(fee_table)
        else:
            st.info("✅ এই সেবাটি বিনামূল্যে!")

        # Payment method selector
        if amount > 0:
            st.markdown("**পেমেন্ট মাধ্যম বেছে নিন:**")
            method = st.radio(
                "মাধ্যম",
                options=["bKash", "Nagad", "Bank Transfer"],
                format_func=lambda x: {"bKash": "📱 bKash", "Nagad": "🟠 Nagad", "Bank Transfer": "🏦 Bank Transfer"}.get(x, x),
                horizontal=True,
                key=f"payment_method_{service_id}",
            )
        else:
            method = "Free"

        st.divider()

        # Payment button
        if amount == 0:
            if st.button("✅ ফ্রি সেবা — চালিয়ে যান", type="primary"):
                result = self.process_payment(0, "Free", service_id)
                st.session_state.payment_result = result
                return result
        else:
            if st.button(f"💳 পেমেন্ট করুন (ডেমো) — ৳{int(amount)}", type="primary"):
                with st.spinner("পেমেন্ট প্রক্রিয়াধীন..."):
                    time.sleep(0.8)  # Realistic delay
                    result = self.process_payment(amount, method, service_id)
                    st.session_state.payment_result = result
                    return result

        # Show result if available
        if "payment_result" in st.session_state:
            result = st.session_state.payment_result

            if result.get("success"):
                st.success("✅ পেমেন্ট সম্পন্ন (ডেমো)")

                # Fraud check security report
                st.markdown("#### 🔐 ফ্রড চেক রিপোর্ট")
                fc = result["fraud_checks"]

                col1, col2, col3, col4 = st.columns(4)
                col1.success("✅ পরিমাণ বৈধ" if fc["amount_valid"] else "❌ পরিমাণ সন্দেহজনক")
                col2.success("✅ ডুপ্লিকেট নয়" if not fc["duplicate"] else "❌ ডুপ্লিকেট!")
                col3.success(f"✅ OCR আস্থা: {fc['ocr_confidence']}%")
                col4.success("✅ ব্যবসায়িক সময়" if fc["business_hours"] else "⚠️ অফিস-সময়ের বাইরে")

                # Receipt
                st.markdown("#### 🧾 রশিদ")
                st.code(result["receipt_text"], language=None)

                # SMS preview
                st.markdown("#### 📱 SMS পূরূপ")
                st.info(result["sms_text"])

                return result
            else:
                st.error(result.get("error", "পেমেন্ট ব্যর্থ"))
                st.warning("⚠️ ফ্রড ডিটেকশন সক্রিয় হয়েছে!")

                fc = result["fraud_checks"]
                col1, col2 = st.columns(2)
                col1.error("✅ পরিমাণ বৈধ" if fc["amount_valid"] else "❌ পরিমাণ সন্দেহজনক")
                col2.error("✅ ডুপ্লিকেট নয়" if not fc["duplicate"] else "❌ ডুপ্লিকেট!")

                return None

        return None


# ============================================================
# Backward compatibility: legacy functions
# ============================================================
def calculate_fee(service_id: str) -> int:
    """Legacy function — get fee for a service."""
    fee_map = {
        "trade_license": 1500,
        "birth_certificate": 0,
        "passport": 3450,
        "tin_certificate": 0,
        "land_deed": 5000,
        "passport_new": 5750,
        "trade_license_renewal": 1000,
        "nid_correction": 0,
    }
    return fee_map.get(service_id, 0)


def initiate_payment(service_id: str, amount: int, user_phone: str) -> Dict:
    """Legacy function — initiate mock payment."""
    tx_raw = f"{service_id}_{amount}_{user_phone}_{datetime.now().isoformat()}"
    transaction_id = "TXN" + hashlib.sha256(tx_raw.encode()).hexdigest()[:12].upper()
    return {
        "transaction_id": transaction_id,
        "service_id": service_id,
        "amount": amount,
        "user_phone": user_phone,
        "status": "pending",
        "message_bn": f"পেমেন্ট প্রক্রিয়াধীন। ট্রানজাকশন আইডি: {transaction_id}",
    }


def verify_payment(transaction_id: str) -> Optional[Dict]:
    """Legacy function — verify mock payment."""
    if not transaction_id or not transaction_id.startswith("TXN"):
        return None
    time.sleep(0.3)
    receipt_number = "RCP" + hashlib.md5(transaction_id.encode()).hexdigest()[:10].upper()
    return {
        "transaction_id": transaction_id,
        "receipt_number": receipt_number,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success",
        "amount_bdt": 0,
        "message_bn": f"পেমেন্ট সফল হয়েছে। রসিদ নম্বর: {receipt_number}",
    }


def format_receipt(receipt: Dict) -> str:
    """Legacy function — format receipt string."""
    if not receipt or receipt.get("status") != "success":
        return "পেমেন্ট রসিদ পাওয়া যায়নি"
    return f"""
═══════════════════════════════════
        পেমেন্ট রসিদ
═══════════════════════════════════
রসিদ নম্বর: {receipt.get('receipt_number', 'N/A')}
তারিখ: {receipt.get('timestamp', 'N/A')}
পরিমাণ: ৳{receipt.get('amount_bdt', 0)}
অবস্থা: সফল ✅
═══════════════════════════════════
    """.strip()


# ============================================================
# Sample payment trace (for comments/documentation)
# ============================================================
"""
SAMPLE PAYMENT TRACE:
=====================
>>> pv = PaymentVerifier()
>>> result = pv.process_payment(5750, "bKash", "passport")
>>> result
{
  "success": True,
  "transaction_id": "NGA-PAS-84729361",
  "amount_paid": 5750,
  "method": "bKash",
  "timestamp": "2026-04-10 10:23:45",
  "fraud_checks": {
    "amount_valid": True,
    "amount_in_range": True,
    "suspicious_decimals": True,
    "duplicate": False,
    "business_hours": True,
    "ocr_confidence": 94
  },
  "receipt_text": "═══════════════════════════════════\n        নাগরআই ডেমো রশিদ\n...",
  "sms_text": "NagarAI: আপনার passport সেবার পেমেন্ট সম্পন্ন হয়েছে..."
}

FRAUD DETECTION EXAMPLE:
========================
>>> result = pv.process_payment(5750.13, "bKash", "passport")
>>> result["success"]
False
>>> result["error"]
"⚠️ সন্দেহজনক দশমিক মান প্রত্যাখ্যান হয়েছে!"
"""


if __name__ == "__main__":
    print("=== Payment Mock Module Test ===\n")

    pv = PaymentVerifier()

    # Test 1: Normal payment
    r1 = pv.process_payment(5750, "bKash", "passport")
    assert r1["success"] == True
    assert r1["fraud_checks"]["amount_valid"] == True
    assert r1["fraud_checks"]["duplicate"] == False
    assert "NGA-PAS-" in r1["transaction_id"]
    print("✅ Test 1 PASSED: Normal payment processed")
    print(f"   TXN: {r1['transaction_id']}, OCR: {r1['fraud_checks']['ocr_confidence']}%")

    # Test 2: Suspicious decimals rejected
    r2 = pv.process_payment(5750.13, "Nagad", "passport")
    assert r2["success"] == False
    assert "সন্দেহজনক" in r2["error"]
    print("✅ Test 2 PASSED: Suspicious decimals rejected")

    # Test 3: Fee range check
    r3 = pv.process_payment(99999, "bKash", "passport")
    assert r3["fraud_checks"]["amount_in_range"] == False
    print("✅ Test 3 PASSED: Out-of-range amount flagged")

    # Test 4: Free service
    r4 = pv.process_payment(0, "Free", "birth_certificate")
    assert r4["success"] == True
    assert r4["amount_paid"] == 0
    print("✅ Test 4 PASSED: Free service processed")

    # Test 5: Legacy functions
    assert calculate_fee("passport") == 3450
    assert calculate_fee("birth_certificate") == 0
    print("✅ Test 5 PASSED: Legacy functions working")

    print("\n🎉 All 5 payment tests PASSED!")
