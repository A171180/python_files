# Demo Instructions

1. Start backend (mock server):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

2. Run Flutter stub (replace app main with `flutter/lib/main.dart`):

```bash
flutter run -d <device>
```

3. Demonstration flow
- Show the app; it polls `http://localhost:8080/current_mood` every 5s.
- Use `/analyze` to POST base64 images (or use webcam->encode) to demo mood switching.
- Use `/playlist?mood=stressed` to show mapped YouTube query.

4. Next steps to production
- Replace mock classifier with Gemini Vision API SDK calls (send camera frames every 5s).
- Deploy Vertex AI model for improved mapping and host a Cloud Function for low-latency inference.
- Use YouTube Data API or Spotify API with OAuth to fetch/stream playlists.
- Integrate Firebase Auth + Firestore to cache playlists and aggregate anonymized campus moods.
