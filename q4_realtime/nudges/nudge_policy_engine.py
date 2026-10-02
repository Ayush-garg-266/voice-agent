"""
Deterministic Nudge Policy Engine for Q4 Real-Time Agent Assistance.
Implements duplicate suppression, cooldown windows, confidence thresholds, priority ranking,
topic grouping, and suppressed nudge auditing.
"""

import time
from typing import Dict, Any, List, Optional
from shared.logging import logger

class NudgePolicyEngine:
    """
    Evaluates raw LLM signals against strict deterministic policies before delivering live agent nudges.
    """

    def __init__(
        self,
        min_confidence_threshold: float = 0.75,
        cooldown_seconds: float = 30.0,
        max_rep_limit_per_topic: int = 2
    ):
        self.min_confidence_threshold = min_confidence_threshold
        self.cooldown_seconds = cooldown_seconds
        self.max_rep_limit_per_topic = max_rep_limit_per_topic

        self.active_nudges: List[Dict[str, Any]] = []
        self.suppressed_nudges: List[Dict[str, Any]] = []
        self.topic_history: Dict[str, List[float]] = {}  # topic -> list of timestamps

    def process_signal(self, signal_payload: Dict[str, Any], frame_meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates signal against policy rules.
        Returns result dict containing decision ('EMITTED' vs 'SUPPRESSED') and details.
        """
        eval_start_ts = time.time()

        if not signal_payload.get("detected", False):
            return {"status": "NO_SIGNAL", "reason": "No signal detected by Gemini"}

        signal_type = signal_payload.get("signal_type", "unknown")
        confidence = float(signal_payload.get("confidence", 0.0))
        urgency = signal_payload.get("urgency", "low").lower()
        evidence = signal_payload.get("evidence", "")
        action = signal_payload.get("recommended_action", "")
        expires_in = int(signal_payload.get("expires_after_seconds", 30))

        # Rule 1: Confidence Threshold Check
        if confidence < self.min_confidence_threshold:
            suppressed_record = {
                "signal_type": signal_type,
                "confidence": confidence,
                "reason": f"Below confidence threshold ({confidence:.2f} < {self.min_confidence_threshold:.2f})",
                "timestamp": eval_start_ts
            }
            self.suppressed_nudges.append(suppressed_record)
            return {"status": "SUPPRESSED", "details": suppressed_record}

        # Rule 2: Ambiguous / Unclear Audio Suppression
        if signal_type == "unclear_audio":
            suppressed_record = {
                "signal_type": signal_type,
                "confidence": confidence,
                "reason": "Audio marked ambiguous/unclear; high-confidence nudge suppressed",
                "timestamp": eval_start_ts
            }
            self.suppressed_nudges.append(suppressed_record)
            return {"status": "SUPPRESSED", "details": suppressed_record}

        # Rule 3: Cooldown & Repetition Limit Check
        timestamps = self.topic_history.get(signal_type, [])
        now = eval_start_ts

        # Check cooldown
        if timestamps and (now - timestamps[-1]) < self.cooldown_seconds:
            elapsed = round(now - timestamps[-1], 1)
            suppressed_record = {
                "signal_type": signal_type,
                "confidence": confidence,
                "reason": f"Cooldown active ({elapsed}s < {self.cooldown_seconds}s limit)",
                "timestamp": eval_start_ts
            }
            self.suppressed_nudges.append(suppressed_record)
            return {"status": "SUPPRESSED", "details": suppressed_record}

        # Check repetition limit
        if len(timestamps) >= self.max_rep_limit_per_topic:
            suppressed_record = {
                "signal_type": signal_type,
                "confidence": confidence,
                "reason": f"Topic repetition limit reached ({len(timestamps)} >= {self.max_rep_limit_per_topic})",
                "timestamp": eval_start_ts
            }
            self.suppressed_nudges.append(suppressed_record)
            return {"status": "SUPPRESSED", "details": suppressed_record}

        # Determine Nudge Text based on Policy Rules
        nudge_text = self._format_policy_nudge_text(signal_type, urgency, action)

        eval_end_ts = time.time()
        policy_latency_ms = (eval_end_ts - signal_payload.get("signal_ts", eval_start_ts)) * 1000.0

        nudge = {
            "nudge_id": f"ndg_{len(self.active_nudges)+1:04d}",
            "signal_type": signal_type,
            "confidence": confidence,
            "urgency": urgency,
            "evidence": evidence,
            "nudge_text": nudge_text,
            "created_timestamp": eval_start_ts,
            "expires_timestamp": eval_start_ts + expires_in,
            "policy_latency_ms": round(policy_latency_ms, 2),
            "total_audio_to_nudge_ms": round((eval_end_ts - frame_meta.get("audio_received_timestamp", eval_start_ts)) * 1000.0, 2)
        }

        self.active_nudges.append(nudge)
        if signal_type not in self.topic_history:
            self.topic_history[signal_type] = []
        self.topic_history[signal_type].append(eval_start_ts)

        logger.info(f"[Nudge Policy Engine] EMITTED NUDGE: [{urgency.upper()}] {signal_type} -> {nudge_text}")
        return {"status": "EMITTED", "nudge": nudge}

    def _format_policy_nudge_text(self, signal_type: str, urgency: str, custom_action: str) -> str:
        """Formats canonical deterministic nudge wording as required by specifications."""
        if signal_type == "rising_frustration":
            return "Customer frustration is increasing. Slow down and acknowledge the concern."
        elif signal_type == "missed_cross_sell":
            return "Potential cross-sell opportunity detected. Ask about relevant additional coverage or options."
        elif signal_type == "compliance_gap":
            return "Required disclosure may have been missed. Verify disclosure before continuing."
        elif custom_action:
            return custom_action
        else:
            return f"Action required: Address {signal_type.replace('_', ' ')}."
