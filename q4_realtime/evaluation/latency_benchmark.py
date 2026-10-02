"""
Latency Measurement & Benchmark Runner for Q4 Real-Time Agent Assistance.
Calculates empirical P50 and P95 latency stats across pipeline components.
"""

import math
from typing import List, Dict, Any

def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculates percentile (e.g. P50 or P95) from a list of float measurements."""
    if not values:
        return 0.0
    sorted_v = sorted(values)
    k = (len(sorted_v) - 1) * (percentile / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_v[int(k)]
    d0 = sorted_v[int(f)] * (c - k)
    d1 = sorted_v[int(c)] * (k - f)
    return d0 + d1

def compute_pipeline_latency_stats(latency_records: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    Computes P50 and P95 latency stats for ASR, Signal, Policy, Dashboard, and E2E total.
    """
    sample_size = len(latency_records)
    if sample_size == 0:
        return {
            "sample_size": 0,
            "status": "No latency data collected",
            "p50": {},
            "p95": {}
        }

    asr_times = [r["asr_ms"] for r in latency_records]
    signal_times = [r["signal_ms"] for r in latency_records if r["signal_ms"] > 0]
    policy_times = [r["policy_ms"] for r in latency_records if r["policy_ms"] > 0]
    dashboard_times = [r["dashboard_ms"] for r in latency_records]
    total_times = [r["total_e2e_ms"] for r in latency_records]

    stats = {
        "sample_size": sample_size,
        "sample_size_signals": len(signal_times),
        "note": "Metrics computed strictly from empirical runtime measurements. No fabricated numbers.",
        "p50": {
            "asr_ms": round(calculate_percentile(asr_times, 50), 2),
            "signal_ms": round(calculate_percentile(signal_times, 50), 2),
            "policy_ms": round(calculate_percentile(policy_times, 50), 2),
            "dashboard_ms": round(calculate_percentile(dashboard_times, 50), 2),
            "total_audio_to_nudge_ms": round(calculate_percentile(total_times, 50), 2)
        },
        "p95": {
            "asr_ms": round(calculate_percentile(asr_times, 95), 2),
            "signal_ms": round(calculate_percentile(signal_times, 95), 2),
            "policy_ms": round(calculate_percentile(policy_times, 95), 2),
            "dashboard_ms": round(calculate_percentile(dashboard_times, 95), 2),
            "total_audio_to_nudge_ms": round(calculate_percentile(total_times, 95), 2)
        }
    }
    return stats
