import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, APIRouter
from pydantic import BaseModel

from shared.logging import logger
from q1_business_loan.tools.kb_tool import query_knowledge_base
from q1_business_loan.agent.conversation_manager import Q1ConversationManager

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/q1", tags=["Q1 Voice Agent"])

app = FastAPI(
    title="Q1 Business Loan Qualification Voice Agent API",
    description="Vapi Webhook & Qualification Service",
    version="1.0.0"
)

# Enable CORS for local simulator UI (supports file:// and localhost origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# In-memory session store for active calls
active_sessions: Dict[str, Q1ConversationManager] = {}

@router.get("/simulator", response_class=HTMLResponse)
def get_simulator():
    sim_path = os.path.join(os.path.dirname(__file__), "simulator.html")
    if os.path.exists(sim_path):
        with open(sim_path, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="Simulator HTML file not found.")

class QualifyRequest(BaseModel):
    session_id: Optional[str] = "sess_demo"
    user_message: str

class VapiFunctionCallPayload(BaseModel):
    message: Dict[str, Any]


@router.get("/health")
def q1_health_check():
    return {
        "status": "healthy",
        "module": "Q1 Business Loan Qualification Voice Agent",
        "active_sessions": len(active_sessions),
        "voice_platform": "Vapi"
    }


@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Vapi Server Webhook handler.
    Receives Vapi call events, end-of-call reports, and function call requests (e.g. query_knowledge_base).
    """
    try:
        body = await request.json()
        logger.info(f"Vapi Webhook Received event: {body.get('message', {}).get('type')}")

        msg = body.get("message", {})
        msg_type = msg.get("type")

        # 1. Handle Vapi Tool / Function Call
        if msg_type in ["tool-calls", "function-call"]:
            tool_calls = msg.get("toolCalls", []) or [msg.get("functionCall")]
            results = []

            for call in tool_calls:
                if not call:
                    continue
                fn_name = call.get("function", {}).get("name") or call.get("name")
                call_id = call.get("id", "call_1")
                args = call.get("function", {}).get("arguments") or call.get("arguments", {})

                if isinstance(args, str):
                    import json
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {"query": args}

                if fn_name == "query_knowledge_base":
                    query_text = args.get("query", "")
                    rag_result = query_knowledge_base(query=query_text)
                    results.append({
                        "toolCallId": call_id,
                        "result": rag_result.get("grounded_answer")
                    })

            return {"results": results}

        # 2. Handle End-of-Call Report
        elif msg_type == "end-of-call-report":
            call_id = msg.get("call", {}).get("id", "unknown")
            transcript = msg.get("transcript", "")
            logger.info(f"End of call report for call {call_id}. Transcript length: {len(transcript)}")
            return {"status": "logged", "call_id": call_id}

        return {"status": "received"}

    except Exception as e:
        logger.error(f"Error handling Vapi webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qualify")
def qualify_turn(req: QualifyRequest):
    """
    Direct REST endpoint to execute a conversation turn for testing or web client interaction.
    """
    sess_id = req.session_id or "sess_demo"
    if sess_id not in active_sessions:
        active_sessions[sess_id] = Q1ConversationManager(session_id=sess_id)

    manager = active_sessions[sess_id]
    result = manager.process_turn(req.user_message)
    return result


@router.post("/log_session")
def log_session(session_id: str):
    if session_id in active_sessions:
        manager = active_sessions[session_id]
        return {
            "session_id": session_id,
            "history_length": len(manager.history),
            "state": manager.state.model_dump(),
            "citations_retrieved": len(manager.retrieved_citations)
        }
    raise HTTPException(status_code=404, detail="Session not found.")
