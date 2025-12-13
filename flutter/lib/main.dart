import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(MoodTunesApp());

class MoodTunesApp extends StatefulWidget {
  @override
  _MoodTunesAppState createState() => _MoodTunesAppState();
}

class _MoodTunesAppState extends State<MoodTunesApp> {
  String _mood = 'neutral';
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    // Start polling backend every 5 seconds (simulates Gemini Vision analysis)
    _timer = Timer.periodic(Duration(seconds: 5), (_) => _fetchMood());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _fetchMood() async {
    try {
      // Replace with your backend analyze endpoint
      final res = await http.get(Uri.parse('http://localhost:8080/current_mood'));
      if (res.statusCode == 200) {
        final j = json.decode(res.body);
        setState(() => _mood = j['mood'] ?? 'neutral');
        // In a real app, update audio playback here (YouTube/Spotify SDK)
      }
    } catch (e) {
      // ignore network errors in prototype
    }
  }

  Color _bgForMood(String m) {
    switch (m) {
      case 'happy':
        return Colors.yellow.shade200;
      case 'stressed':
        return Colors.red.shade200;
      case 'focused':
        return Colors.blue.shade200;
      default:
        return Colors.grey.shade200;
    }
  }

  @override
  Widget build(BuildContext c) {
    return MaterialApp(
      home: Scaffold(
        backgroundColor: _bgForMood(_mood),
        appBar: AppBar(title: Text('AI Mood Tunes — Prototype')),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Detected mood:', style: TextStyle(fontSize: 20)),
              SizedBox(height: 12),
              Text(_mood.toUpperCase(), style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold)),
              SizedBox(height: 24),
              ElevatedButton(
                onPressed: _fetchMood,
                child: Text('Poll now'),
              ),
              SizedBox(height: 12),
              Text('This stub polls a backend every 5s.', style: TextStyle(fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }
}
