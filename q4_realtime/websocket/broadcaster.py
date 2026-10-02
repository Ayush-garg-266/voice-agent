"""
Real-Time Broadcaster Engine for Q4 Live Call Assistance.
Orchestrates live streaming audio processing through ASR, Gemini Signal Extractor, Nudge Engine,
and broadcasts live state events to the Streamlit Dashboard.
"""

import time
from typing import Dict, Any, List, Callable, Optional
from q4_realtime.streaming.audio_streamer import AudioStreamer
from q4_realtime.asr.streaming_asr import StreamingASR
from q4_realtime.signals.gemini_signal_extractor import GeminiSignalExtractor
from q4_realtime.nudges.nudge_policy_engine import NudgePolicyEngine
from shared.logging import logger


class RealtimeCallPipeline:
    """
    End-to-end Real-Time Call Pipeline orchestrator.
    Processes live or replayed audio stream chunks and maintains active call state and metrics.
    """

    def __init__(
        self,
        asr_provider: str = "Deepgram Streaming Nova-2",
        confidence_threshold: float = 0.75,
        model_name: Optional[str] = None
    ):
        self.streamer = AudioStreamer(chunk_duration_sec=1.5)
        self.asr = StreamingASR(provider=asr_provider)
        self.signal_extractor = GeminiSignalExtractor(model_name=model_name)
        self.nudge_engine = NudgePolicyEngine(min_confidence_threshold=confidence_threshold)

        self.listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.latency_metrics: List[Dict[str, float]] = []

    def register_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Registers a subscriber/dashboard listener for live update events."""
        self.listeners.append(callback)

    def process_live_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single live chunk through the pipeline and emits WebSocket broadcast payload.
        """
        # Step 1: Streaming ASR
        frame = self.asr.process_chunk(chunk)
        sliding_transcript = self.asr.get_sliding_window_transcript(last_n_turns=6)

        # Step 2: Gemini Signal Extraction
        signal_res = self.signal_extractor.extract_signals(frame, sliding_transcript)

        # Step 3: Nudge Policy Engine
        policy_res = self.nudge_engine.process_signal(signal_res, frame)

        # Step 4: Record Latency Metrics
        broadcast_ts = time.time()
        nudge_to_dashboard_ms = round((broadcast_ts - policy_res.get("nudge", {}).get("created_timestamp", broadcast_ts)) * 1000.0, 2)
        total_e2e_ms = round((broadcast_ts - chunk["audio_received_timestamp"]) * 1000.0, 2)

        latency_record = {
            "chunk_id": chunk["chunk_id"],
            "asr_ms": frame["asr_latency_ms"],
            "signal_ms": signal_res.get("signal_latency_ms", 0.0),
            "policy_ms": policy_res.get("nudge", {}).get("policy_latency_ms", 0.0),
            "dashboard_ms": nudge_to_dashboard_ms,
            "total_e2e_ms": total_e2e_ms
        }
        self.latency_metrics.append(latency_record)

        # Build Broadcast Payload
        broadcast_payload = {
            "timestamp": broadcast_ts,
            "frame": frame,
            "signal": signal_res,
            "policy_result": policy_res,
            "latency": latency_record,
            "active_nudges": list(self.nudge_engine.active_nudges),
            "suppressed_nudges": list(self.nudge_engine.suppressed_nudges),
            "full_transcript": list(self.asr.full_transcript_history)
        }

        # Notify active listeners / WebSockets
        for listener in self.listeners:
            try:
                listener(broadcast_payload)
            except Exception as e:
                logger.error(f"Broadcaster listener error: {e}")

        return broadcast_payload

    def run_simulation(self, script_turns: List[Dict[str, str]], delay_sec: float = 1.0) -> List[Dict[str, Any]]:
        """
        Runs an end-to-end simulation of a call script turn by turn.
        """
        events = []
        for chunk in self.streamer.stream_call(script_turns, simulate_realtime_delay=False):
            payload = self.process_live_chunk(chunk)
            events.append(payload)
            if delay_sec > 0:
                time.sleep(delay_sec)
        return events
