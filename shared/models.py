from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class KnowledgeRecord(BaseModel):
    record_id: str
    title: str
    content: str
    category: str
    source_document: str
    section: Optional[str] = None
    version: str = "1.0"
    contains_pii: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RetrievalCitation(BaseModel):
    record_id: str
    source_document: str
    section: Optional[str] = None
    content_snippet: str
    relevance_score: float

class RetrievalResponse(BaseModel):
    query: str
    citations: List[RetrievalCitation]
    grounded_answer: Optional[str] = None
    info_available: bool = True

class LeadQualificationRequest(BaseModel):
    business_name: str
    operating_months: int
    annual_revenue: float
    monthly_cashflow: float
    requested_amount: float
    business_type: str

class LeadQualificationResponse(BaseModel):
    is_prequalified: bool
    status_reason: str
    recommended_loan_amount: float
    required_documents: List[str]
    escalation_needed: bool = False

class RealtimeSignal(BaseModel):
    signal_id: str
    signal_type: str # COMPLIANCE, RISING_FRUSTRATION, MISSED_CROSS_SELL, PAYMENT_DIFFICULTY
    speaker: str # AGENT or CUSTOMER
    transcript_snippet: str
    timestamp_ms: float
    confidence: float
    nudge_text: str
    priority: int # 0=Critical, 1=High, 2=Medium
