import os
import sys
import json
import time
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from q1_business_loan.agent.conversation_manager import Q1ConversationManager
from q1_business_loan.webhooks.vapi_webhook import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

TRANSCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evaluation", "transcripts"))
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)


def run_scenario(scenario_id: str, turns: list[str]) -> dict:
    manager = Q1ConversationManager(session_id=f"sess_{scenario_id.lower()}")
    transcript_log = []
    final_res = None

    for turn_idx, user_text in enumerate(turns, start=1):
        if turn_idx > 1:
            time.sleep(4.0)  # Pause between turns to stay within Gemini API free-tier RPM limit
        res = manager.process_turn(user_text)
        final_res = res
        transcript_log.append({
            "turn": turn_idx,
            "user_message": user_text,
            "agent_response": res["agent_response"],
            "tool_called": res["tool_called"],
            "kb_query": res.get("kb_query"),
            "retrieved_source": res.get("retrieved_source"),
            "retrieved_record_id": res.get("retrieved_record_id"),
            "turn_latency_ms": res.get("turn_latency_ms"),
            "qualification_status": res["qualification_result"]["qualification_status"],
            "escalation_required": res["qualification_result"]["escalation_required"]
        })

    saved_payload = {
        "scenario_id": scenario_id,
        "turns_executed": len(turns),
        "transcript": transcript_log,
        "final_qualification_result": final_res["qualification_result"] if final_res else {}
    }

    out_file = os.path.join(TRANSCRIPT_DIR, f"{scenario_id.lower()}_transcript.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(saved_payload, f, indent=2)

    return final_res


def test_scenario_1_cooperative():
    time.sleep(3.0)
    turns = [
        "My business name is Nexus Technology LLC. We've been operating for 3 years.",
        "Our annual revenue is $250,000 and monthly cashflow is around $20,000.",
        "I am looking to borrow $50,000 for purchasing inventory."
    ]
    res = run_scenario("TEST_001", turns)
    assert res["qualification_result"]["qualification_status"] == "prequalified"
    assert not res["qualification_result"]["escalation_required"]


def test_scenario_2_objection_handling():
    time.sleep(3.0)
    turns = [
        "I run Apex Global LLC, 2 years operating history, $150,000 revenue.",
        "Why is your interest rate so high for unsecured loans?"
    ]
    res = run_scenario("TEST_002", turns)
    assert res["tool_called"]
    assert len(res["agent_response"]) > 0


def test_scenario_3_conflicting_details():
    time.sleep(3.0)
    turns = [
        "My business is Vantage Retail LLC, operating for 24 months.",
        "My annual revenue is $500,000, but recent monthly cashflow is $10,000."
    ]
    res = run_scenario("TEST_003", turns)
    assert res["qualification_result"]["qualification_status"] == "needs_review"


def test_scenario_4_out_of_scope():
    time.sleep(3.0)
    turns = [
        "My business is Horizon Corp, 2 years operating history.",
        "How do I file my personal residential mortgage tax deduction in Texas?"
    ]
    res = run_scenario("TEST_004", turns)
    assert res["tool_called"] is True
    assert res["kb_query"] == "How do I file my personal residential mortgage tax deduction in Texas?"
    assert res["qualification_result"]["escalation_required"] is False
    assert res["qualification_result"]["qualification_status"] != "escalated"
    assert "don't have enough verified information" in res["agent_response"].lower()


def test_scenario_5_human_escalation():
    time.sleep(3.0)
    turns = [
        "I want to speak with a human loan officer right now."
    ]
    res = run_scenario("TEST_005", turns)
    assert res["qualification_result"]["escalation_required"]
    assert res["qualification_result"]["qualification_status"] == "escalated"


def test_regression_issue1_state_extraction():
    time.sleep(2.0)
    manager = Q1ConversationManager(session_id="sess_issue1_regress")
    msg = "My business is ABC Traders, a private limited company. We have been operating for 4 years, our annual revenue is 5000000 rupees, and I want a business loan of 1000000 rupees for working capital."
    res = manager.process_turn(msg)

    state = manager.state
    assert state.business_name == "ABC Traders"
    assert state.operating_months == 48
    assert state.annual_revenue == 5000000.0
    assert state.requested_amount == 1000000.0
    assert state.loan_purpose == "working capital"

def test_regression_issue2_document_objection_grounded():
    time.sleep(2.0)
    manager = Q1ConversationManager(session_id="sess_issue2_regress")
    msg = "Why do you need so many business documents? I don't want to provide all of them."
    res = manager.process_turn(msg)

    assert res["tool_called"] is True
    assert res["retrieved_source"] is not None
    assert res["retrieved_record_id"] is not None
    assert "don't have enough verified information" not in res["agent_response"].lower()
    assert len(manager.retrieved_citations) > 0

def test_q1_webhooks():
    client = TestClient(app)

    # Health check
    res_h = client.get("/q1/health")
    assert res_h.status_code == 200
    assert res_h.json()["status"] == "healthy"

    # REST Qualify endpoint
    res_q = client.post("/q1/qualify", json={"session_id": "sess_test_web", "user_message": "My company is Apex Corp, operating 2 years."})
    assert res_q.status_code == 200
    data = res_q.json()
    assert "agent_response" in data
    assert "qualification_result" in data
