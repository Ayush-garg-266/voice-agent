"""
Gemini Signal Extraction Engine for Q4 Real-Time Call Monitoring.
Extracts structured conversation signals (compliance gap, missed cross-sell, frustration, etc.)
from sliding window transcript context using Gemini API.
"""

import time
import json
from typing import Dict, Any, Optional, List
from shared.llm.gemini_client import get_gemini_client
from shared.logging import logger

VALID_SIGNALS = [
    "missed_cross_sell",
    "compliance_gap",
    "risky_statement",
    "rising_frustration",
    "payment_difficulty",
    "callback_required",
    "customer_buying_signal",
    "unclear_audio"
]

SIGNAL_EXTRACTION_SYSTEM_PROMPT = """You are a Real-Time Conversation Signal Analyzer for a financial voice call center.
Your task is to analyze recent speaker-separated transcript context and extract high-confidence operational signals.

Respond ONLY with valid JSON conforming strictly to this JSON schema:
{
  "detected": true/false,
  "signal_type": "missed_cross_sell" | "compliance_gap" | "risky_statement" | "rising_frustration" | "payment_difficulty" | "callback_required" | "customer_buying_signal" | "unclear_audio",
  "confidence": 0.0 to 1.0,
  "evidence": "Short exact quote or clear statement from transcript",
  "urgency": "low" | "medium" | "high" | "critical",
  "recommended_action": "Concise advice for the agent",
  "expires_after_seconds": 15 to 60
}

RULES:
1. If no clear signal is present or transcript is normal, return {"detected": false}.
2. Do NOT expose internal reasoning or chain-of-thought.
3. Be strict with confidence scoring: return >= 0.85 only when strong empirical evidence exists.
4. If audio transcript is ambiguous, garbled, or noisy, return signal_type 'unclear_audio' with lower confidence.
"""

class GeminiSignalExtractor:
    """
    Real-Time Signal Extractor powered by Gemini API.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.llm = get_gemini_client(default_model=model_name)

    def extract_signals(self, transcript_frame: Dict[str, Any], sliding_context: str) -> Dict[str, Any]:
        """
        Analyzes the latest transcript frame & sliding window to extract structured signals.
        Calculates signal extraction latency accurately.
        """
        start_ts = time.time()

        prompt = (
            f"Sliding Transcript Context:\n{sliding_context}\n\n"
            f"Latest Turn:\n{transcript_frame['speaker']}: \"{transcript_frame['text']}\"\n\n"
            f"Analyze for real-time operational signals and return structured JSON."
        )

        try:
            raw_response = self.llm.generate(
                prompt=prompt,
                system_instruction=SIGNAL_EXTRACTION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=250
            )
            signal_ts = time.time()
            signal_latency_ms = (signal_ts - transcript_frame["transcription_timestamp"]) * 1000.0

            data = json.loads(raw_response) if raw_response else {"detected": False}
            data["signal_ts"] = signal_ts
            data["signal_latency_ms"] = round(signal_latency_ms, 2)
            data["frame_id"] = transcript_frame.get("chunk_id", "chk_0000")
            return data

        except Exception as e:
            logger.error(f"Gemini Signal Extraction error: {e}")
            signal_ts = time.time()
            signal_latency_ms = (signal_ts - transcript_frame["transcription_timestamp"]) * 1000.0
            return {
                "detected": False,
                "error": str(e),
                "signal_ts": signal_ts,
                "signal_latency_ms": round(signal_latency_ms, 2),
                "frame_id": transcript_frame.get("chunk_id", "chk_0000")
            }
