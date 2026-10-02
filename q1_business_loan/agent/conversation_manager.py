import time
from typing import List, Dict, Any, Optional
import re
from shared.logging import logger
from shared.llm.gemini_client import get_gemini_client
from q1_business_loan.prompts.system_prompt import Q1_SYSTEM_PROMPT
from q1_business_loan.tools.kb_tool import query_knowledge_base
from q1_business_loan.agent.qualification_engine import QualificationEngine, QualificationState, QualificationResult

class Q1ConversationManager:
    """
    Manages stateful conversation turns for Q1 Business Loan Qualification Voice Agent.
    Interprets user turns, calls Q2 RAG tool when required, updates qualification state,
    measures turn execution latency, and returns grounded agent responses.
    """

    def __init__(self, session_id: str = "sess_demo"):
        self.session_id = session_id
        self.gemini_client = get_gemini_client()
        self.engine = QualificationEngine()
        self.state = QualificationState()
        self.history: List[Dict[str, str]] = []
        self.retrieved_citations: List[Dict[str, Any]] = []

    def process_turn(self, user_message: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Session [{self.session_id}] User turn: '{user_message}'")
        self.history.append({"role": "user", "content": user_message})

        # Update qualification metrics from turn text first
        self._extract_state_metrics(user_message)

        # Check for explicit human request
        user_lower = user_message.lower()
        human_keywords = [
            "human", "person", "representative", "agent please", "speak with a human",
            "speak to a human", "talk to a human", "talk to a person", "human loan officer",
            "transfer me", "supervisor", "real person"
        ]
        if any(term in user_lower for term in human_keywords):
            self.state.human_escalation_requested = True
            self.state.escalation_reason = "Customer requested human assistance."

            agent_response = (
                "I completely understand. I am transferring your request to a senior human loan officer "
                "who will follow up with you directly. Have a great day!"
            )
            self.history.append({"role": "assistant", "content": agent_response})
            eval_res = self.engine.evaluate(self.state, self.retrieved_citations)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            return {
                "agent_response": agent_response,
                "qualification_result": eval_res.model_dump(),
                "tool_called": False,
                "kb_query": None,
                "retrieved_source": None,
                "retrieved_record_id": None,
                "turn_latency_ms": elapsed_ms
            }

        # Check if query needs Q2 RAG retrieval
        tool_called = False
        rag_evidence_text = ""
        kb_query_executed = None
        retrieved_source = None
        retrieved_record_id = None

        needs_rag = any(kw in user_lower for kw in [
            "rate", "interest", "fee", "doc", "document", "collateral", "guarantee",
            "tax", "mortgage", "crypto", "gambling", "turnover", "how long", "approval",
            "high", "why", "requirement", "policy", "faq"
        ])

        if needs_rag:
            logger.info(f"Query triggers Q2 RAG retrieval tool: '{user_message}'")
            kb_query_executed = user_message
            rag_res = query_knowledge_base(query=user_message, top_k=3)
            tool_called = True

            citations = rag_res.get("citations", [])
            if citations:
                self.retrieved_citations.extend(citations)
                retrieved_source = citations[0].get("source_document")
                retrieved_record_id = citations[0].get("record_id")

            rag_evidence_text = (
                f"\n\n[VERIFIED KB EVIDENCE]:\n{rag_res.get('grounded_answer', '')}\n"
                f"Info Available: {rag_res.get('info_available', True)}"
            )

        # Build conversation context for Gemini
        history_str = "\n".join([f"{h['role'].upper()}: {h['content']}" for h in self.history[-6:]])

        prompt = (
            f"{history_str}{rag_evidence_text}\n\n"
            f"Generate a grounded, conversational, professional voice turn response (max 2-3 sentences):"
        )

        try:
            agent_response = self.gemini_client.generate(
                prompt=prompt,
                system_instruction=Q1_SYSTEM_PROMPT,
                temperature=0.3
            )
            agent_response = agent_response.strip()
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            agent_response = (
                "I apologize, I am experiencing a temporary technical connection issue. "
                "Let me connect you with a human representative."
            )

        self.history.append({"role": "assistant", "content": agent_response})
        eval_res = self.engine.evaluate(self.state, self.retrieved_citations)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "agent_response": agent_response,
            "qualification_result": eval_res.model_dump(),
            "tool_called": tool_called,
            "kb_query": kb_query_executed,
            "retrieved_source": retrieved_source,
            "retrieved_record_id": retrieved_record_id,
            "turn_latency_ms": elapsed_ms
        }

    def _extract_state_metrics(self, text: str):
        text_lower = text.lower()

        # Extract business name
        m_name = re.search(
            r'(?:my business is|business name is|company is|business is|company named|business named|run|my company is|we are)\s+([a-zA-Z0-9\s]+?)(?:\,|\.|$|a |an |we |\d)',
            text,
            re.IGNORECASE
        )
        if m_name:
            val = m_name.group(1).strip()
            if len(val) > 2 and val.lower() not in ["a", "the", "we", "my"]:
                self.state.business_name = val

        # Extract business operating history / age
        m_year = re.search(r'(\d+)\s*(?:years?|yrs?|months?|mos?)', text_lower)
        if m_year:
            num = int(m_year.group(1))
            if "year" in text_lower or "yr" in text_lower:
                self.state.operating_months = num * 12
            else:
                self.state.operating_months = num

        # Extract requested loan amount
        m_amt = re.search(
            r'(?:borrow|need|request|borrowing|looking to borrow|want a business loan of|want a loan of|loan of|want|looking for|amount of|loan amount of)\s*\$?(\d+(?:,\d{3})*)',
            text_lower
        )
        if m_amt:
            amt_val = float(m_amt.group(1).replace(",", ""))
            if amt_val >= 1000:
                self.state.requested_amount = amt_val

        # Extract annual revenue specifically when revenue / turnover / sales is mentioned
        if any(k in text_lower for k in ["revenue", "turnover", "gross", "sales"]):
            m_rev = re.search(
                r'(?:annual revenue|revenue|turnover|sales)\s*(?:is|of|around)?\s*\$?(\d+(?:,\d{3})*)|\$?(\d+(?:,\d{3})*)\s*(?:annual revenue|revenue|turnover|sales)',
                text_lower
            )
            if m_rev:
                val_str = m_rev.group(1) or m_rev.group(2)
                if val_str:
                    self.state.annual_revenue = float(val_str.replace(",", ""))

        # Extract monthly cashflow specifically when monthly / cashflow is mentioned
        if any(k in text_lower for k in ["monthly", "cashflow", "cash flow"]):
            m_cash = re.search(
                r'(?:monthly|cashflow|cash flow)\s*(?:is|around|of)?\s*\$?(\d+(?:,\d{3})*)|\$?(\d+(?:,\d{3})*)\s*(?:monthly|cashflow|cash flow)',
                text_lower
            )
            if m_cash:
                val_str = m_cash.group(1) or m_cash.group(2)
                if val_str:
                    self.state.monthly_cashflow = float(val_str.replace(",", ""))

        # Extract loan purpose
        m_purp = re.search(
            r'(?:loan for|purpose is|purpose of|funds for|used for|borrow for|for)\s+(?!(?:\d|years|months|yrs|mos|a loan|the loan|borrowing))([a-zA-Z0-9\s]+?)(?:\.|\,|$)',
            text_lower
        )
        if m_purp:
            purp_val = m_purp.group(1).strip()
            if len(purp_val) > 2:
                self.state.loan_purpose = purp_val
