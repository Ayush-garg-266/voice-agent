"""
Automated Pytest Suite for Q4 Real-Time Agent Assistance & Supervisor Nudge Engine.
Tests the 4 mandatory call scenarios, confidence thresholds, duplicate suppression,
cooldown rules, latency statistics calculation, and false positive controls.
"""

import pytest
import time
from q4_realtime.streaming.audio_streamer import AudioStreamer
from q4_realtime.asr.streaming_asr import StreamingASR
from q4_realtime.signals.gemini_signal_extractor import GeminiSignalExtractor, VALID_SIGNALS
from q4_realtime.nudges.nudge_policy_engine import NudgePolicyEngine
from q4_realtime.websocket.broadcaster import RealtimeCallPipeline
from q4_realtime.evaluation.latency_benchmark import compute_pipeline_latency_stats, calculate_percentile


def test_audio_streamer_and_asr():
    """Verify audio streamer and streaming ASR process chunks with timestamps."""
    streamer = AudioStreamer(chunk_duration_sec=0.1)
    asr = StreamingASR()

    script = [
        {"speaker": "Agent", "text": "Hello, how can I help?"},
        {"speaker": "Customer", "text": "I need a loan."}
    ]

    frames = []
    for chunk in streamer.stream_call(script, simulate_realtime_delay=False):
        frame = asr.process_chunk(chunk)
        frames.append(frame)

    assert len(frames) == 2
    assert frames[0]["speaker"] == "Agent"
    assert frames[1]["speaker"] == "Customer"
    assert frames[0]["asr_latency_ms"] > 0
    assert len(asr.full_transcript_history) == 2


def test_nudge_policy_engine_duplicate_suppression_and_cooldown():
    """Verify nudge policy engine suppresses duplicates and enforces cooldown."""
    engine = NudgePolicyEngine(min_confidence_threshold=0.75, cooldown_seconds=10.0)

    signal_high_conf = {
        "detected": True,
        "signal_type": "rising_frustration",
        "confidence": 0.90,
        "evidence": "Customer said stop wasting my time",
        "urgency": "high",
        "recommended_action": "Acknowledge frustration",
        "expires_after_seconds": 30,
        "signal_ts": time.time()
    }

    frame_meta = {"audio_received_timestamp": time.time() - 0.2}

    # Turn 1: Should emit nudge
    res1 = engine.process_signal(signal_high_conf, frame_meta)
    assert res1["status"] == "EMITTED"
    assert len(engine.active_nudges) == 1
    assert "frustration is increasing" in res1["nudge"]["nudge_text"]

    # Turn 2: Immediate duplicate signal should be SUPPRESSED due to cooldown
    res2 = engine.process_signal(signal_high_conf, frame_meta)
    assert res2["status"] == "SUPPRESSED"
    assert "Cooldown active" in res2["details"]["reason"]
    assert len(engine.suppressed_nudges) == 1


def test_nudge_policy_engine_confidence_threshold():
    """Verify low confidence signals are suppressed."""
    engine = NudgePolicyEngine(min_confidence_threshold=0.80)

    signal_low_conf = {
        "detected": True,
        "signal_type": "missed_cross_sell",
        "confidence": 0.60,
        "evidence": "Vague hint",
        "signal_ts": time.time()
    }
    frame_meta = {"audio_received_timestamp": time.time()}

    res = engine.process_signal(signal_low_conf, frame_meta)
    assert res["status"] == "SUPPRESSED"
    assert "Below confidence threshold" in res["details"]["reason"]


def test_latency_stats_calculation():
    """Verify P50 and P95 latency calculation logic."""
    records = [
        {"asr_ms": 100.0, "signal_ms": 300.0, "policy_ms": 5.0, "dashboard_ms": 10.0, "total_e2e_ms": 415.0},
        {"asr_ms": 120.0, "signal_ms": 350.0, "policy_ms": 6.0, "dashboard_ms": 12.0, "total_e2e_ms": 488.0},
        {"asr_ms": 90.0, "signal_ms": 280.0, "policy_ms": 4.0, "dashboard_ms": 8.0, "total_e2e_ms": 382.0}
    ]

    stats = compute_pipeline_latency_stats(records)
    assert stats["sample_size"] == 3
    assert stats["p50"]["asr_ms"] > 0
    assert stats["p95"]["total_audio_to_nudge_ms"] >= stats["p50"]["total_audio_to_nudge_ms"]


@pytest.mark.integration
def test_scenario_missed_cross_sell():
    """Integration Test 1: Missed Cross-Sell Scenario."""
    pipeline = RealtimeCallPipeline(confidence_threshold=0.70)
    script = [
        {"speaker": "Customer", "text": "I want an equipment loan for my new branch, and I also need protection for the warehouse."},
        {"speaker": "Agent", "text": "Okay, let's just do the equipment loan."}
    ]

    events = pipeline.run_simulation(script, delay_sec=0)
    assert len(events) == 2
    # Verify pipeline executed without error
    assert pipeline.latency_metrics is not None


@pytest.mark.integration
def test_scenario_compliance_risk():
    """Integration Test 2: Compliance Disclosure Risk Scenario."""
    pipeline = RealtimeCallPipeline(confidence_threshold=0.70)
    script = [
        {"speaker": "Customer", "text": "What are the exact fees and interest rate schedule?"},
        {"speaker": "Agent", "text": "Don't worry about reading the rate disclosure schedule."}
    ]

    events = pipeline.run_simulation(script, delay_sec=0)
    assert len(events) == 2


@pytest.mark.integration
def test_scenario_rising_frustration():
    """Integration Test 3: Rising Frustration Scenario."""
    pipeline = RealtimeCallPipeline(confidence_threshold=0.70)
    script = [
        {"speaker": "Customer", "text": "This is the third time I am transferred! Connect me to your manager right now!"}
    ]

    events = pipeline.run_simulation(script, delay_sec=0)
    assert len(events) == 1


@pytest.mark.integration
def test_scenario_noisy_audio_false_positive():
    """Integration Test 4: Noisy / Ambiguous Audio False Positive Control."""
    pipeline = RealtimeCallPipeline(confidence_threshold=0.80)
    script = [
        {"speaker": "Customer", "text": "[static noise] ...uh... rate... maybe... [garbled audio]"}
    ]

    events = pipeline.run_simulation(script, delay_sec=0)
    # High confidence nudges should be suppressed
    assert len(pipeline.nudge_engine.active_nudges) == 0
