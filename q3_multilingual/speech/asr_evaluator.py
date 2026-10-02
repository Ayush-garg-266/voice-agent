"""
ASR (Speech-to-Text) Capability Evaluator for Q3 SE Asian Multilingual Voice Bots.
Documents provider, model, supported languages, code-switching behavior, known errors, and accent limitations.
"""

from typing import Dict, Any

class ASREvaluator:
    """
    Evaluates Speech Recognition (ASR) capabilities for Philippines and Indonesia.
    """

    @staticmethod
    def get_asr_documentation() -> Dict[str, Any]:
        return {
            "philippines": {
                "recommended_provider": "Deepgram / Google Cloud Speech-to-Text v2",
                "model": "Deepgram Nova-2 / Chirp v2",
                "language_codes": ["tl-PH", "en-PH"],
                "code_switching_behavior": "Deepgram Nova-2 handles mid-sentence Taglish code-switching smoothly when configured with multi-language hint (en-PH + tl-PH).",
                "known_errors": [
                    "Homophone confusion (e.g. 'po' recognized as 'four' or 'for' in pure English model mode).",
                    "Amount formatting drops (e.g. 'dalawang libo limang daan' transcribed as words instead of '2500').",
                    "Code-switch boundary drops when speaker switches back and forth within 2 seconds."
                ],
                "accent_limitations": "Handles Metro Manila Taglish well; struggles with heavy Visayan / Ilocano regional accents."
            },
            "indonesia": {
                "recommended_provider": "Deepgram Nova-2 / Google Cloud Speech-to-Text v2",
                "model": "Deepgram Nova-2 / Chirp v2",
                "language_codes": ["id-ID"],
                "code_switching_behavior": "Handles Bahasa Indonesia with common finance English loanwords (DP, Tenor, Virtual Account, Credit Card) accurately.",
                "known_errors": [
                    "Number transcription variance (e.g. 'empat ratus lima puluh ribu' vs '450.000').",
                    "Abbreviation confusion ('VA' recognized as 'Pia' or 'V-A').",
                    "Javanese accent phoneme shifts (e.g. voiced 'd' phoneme in 'denda' shifting acoustic probability)."
                ],
                "accent_limitations": "Handles standard Jakarta Bahasa Indonesia smoothly. 'Medok' Javanese accent or Sundanese syntax requires post-ASR LLM normalization."
            }
        }
