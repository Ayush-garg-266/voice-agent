# Q4 — Real-Time Live Call Insights & Agent Nudges

This module implements real-time call monitoring, Gemini signal extraction, policy-governed duplicate suppression, and live agent/supervisor nudge delivery.

## Module Structure
- `streaming/`: [q4_realtime/streaming/audio_streamer.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/streaming/audio_streamer.py) - Real-time chunked audio stream generator.
- `asr/`: [q4_realtime/asr/streaming_asr.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/asr/streaming_asr.py) - Streaming speech-to-text transcript processing & ASR latency tracking.
- `signals/`: [q4_realtime/signals/gemini_signal_extractor.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/signals/gemini_signal_extractor.py) - Gemini-powered structured signal extraction (compliance gap, frustration, missed cross-sell, etc.).
- `nudges/`: [q4_realtime/nudges/nudge_policy_engine.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/nudges/nudge_policy_engine.py) - Deterministic policy layer with cooldowns, confidence thresholds, duplicate suppression, and priority queues.
- `websocket/`: [q4_realtime/websocket/broadcaster.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/websocket/broadcaster.py) - End-to-end real-time call pipeline & WebSocket metrics broadcaster.
- `dashboard/`: [q4_realtime/dashboard/app.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/dashboard/app.py) - Streamlit live agent/supervisor dashboard.
- `evaluation/`: [q4_realtime/evaluation/latency_benchmark.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/evaluation/latency_benchmark.py) - P50/P95 latency benchmark calculator.
- `tests/`: [q4_realtime/tests/test_q4_realtime.py](file:///c:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q4_realtime/tests/test_q4_realtime.py) - Pytest suite for missed cross-sell, compliance risk, frustration, noisy audio, and policy suppression.

## Running the Live Dashboard
```bash
streamlit run q4_realtime/dashboard/app.py
```

## Running Automated Pytest Suite
```bash
pytest q4_realtime/tests/test_q4_realtime.py -v
```
