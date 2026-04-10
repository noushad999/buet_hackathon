# NagarAI — নাগরআই

> **এক অ্যাপ, দুই সেবা** | AI-Powered Civic Service Platform

## Quick Start

```bash
cd nagarai
pip install -r requirements.txt
streamlit run NagarAI.py
```

Opens at: `http://localhost:8501`

---

## Demo Script (2 min 10 sec)

### 1. Landing Page (10s)
- Show two service cards: 🏛️ Government + 🚨 Social
- Point out bilingual UI (বাংলা default)
- Security footer: "কোনো ব্যক্তিগত তথ্য সংরক্ষিত হচ্ছে না"

### 2. Government Service (60s)
- Click 🏛️ সরকারি সেবা
- Type: **"পাসপোর্ট নবায়ন করতে চাই"**
- Show AI detects intent with confidence bar
- Follow guided form (5 questions, one at a time)
- Show real-time validation (green ✅/red ❌)
- Complete payment mock (bKash)
- Appointment confirmed → **balloons animation** 🎉
- Show SMS mockup in phone frame

### 3. Social Service (30s)
- Click 🚨 সামাজিক সেবা
- Show emergency numbers (999, 199, 100) — always visible
- Click 🏥 হাসপাতাল → show 3 nearest hospitals
- Show "কল করুন" and "দিকনির্দেশনা" buttons
- Point out: **No login required, zero friction**

### 4. Heatmap Dashboard (20s)
- Click 📊 ফিডব্যাক হিটম্যাপ
- Show 4 summary metrics (applications, NagarAI %, time saved, taka saved)
- Point to B2G value: "NagarAI SaaS: ৳৫-২০ লক্ষ/বছর/অফিস"
- Show comparison table: myGov vs NagarAI (all ✅ for NagarAI)

### 5. Security Demo (10s)
- In sidebar, type NID/phone in PII redaction test
- Show live redaction
- Show anonymized audit log

---

## Features

| Feature | Status |
|---------|--------|
| AI Intent Detection (Bengali/English) | ✅ |
| Guided Form (one question at a time) | ✅ |
| PII Redaction (NID, Phone, Email, Names) | ✅ |
| Session Management (15-min expiry) | ✅ |
| Input Sanitization (SQL injection, prompt injection) | ✅ |
| Mock Payment (bKash/Nagad/Bank) | ✅ |
| Fraud Detection (amount, decimals, duplicates) | ✅ |
| Appointment Booking (synthetic slots) | ✅ |
| Emergency Service Finder (zero login) | ✅ |
| Government Analytics Dashboard (B2G) | ✅ |
| Bilingual UI (বাংলা + English) | ✅ |

## Architecture

```
NagarAI.py (landing)
├── pages/1_Govt_Service.py  (AI → form → payment → appointment)
├── pages/2_Social_Service.py (emergency finder, zero login)
├── pages/3_Heatmap.py        (B2G analytics dashboard)
└── lib/
    ├── ai_engine.py          (NagarAIEngine: intent, questions, validation, checklist)
    ├── security.py           (PIIRedactor, SessionManager, InputSanitizer)
    ├── payment_mock.py       (PaymentVerifier: fraud detection, OCR simulation)
    ├── appointment.py        (AppointmentEngine: slots, booking, load levels)
    ├── location_mock.py      (LocationService: haversine distance)
    ├── synthetic_data.py     (heatmap data, weekly tables, summary metrics)
    └── i18n.py               (bilingual translations)
```

## Team

- AI/Backend: NagarAI Engine + Security Module
- Frontend: Streamlit multi-page app
- Data: Synthetic analytics + emergency DB
- UX: Bengali-first, zero-login emergency services

## License

MIT — Impact Dhaka 2026 Hackathon
