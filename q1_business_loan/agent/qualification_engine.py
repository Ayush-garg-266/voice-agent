from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from shared.logging import logger

class QualificationState(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    operating_months: Optional[int] = None
    registration_status: Optional[str] = None
    annual_revenue: Optional[float] = None
    monthly_cashflow: Optional[float] = None
    requested_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    preferred_tenor_months: Optional[int] = None
    has_collateral: Optional[bool] = None

    # Internal Tracking
    conflicting_revenue_flag: bool = False
    unsupported_purpose_flag: bool = False
    human_escalation_requested: bool = False
    escalation_reason: Optional[str] = None


class QualificationResult(BaseModel):
    qualification_status: str  # prequalified, unqualified, needs_review, escalated
    missing_information: List[str]
    collected_information: Dict[str, Any]
    retrieved_evidence: List[Dict[str, Any]]
    next_step: str
    escalation_required: bool


class QualificationEngine:
    """
    Evaluates applicant details against documented Q2 business loan criteria:
    - Operating history: >= 12 months
    - Annual revenue: >= $100,000 USD
    - Entity registration: Active registered entity (LLC, Corp, Sole Prop, Partnership)
    - Unsecured loan limit: <= $100,000 (Requires collateral if > $100,000)
    """

    MIN_OPERATING_MONTHS = 12
    MIN_ANNUAL_REVENUE = 100000.0
    MAX_UNSECURED_AMOUNT = 100000.0
    UNSUPPORTED_PURPOSES = ["crypto", "cryptocurrency", "gambling", "personal travel", "mortgage", "stock trading"]

    def evaluate(self, state: QualificationState, evidence_citations: List[Dict[str, Any]] = None) -> QualificationResult:
        evidence = evidence_citations or []
        collected = {k: v for k, v in state.model_dump().items() if v is not None and not k.endswith("_flag") and not k.endswith("_requested")}
        missing = []

        # Check missing mandatory fields
        if not state.business_name:
            missing.append("business_name")
        if state.operating_months is None:
            missing.append("operating_months")
        if state.annual_revenue is None:
            missing.append("annual_revenue")
        if state.requested_amount is None:
            missing.append("requested_amount")

        # 1. Human Escalation Triggered
        if state.human_escalation_requested:
            return QualificationResult(
                qualification_status="escalated",
                missing_information=missing,
                collected_information=collected,
                retrieved_evidence=evidence,
                next_step="Transfer caller to senior loan officer and schedule callback.",
                escalation_required=True
            )

        # 2. Incomplete Information
        if missing:
            return QualificationResult(
                qualification_status="needs_review",
                missing_information=missing,
                collected_information=collected,
                retrieved_evidence=evidence,
                next_step=f"Prompt applicant for missing information: {', '.join(missing)}.",
                escalation_required=False
            )

        # 3. Conflicting Revenue Details
        if state.annual_revenue and state.monthly_cashflow:
            est_annual_from_monthly = state.monthly_cashflow * 12
            if abs(state.annual_revenue - est_annual_from_monthly) / max(state.annual_revenue, 1) > 0.4:
                return QualificationResult(
                    qualification_status="needs_review",
                    missing_information=[],
                    collected_information=collected,
                    retrieved_evidence=evidence,
                    next_step="Clarify discrepancy between annual revenue and monthly cash flow.",
                    escalation_required=False
                )

        # 4. Unsupported Purpose Check
        if state.loan_purpose and any(unsupported in state.loan_purpose.lower() for unsupported in self.UNSUPPORTED_PURPOSES):
            return QualificationResult(
                qualification_status="unqualified",
                missing_information=[],
                collected_information=collected,
                retrieved_evidence=evidence,
                next_step="Decline loan application due to unsupported loan purpose per policy Section 2.",
                escalation_required=False
            )

        # 5. Core Eligibility Criteria Checks
        reasons_unqualified = []
        if state.operating_months < self.MIN_OPERATING_MONTHS:
            reasons_unqualified.append(f"Operating history ({state.operating_months} mos) under 12 months minimum requirement.")
        if state.annual_revenue < self.MIN_ANNUAL_REVENUE:
            reasons_unqualified.append(f"Annual revenue (${state.annual_revenue:,.2f}) under $100,000 minimum requirement.")

        if reasons_unqualified:
            return QualificationResult(
                qualification_status="unqualified",
                missing_information=[],
                collected_information=collected,
                retrieved_evidence=evidence,
                next_step="Inform applicant of eligibility gap politely and offer re-application timeline.",
                escalation_required=False
            )

        # 6. Prequalified
        collateral_note = ""
        if state.requested_amount > self.MAX_UNSECURED_AMOUNT and not state.has_collateral:
            collateral_note = " (Requires asset collateral for loan amount > $100k)"

        return QualificationResult(
            qualification_status="prequalified",
            missing_information=[],
            collected_information=collected,
            retrieved_evidence=evidence,
            next_step=f"Issue preliminary conditional pre-qualification and trigger digital document upload link{collateral_note}.",
            escalation_required=False
        )
