"""
Philippines Bancassurance Conversation Flow Engine.
Tracks turn state, qualification data, and executes Gemini LLM responses in Taglish.
"""

from typing import Dict, Any, List, Optional
from shared.llm.gemini_client import get_gemini_client
from q3_multilingual.philippines.system_prompt import get_philippines_system_prompt
from q3_multilingual.philippines.kb_data import PH_BANCASSURANCE_KB
from q3_multilingual.philippines.formatters import (
    format_currency_ph,
    format_date_ph,
    format_payment_explanation_ph,
    apply_politeness_ph
)
from shared.logging import logger


class PhilippinesBancassuranceBot:
    """
    Localized Philippines Voice Bot for Life Insurance & Bancassurance.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.llm = get_gemini_client(default_model=model_name)
        self.system_prompt = get_philippines_system_prompt()
        self.conversation_history: List[Dict[str, str]] = []
        self.state = {
            "stage": "GREETING",
            "policy_num": "POL-PH-889412",
            "premium_amount": 2500.0,
            "due_date": "2026-10-15",
            "qualification": {
                "has_existing_coverage": None,
                "preferred_budget": None,
                "interested_in_rider": None,
                "bank_referral_agreed": None
            },
            "escalated": False
        }

    def process_turn(self, user_input: str) -> Dict[str, Any]:
        """
        Processes a turn of conversation in Taglish.
        Returns bot response text, current stage, escalation flag, and metadata.
        """
        logger.info(f"[PH Bot] User Input: {user_input}")

        # Check for immediate escalation request
        user_lower = user_input.lower()
        if any(kw in user_lower for kw in ["kausap", "manager", "human", "tao", "agent", "supervisor", "transfer"]):
            self.state["escalated"] = True
            escalation_msg = (
                "Naiintindihan ko po. I-transfer ko po ang inyong tawag sa aming Senior Bancassurance Specialist "
                "sa pinakamalapit na partner bank branch para mas maasikaso po kayo. Sandali lamang po."
            )
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": escalation_msg})
            return {
                "response": escalation_msg,
                "stage": "ESCALATED",
                "escalated": True,
                "language": "Taglish (PH)"
            }

        # Format conversation context for Gemini
        history_str = ""
        for turn in self.conversation_history[-6:]:
            speaker = "User" if turn["role"] == "user" else "Maria (Bot)"
            history_str += f"{speaker}: {turn['content']}\n"

        prompt = (
            f"Conversation History:\n{history_str}\n"
            f"User just said: \"{user_input}\"\n\n"
            f"Respond concisely (1-3 sentences maximum) as Maria in natural Taglish with respectful 'po/opo' register."
        )

        try:
            bot_text = self.llm.generate(
                prompt=prompt,
                system_instruction=self.system_prompt,
                temperature=0.6,
                max_output_tokens=200
            )
            bot_text = apply_politeness_ph(bot_text)
        except Exception as e:
            logger.error(f"PH Bot LLM error: {e}")
            bot_text = (
                "Pasensya na po, medyo naputol po ang linya o hindi ko po masyadong naintindihan. "
                "Pwede niyo po bang ulitin?"
            )

        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": bot_text})

        return {
            "response": bot_text,
            "stage": self.state["stage"],
            "escalated": self.state["escalated"],
            "language": "Taglish (PH)"
        }
