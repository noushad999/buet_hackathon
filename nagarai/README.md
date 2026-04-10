# NagarAI — AI-Powered Civic Service Platform

> **One App, Two Services** — Simplify government. Get emergency help instantly.

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
- Show three service cards: Government + Social + Analytics
- Point out clean, professional English UI
- Security footer: "No personal data is being stored"

### 2. Government Service (60s)
- Click 🏛️ Government Service
- Type: **"passport renewal"**
- Show AI detects intent with confidence bar
- Follow guided form (5 questions, one at a time)
- Show real-time validation (green ✅/red ❌)
- Complete payment mock (bKash)
- Appointment confirmed → **balloons animation** 🎉
- Show SMS mockup

### 3. Social Service (30s)
- Click 🚨 Social Service
- Show emergency numbers (999, 199, 100) — always visible
- Click 🏥 Hospitals → show 3 nearest with distance
- Show "Call" and "Directions" buttons
- Point out: **No login required, zero friction**

### 4. Heatmap Dashboard (20s)
- Click 📊 Feedback Heatmap
- Show 4 summary metrics (applications, NagarAI %, time saved, cost savings)
- Point to B2G value: "NagarAI SaaS: BDT 5-20 lakh/year/office"
- Show comparison table: myGov vs NagarAI (all ✅ for NagarAI)

### 5. Security Demo (10s)
- In sidebar, type NID/phone in PII redaction test
- Show live redaction
- Show anonymized audit log

---

## Features

| Feature | Status |
|---------|--------|
| AI Intent Detection (keyword-based) | ✅ |
| Guided Form (one question at a time) | ✅ |
| PII Redaction (NID, Phone, Email, Names) | ✅ |
| Session Management (15-min expiry) | ✅ |
| Input Sanitization (SQL injection, prompt injection) | ✅ |
| Mock Payment (bKash/Nagad/Bank) | ✅ |
| Fraud Detection (amount, decimals, duplicates, OCR) | ✅ |
| Appointment Booking (synthetic slots with load levels) | ✅ |
| Emergency Service Finder (zero login) | ✅ |
| Government Analytics Dashboard (B2G) | ✅ |
| Bilingual UI (English default) | ✅ |

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
    └── i18n.py               (translation engine)
```

## Tech Stack

- **Frontend:** Streamlit (Python)
- **AI:** Keyword-based intent detection (no external API)
- **Security:** Regex-based PII detection, SHA-256 audit logging
- **Data:** Synthetic JSON seed data
- **Geo:** Haversine formula for distance calculation

## License

MIT — Impact Dhaka 2026 Hackathon
