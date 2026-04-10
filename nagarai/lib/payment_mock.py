"""
payment_mock.py — Mock payment engine with fraud detection for NagarAI.

All text in English for international hackathon.
"""

import hashlib
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import streamlit as st

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

_transaction_log: Dict[str, Dict] = {}


class PaymentVerifier:
    """Payment processor with visible fraud detection and OCR simulation."""

    def __init__(self):
        self.transaction_log = _transaction_log

    def process_payment(self, amount: float, method: str, service_id: str) -> dict:
        """Process a mock payment with full fraud detection."""
        txn_digits = random.randint(10000000, 99999999)
        service_prefix = service_id[:3].upper()
        transaction_id = f"NGA-{service_prefix}-{txn_digits}"

        is_duplicate = transaction_id in self.transaction_log

        fee_range = SERVICE_FEE_RANGES.get(service_id, (0, 10000))
        amount_valid = fee_range[0] <= amount <= fee_range[1] if fee_range[1] > 0 else amount == 0

        amount_suspicious = amount != int(amount) and (amount * 100) % 100 not in (0, 50)

        now = datetime.now()
        business_hours = now.weekday() < 5 and 9 <= now.hour < 17

        fraud_checks = {
            "amount_valid": amount_valid and not amount_suspicious,
            "amount_in_range": amount_valid,
            "suspicious_decimals": not amount_suspicious,
            "duplicate": is_duplicate,
            "business_hours": business_hours,
        }

        if is_duplicate:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "amount_paid": amount,
                "method": method,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "fraud_checks": fraud_checks,
                "error": "⚠️ Duplicate transaction detected!",
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
                "error": "⚠️ Suspicious decimal amount rejected!",
                "receipt_text": "",
                "sms_text": "",
            }

        ocr_confidence = random.randint(91, 98)

        self.transaction_log[transaction_id] = {
            "amount": amount,
            "method": method,
            "service_id": service_id,
            "timestamp": now.isoformat(),
        }

        receipt_text = (
            f"{'='*40}\n"
            f"        NagarAI Demo Receipt\n"
            f"{'='*40}\n"
            f"Transaction: {transaction_id}\n"
            f"Date: {now.strftime('%d/%m/%Y %H:%M')}\n"
            f"Amount: BDT {int(amount)}\n"
            f"Method: {method}\n"
            f"Status: ✅ Complete (Demo)\n"
            f"OCR Confidence: {ocr_confidence}%\n"
            f"{'='*40}"
        )

        sms_text = (
            f"NagarAI: Your payment for {service_id} is complete. "
            f"Amount: BDT {int(amount)}, TXN: {transaction_id}. "
            f"Please save this receipt."
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

    def render_payment_demo(self, amount: float, service_name_bn: str, service_id: str = "") -> dict:
        """Render full payment UI in Streamlit."""
        st.markdown(f"### 💳 Payment — {service_name_bn}")
        st.divider()

        st.markdown("**Fee Breakdown:**")
        if amount > 0:
            base_fee = int(amount * 0.6)
            service_charge = int(amount * 0.25)
            vat = amount - base_fee - service_charge

            fee_table = {
                "Description": ["Service Fee", "Service Charge", "VAT/Tax", "Total"],
                "Amount (BDT)": [base_fee, service_charge, vat, int(amount)],
            }
            st.table(fee_table)
        else:
            st.info("✅ This service is free!")

        if amount > 0:
            st.markdown("**Choose payment method:**")
            method = st.radio(
                "Method",
                options=["bKash", "Nagad", "Bank Transfer"],
                format_func=lambda x: {"bKash": "📱 bKash", "Nagad": "🟠 Nagad", "Bank Transfer": "🏦 Bank Transfer"}.get(x, x),
                horizontal=True,
                key=f"payment_method_{service_id}",
            )
        else:
            method = "Free"

        st.divider()

        if amount == 0:
            if st.button("✅ Free Service — Continue", type="primary"):
                result = self.process_payment(0, "Free", service_id)
                st.session_state.payment_result = result
                return result
        else:
            if st.button(f"💳 Pay Now (Demo) — BDT {int(amount)}", type="primary"):
                with st.spinner("Processing payment..."):
                    time.sleep(0.8)
                    result = self.process_payment(amount, method, service_id)
                    st.session_state.payment_result = result
                    return result

        if "payment_result" in st.session_state:
            result = st.session_state.payment_result

            if result.get("success"):
                st.success("✅ Payment Complete (Demo)")

                st.markdown("#### 🔐 Fraud Check Report")
                fc = result["fraud_checks"]

                col1, col2, col3, col4 = st.columns(4)
                col1.success("✅ Amount Valid" if fc["amount_valid"] else "❌ Amount Suspicious")
                col2.success("✅ Not Duplicate" if not fc["duplicate"] else "❌ Duplicate!")
                col3.success(f"✅ OCR: {fc['ocr_confidence']}%")
                col4.success("✅ Business Hours" if fc["business_hours"] else "⚠️ Outside Hours")

                st.markdown("#### 🧾 Receipt")
                st.code(result["receipt_text"], language=None)

                st.markdown("#### 📱 SMS Preview")
                st.info(result["sms_text"])

                return result
            else:
                st.error(result.get("error", "Payment Failed"))
                st.warning("⚠️ Fraud detection triggered!")

                fc = result["fraud_checks"]
                col1, col2 = st.columns(2)
                col1.error("✅ Amount Valid" if fc["amount_valid"] else "❌ Amount Suspicious")
                col2.error("✅ Not Duplicate" if not fc["duplicate"] else "❌ Duplicate!")

                return None

        return None


# Backward compatibility
def calculate_fee(service_id: str) -> int:
    """Legacy function."""
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
    """Legacy function."""
    tx_raw = f"{service_id}_{amount}_{user_phone}_{datetime.now().isoformat()}"
    transaction_id = "TXN" + hashlib.sha256(tx_raw.encode()).hexdigest()[:12].upper()
    return {
        "transaction_id": transaction_id,
        "service_id": service_id,
        "amount": amount,
        "user_phone": user_phone,
        "status": "pending",
        "message_bn": f"Payment processing. TXN: {transaction_id}",
    }


def verify_payment(transaction_id: str) -> Optional[Dict]:
    """Legacy function."""
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
        "message_bn": f"Payment successful. Receipt: {receipt_number}",
    }


def format_receipt(receipt: Dict) -> str:
    """Legacy function."""
    if not receipt or receipt.get("status") != "success":
        return "Payment receipt not found"
    return f"""
{'='*40}
        Payment Receipt
{'='*40}
Receipt No: {receipt.get('receipt_number', 'N/A')}
Date: {receipt.get('timestamp', 'N/A')}
Amount: BDT {receipt.get('amount_bdt', 0)}
Status: Successful ✅
{'='*40}
    """.strip()


if __name__ == "__main__":
    print("=== Payment Mock Module Test ===\n")

    pv = PaymentVerifier()

    r1 = pv.process_payment(5750, "bKash", "passport")
    assert r1["success"] == True
    assert r1["fraud_checks"]["amount_valid"] == True
    assert r1["fraud_checks"]["duplicate"] == False
    assert "NGA-PAS-" in r1["transaction_id"]
    print(f"✅ Test 1 PASSED: Normal payment processed")
    print(f"   TXN: {r1['transaction_id']}, OCR: {r1['fraud_checks']['ocr_confidence']}%")

    r2 = pv.process_payment(5750.13, "Nagad", "passport")
    assert r2["success"] == False
    assert "Suspicious" in r2["error"]
    print("✅ Test 2 PASSED: Suspicious decimals rejected")

    r3 = pv.process_payment(99999, "bKash", "passport")
    assert r3["fraud_checks"]["amount_in_range"] == False
    print("✅ Test 3 PASSED: Out-of-range amount flagged")

    r4 = pv.process_payment(0, "Free", "birth_certificate")
    assert r4["success"] == True
    assert r4["amount_paid"] == 0
    print("✅ Test 4 PASSED: Free service processed")

    assert calculate_fee("passport") == 3450
    assert calculate_fee("birth_certificate") == 0
    print("✅ Test 5 PASSED: Legacy functions working")

    print("\n🎉 All 5 payment tests PASSED!")
