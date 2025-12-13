from flask import Flask, request, jsonify
from random import choice
import time

app = Flask(__name__)

# Simple in-memory state to simulate campus aggregation
AGGREGATED = { 'happy': 0, 'stressed': 0, 'focused': 0, 'neutral': 0 }

def mock_classify_image(image_b64: str) -> str:
    # Mock classifier: rotate moods based on current second for deterministic demo
    s = int(time.time())
    mod = s % 20
    if mod < 6:
        return 'focused'
    if mod < 12:
        return 'stressed'
    if mod < 16:
        return 'happy'
    return 'neutral'

MOOD_TO_YT = {
    'happy': 'Upbeat EDM mix',
    'stressed': 'Lo-fi study beats',
    'focused': 'Minimal ambient focus playlist',
    'neutral': 'Chill background music'
}

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json() or {}
    image = data.get('image_b64')
    if not image:
        return jsonify({'error': 'no image provided'}), 400
    mood = mock_classify_image(image)
    AGGREGATED[mood] = AGGREGATED.get(mood, 0) + 1
    return jsonify({'mood': mood})

@app.route('/current_mood', methods=['GET'])
def current_mood():
    # For the Flutter stub: return a single mood (mocked)
    mood = choice(['happy', 'stressed', 'focused', 'neutral'])
    AGGREGATED[mood] = AGGREGATED.get(mood, 0) + 1
    return jsonify({'mood': mood})

@app.route('/playlist', methods=['GET'])
def playlist():
    mood = request.args.get('mood', 'neutral')
    query = MOOD_TO_YT.get(mood, MOOD_TO_YT['neutral'])
    # In production, call YouTube Data API here and return playlist/track IDs.
    return jsonify({'mood': mood, 'youtube_query': query})

@app.route('/campus_aggregate', methods=['GET'])
def campus_aggregate():
    return jsonify({'aggregate': AGGREGATED})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
