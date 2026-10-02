"""
Streamlit Live Dashboard for Q4 Real-Time Agent Assistance & Supervisor Nudge Engine.
Displays live streaming transcripts, Gemini-detected signals, active policy nudges,
suppressed nudges log, and P50/P95 latency breakdown cards.
"""

import time
import streamlit as st
from q4_realtime.websocket.broadcaster import RealtimeCallPipeline
from q4_realtime.evaluation.latency_benchmark import compute_pipeline_latency_stats

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Real-Time Agent Assistance Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic Dark-Mode CSS
st.markdown("""
<style>
    .main {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .stAppHeader {
        background-color: transparent;
    }
    .card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }
    .nudge-critical {
        border-left: 4px solid #f85149;
        background: rgba(248, 81, 73, 0.1);
    }
    .nudge-high {
        border-left: 4px solid #d29922;
        background: rgba(210, 153, 34, 0.1);
    }
    .nudge-medium {
        border-left: 4px solid #58a6ff;
        background: rgba(88, 166, 255, 0.1);
    }
    .suppressed-tag {
        color: #8b949e;
        font-size: 0.85rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# Sample Test Scenarios
TEST_SCENARIOS = {
    "1. Missed Cross-Sell Opportunity": [
        {"speaker": "Agent", "text": "Good afternoon, thank you for calling loan support. How can I help?"},
        {"speaker": "Customer", "text": "Hi, I'm expanding my retail store and need a ₱500,000 equipment loan. I also opened a new warehouse branch last month."},
        {"speaker": "Agent", "text": "Sure, I can help process your equipment loan right now."},
        {"speaker": "Customer", "text": "Great, do you have any insurance or commercial property protection for the new warehouse?"},
        {"speaker": "Agent", "text": "Let me just check your equipment loan interest rate first."}  # Missed cross-sell trigger
    ],
    "2. Compliance Risk / Missing Disclosure": [
        {"speaker": "Customer", "text": "What is the total annual percentage rate (APR) and early repayment penalty on this loan?"},
        {"speaker": "Agent", "text": "Don't worry about the APR details, we can just approve the funds today without reading all the rate schedules."}  # Compliance disclosure gap
    ],
    "3. Rising Customer Frustration": [
        {"speaker": "Customer", "text": "I've been transferred three times today and nobody is answering my billing inquiry!"},
        {"speaker": "Agent", "text": "Please hold while I check the system."},
        {"speaker": "Customer", "text": "This is ridiculous! I am losing money while waiting on hold. Connect me to your manager immediately!"}  # Frustration trigger
    ],
    "4. Noisy / Ambiguous Audio (False Positive Control)": [
        {"speaker": "Customer", "text": "[muffled static audio] ...uh... rate... discount... maybe... [background noise]"}  # Ambiguous audio trigger
    ]
}

# Sidebar Controls
st.sidebar.title("⚡ Control Panel")
st.sidebar.markdown("Configure real-time nudge policy thresholds and streaming parameters.")

selected_scenario_name = st.sidebar.selectbox("Select Test Scenario Script", list(TEST_SCENARIOS.keys()))
confidence_threshold = st.sidebar.slider("Confidence Threshold (Min)", min_value=0.50, max_value=0.95, value=0.75, step=0.05)
cooldown_seconds = st.sidebar.slider("Cooldown Window (Seconds)", min_value=5, max_value=60, value=30, step=5)

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Google Gemini 1.5 Flash + Deepgram ASR Pipeline")

# Main Title & Subtitle
st.title("🎙️ Real-Time Agent Assistance & Supervisor Dashboard")
st.markdown("Continuous live call monitoring, Gemini signal extraction, and policy-governed nudge engine.")

col_main, col_metrics = st.columns([2, 1])

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "active_nudges" not in st.session_state:
    st.session_state.active_nudges = []
if "suppressed_nudges" not in st.session_state:
    st.session_state.suppressed_nudges = []
if "latency_records" not in st.session_state:
    st.session_state.latency_records = []

# Action Buttons
start_sim = st.button("▶️ Start Live Call Simulation", use_container_width=True)

if start_sim:
    st.session_state.history = []
    st.session_state.active_nudges = []
    st.session_state.suppressed_nudges = []
    st.session_state.latency_records = []

    pipeline = RealtimeCallPipeline(confidence_threshold=confidence_threshold)
    script_turns = TEST_SCENARIOS[selected_scenario_name]

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, turn in enumerate(script_turns):
        status_text.text(f"Streaming turn {idx+1}/{len(script_turns)}: {turn['speaker']} speaking...")

        chunk = {
            "chunk_id": f"chk_{idx+1:04d}",
            "speaker": turn["speaker"],
            "text": turn["text"],
            "audio_received_timestamp": time.time()
        }

        event_payload = pipeline.process_live_chunk(chunk)

        st.session_state.history.append(event_payload["frame"])
        if event_payload["policy_result"].get("status") == "EMITTED":
            st.session_state.active_nudges.append(event_payload["policy_result"]["nudge"])
        elif event_payload["policy_result"].get("status") == "SUPPRESSED":
            st.session_state.suppressed_nudges.append(event_payload["policy_result"]["details"])

        st.session_state.latency_records.append(event_payload["latency"])
        progress_bar.progress((idx + 1) / len(script_turns))
        time.sleep(0.5)

    status_text.success("Live call streaming simulation completed!")

# Render Live Columns
with col_main:
    st.subheader("🗣️ Live Transcript Stream")
    transcript_container = st.container()
    with transcript_container:
        if not st.session_state.history:
            st.info("Click 'Start Live Call Simulation' to begin streaming transcript.")
        for frame in st.session_state.history:
            speaker_icon = "👤" if frame["speaker"] == "Customer" else "🎧"
            st.markdown(
                f"<div class='card'><b>{speaker_icon} {frame['speaker']}:</b> {frame['text']}"
                f"<br><span style='color:#8b949e; font-size:0.8rem;'>ASR Latency: {frame['asr_latency_ms']}ms</span></div>",
                unsafe_allow_html=True
            )

    st.subheader("🔔 Active Real-Time Nudges")
    if not st.session_state.active_nudges:
        st.caption("No active nudges triggered.")
    for ndg in st.session_state.active_nudges:
        urgency_class = f"nudge-{ndg.get('urgency', 'medium')}"
        st.markdown(
            f"<div class='card {urgency_class}'>"
            f"<b>[{ndg.get('urgency', 'MEDIUM').upper()}] {ndg.get('signal_type', '').upper()}</b><br>"
            f"💡 <b>{ndg.get('nudge_text')}</b><br>"
            f"📌 <i>Evidence: \"{ndg.get('evidence')}\"</i><br>"
            f"<span style='color:#8b949e; font-size:0.8rem;'>Confidence: {ndg.get('confidence', 0):.2f} | E2E Latency: {ndg.get('total_audio_to_nudge_ms')}ms</span>"
            f"</div>",
            unsafe_allow_html=True
        )

with col_metrics:
    st.subheader("📊 Latency Metrics (P50 / P95)")
    stats = compute_pipeline_latency_stats(st.session_state.latency_records)
    if stats["sample_size"] > 0:
        st.markdown(f"**Sample Size**: {stats['sample_size']} frames")
        st.metric("ASR Latency (P50)", f"{stats['p50']['asr_ms']} ms")
        st.metric("Gemini Signal Latency (P50)", f"{stats['p50']['signal_ms']} ms")
        st.metric("Total E2E Nudge Latency (P50)", f"{stats['p50']['total_audio_to_nudge_ms']} ms")
        st.metric("Total E2E Nudge Latency (P95)", f"{stats['p95']['total_audio_to_nudge_ms']} ms")
    else:
        st.caption("Awaiting live stream measurements...")

    st.subheader("🛡️ Suppressed Nudges Log")
    if not st.session_state.suppressed_nudges:
        st.caption("No suppressed nudges.")
    for sup in st.session_state.suppressed_nudges:
        st.markdown(
            f"<div class='card'><span class='suppressed-tag'>"
            f"🚫 <b>{sup.get('signal_type')}</b> (Conf: {sup.get('confidence', 0.0):.2f})<br>"
            f"Reason: {sup.get('reason')}"
            f"</span></div>",
            unsafe_allow_html=True
        )
