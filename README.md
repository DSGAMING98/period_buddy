# 🩸 Period Buddy — v1.0 Offline Edition

**Period Buddy** is a fully **offline, privacy-first period tracking & support app** built with **Streamlit**.  
No APIs. No cloud. No data leaks. Everything stays **local on your machine**.

It combines:
- Cycle tracking
- Symptom & mood logging
- Pattern analysis
- Offline “AI Buddy” chat
- Self-care tools
- SOS emergency guidance
- Secure local authentication

This app is **not a medical diagnosis tool** — it’s a **support system** to help users understand their bodies better and feel less alone.

---

## ✨ Core Features

✅ **Secure Local Login System**
- Encrypted passwords (PBKDF2 + salt)
- Brute-force protection
- Profile-based private data
- Local-only storage

✅ **Cycle Tracker**
- Log period start dates
- Predict next period window
- PMS window detection
- Fertile window estimates

✅ **Symptoms & Mood Tracker**
- Pain level (0–10)
- Emotional state tracking
- Body symptom selection
- Personalized comfort analysis
- CSV export for doctor visits

✅ **Home Dashboard (Advanced Graphs)**
- Pain vs Cycle Day graph
- Mood vs PMS window comparison
- Average pain per cycle
- Next period countdown
- Pattern detection

✅ **Offline AI Buddy Chat**
- Rule-based emotional support
- Context-aware replies
- Knows your cycle + symptoms
- Works with **zero internet**

✅ **Self-Care Toolkit**
- Cramps, bloating, mood, anxiety, fatigue
- Energy-based quick actions (2 min, 10 min, 30 min)
- Gentle, realistic coping ideas

✅ **SOS Zone**
- Pain emergency support
- Heavy bleeding guidance
- Emotional distress support
- Dizziness & fainting safety
- Clear red-flag warnings

✅ **Exports**
- Period history → CSV
- Symptom & mood logs → CSV

---

## 🖥️ Tech Stack

- **Python 3.9+**
- **Streamlit**
- **Pandas**
- **Local JSON Storage**
- **PBKDF2 Cryptography (hashlib)**

No APIs. No cloud databases. No subscriptions.

---

## 📂 Project Structure

# 🩸 Period Buddy — v1.0 Offline Edition

**Period Buddy** is a fully **offline, privacy-first period tracking & support app** built with **Streamlit**.  
No APIs. No cloud. No data leaks. Everything stays **local on your machine**.

It combines:
- Cycle tracking
- Symptom & mood logging
- Pattern analysis
- Offline “AI Buddy” chat
- Self-care tools
- SOS emergency guidance
- Secure local authentication

This app is **not a medical diagnosis tool** — it’s a **support system** to help users understand their bodies better and feel less alone.

---

## ✨ Core Features

✅ **Secure Local Login System**
- Encrypted passwords (PBKDF2 + salt)
- Brute-force protection
- Profile-based private data
- Local-only storage

✅ **Cycle Tracker**
- Log period start dates
- Predict next period window
- PMS window detection
- Fertile window estimates

✅ **Symptoms & Mood Tracker**
- Pain level (0–10)
- Emotional state tracking
- Body symptom selection
- Personalized comfort analysis
- CSV export for doctor visits

✅ **Home Dashboard (Advanced Graphs)**
- Pain vs Cycle Day graph
- Mood vs PMS window comparison
- Average pain per cycle
- Next period countdown
- Pattern detection

✅ **Offline AI Buddy Chat**
- Rule-based emotional support
- Context-aware replies
- Knows your cycle + symptoms
- Works with **zero internet**

✅ **Self-Care Toolkit**
- Cramps, bloating, mood, anxiety, fatigue
- Energy-based quick actions (2 min, 10 min, 30 min)
- Gentle, realistic coping ideas

✅ **SOS Zone**
- Pain emergency support
- Heavy bleeding guidance
- Emotional distress support
- Dizziness & fainting safety
- Clear red-flag warnings

✅ **Exports**
- Period history → CSV
- Symptom & mood logs → CSV

---

## 🖥️ Tech Stack

- **Python 3.9+**
- **Streamlit**
- **Pandas**
- **Local JSON Storage**
- **PBKDF2 Cryptography (hashlib)**

No APIs. No cloud databases. No subscriptions.

---

## 📂 Project Structure



period_buddy/
│
├── app.py
├── pages/
│ ├── 0_Login_Profile.py
│ ├── 1_Home.py
│ ├── 2_Cycle_Tracker.py
│ ├── 3_Symptoms_Mood.py
│ ├── 4_AIBuddyChat.py
│ ├── 5_SelfCare.py
│ └── 6_SOS.py
│
├── utils/
│ ├── auth_utils.py
│ ├── cycle_utils.py
│ ├── symptom_utils.py
│ ├── storage_utils.py
│ ├── session_data.py
│ ├── offline_chat.py
│ └── ui_utils.py
│
├── data/
│ ├── users.json
│ ├── cycle_examples.json
│ ├── symptoms_map.json
│ └── users/
│
├── assets/
│ ├── styles.css
│ └── logo.png
│
├── requirements.txt
└── README.md
🔐 Privacy & Security

100% offline operation

No internet requests

No third-party APIs

Encrypted local passwords

Each profile has separate private logs

Data stored only in /data/

You own your data. Always.

⚠️ Medical Disclaimer

This application is not a medical device and does not provide medical diagnosis or treatment.

For:

Severe pain
Extreme bleeding
Fainting
Mental health crises
Users must seek real medical professionals immediately.

🧠 Use Cases

Personal cycle awareness
Exam stress + PMS tracking
Chronic pain pattern detection
Emotional support during periods
Doctor visit preparation
Mental health journaling
Educational health projects

🏗️ Future Roadmap

Desktop executable build
Backup & restore
Visual theme switcher
Notifications
PDF health summary export
Wearable data integration (optional, offline sync)

👨‍💻 Developed By Prajwal or dsgaming on GitHub

Built with focus on:

Privacy
Emotional safety
Real-world usefulness
Offline-first design

✅ Status

Stable Release: v1.0 – Offline Edition
Ready for:
Health-tech demos
Portfolio showcase
Personal daily use
