# AI Mood Tunes — Prototype

Overview
- Real-time face-based mood detection (Gemini Vision API placeholder)
- Vertex AI mapping (mocked endpoint) maps moods → playlist queries
- Flutter front-end stub demonstrates camera polling every 5s
- Firebase placeholders for Auth / Firestore caching

Quick start (backend)
1. Create venv: `python3 -m venv .venv && source .venv/bin/activate`
2. Install: `pip install -r backend/requirements.txt`
3. Run server: `python backend/app.py`

Flutter
- `flutter create mood_tunes` then replace `lib/main.dart` with the provided stub in `flutter/lib/main.dart`.

Notes
- Gemini Vision and Vertex AI calls are stubbed/mocked. Replace with real SDK calls and credentials for production.
