"""
Indonesia Multifinance Conversation Flow Engine.
Tracks turn state, regional accent handling, and executes Gemini LLM responses in Bahasa Indonesia.
"""

from typing import Dict, Any, List, Optional
from shared.llm.gemini_client import get_gemini_client
from q3_multilingual.indonesia.system_prompt import get_indonesia_system_prompt
from q3_multilingual.indonesia.kb_data import ID_MULTIFINANCE_KB
from q3_multilingual.indonesia.formatters import (
    format_currency_id,
    format_date_id,
    format_payment_explanation_id,
    apply_politeness_id
)
from shared.logging import logger


class IndonesiaMultifinanceBot:
    """
    Localized Indonesia Voice Bot for Multifinance / Consumer Finance.
    """

    def __init__(self, model_name: Optional[str] = None, user_gender_honorific: str = "Bapak/Ibu"):
        self.llm = get_gemini_client(default_model=model_name)
        self.system_prompt = get_indonesia_system_prompt()
        self.conversation_history: List[Dict[str, str]] = []
        self.honorific = user_gender_honorific
        self.state = {
            "stage": "GREETING",
            "contract_num": "CTR-ID-774019",
            "angsuran_amount": 450000.0,
            "jatuh_tempo": "2026-10-15",
            "tenor_months": 24,
            "escalated": False
        }

    def process_turn(self, user_input: str) -> Dict[str, Any]:
        """
        Processes a turn of conversation in Bahasa Indonesia (with dialect tolerance).
        Returns bot response text, current stage, escalation flag, and metadata.
        """
        logger.info(f"[ID Bot] User Input: {user_input}")

        # Check for immediate escalation request
        user_lower = user_input.lower()
        escalation_keywords = [
            "bicara cs", "manajer", "orang asli", "petugas", "human", "supervisor",
            "bicara sama cs", "hubungkan cs", "customer service"
        ]
        if any(kw in user_lower for kw in escalation_keywords):
            self.state["escalated"] = True
            escalation_msg = (
                f"Baik {self.honorific}, saya bantu hubungkan langsung dengan Customer Service Officer (CSO) "
                f"kami di kantor cabang terdekat untuk penanganan lebih lanjut. Mohon tunggu sebentar ya Pak/Bu."
            )
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": escalation_msg})
            return {
                "response": escalation_msg,
                "stage": "ESCALATED",
                "escalated": True,
                "language": "Bahasa Indonesia (ID)"
            }

        # Format conversation context for Gemini
        history_str = ""
        for turn in self.conversation_history[-6:]:
            speaker = "User" if turn["role"] == "user" else "Budi (Bot)"
            history_str += f"{speaker}: {turn['content']}\n"

        prompt = (
            f"Conversation History:\n{history_str}\n"
            f"User just said: \"{user_input}\"\n\n"
            f"Respond concisely (1-3 sentences maximum) as Budi in polite Bahasa Indonesia using '{self.honorific}' honorific."
        )

        try:
            bot_text = self.llm.generate(
                prompt=prompt,
                system_instruction=self.system_prompt,
                temperature=0.6,
                max_output_tokens=200
            )
            bot_text = apply_politeness_id(bot_text, gender_honorific=self.honorific)
        except Exception as e:
            logger.error(f"ID Bot LLM error: {e}")
            bot_text = (
                f"Mohon maaf {self.honorific}, suara kurang terdengar jelas. "
                f"Bisa tolong diulangi kembali Pak/Bu?"
            )

        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "assistant", "content": bot_text})

        return {
            "response": bot_text,
            "stage": self.state["stage"],
            "escalated": self.state["escalated"],
            "language": "Bahasa Indonesia (ID)"
        }
