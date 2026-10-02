"""
Generates the crisp, production-grade technical architecture diagram image for docs/architecture.png using Matplotlib & Pillow.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_diagram():
    os.makedirs("docs", exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 16), dpi=300)
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")
    ax.axis("off")

    # Colors
    bg_card = "#161b22"
    border_blue = "#58a6ff"
    border_green = "#3fb950"
    border_purple = "#bc8cff"
    border_gold = "#d29922"
    text_color = "#c9d1d9"
    sub_color = "#8b949e"

    # Header Title
    ax.text(7.0, 15.5, "AI ENGINEER ASSESSMENT — TECHNICAL ARCHITECTURE",
            ha="center", va="center", fontsize=18, fontweight="bold", color="#ffffff")
    ax.text(7.0, 15.1, "Unified Platform Powered by Google Gemini API & Deepgram Streaming",
            ha="center", va="center", fontsize=12, color=sub_color)

    # -------------------------------------------------------------
    # SECTION 1: KNOWLEDGE BASE & VOICE AGENTS (Q1, Q2, Q3)
    # -------------------------------------------------------------
    ax.text(7.0, 14.4, "SECTION 1: KNOWLEDGE BASE GROUNDING & VOICE BOT PLATFORM (Q1, Q2, Q3)",
            ha="center", va="center", fontsize=12, fontweight="bold", color=border_blue)

    # Q2 Box (Top Center)
    box_q2 = patches.FancyBboxPatch((4.0, 10.8), 6.0, 3.2, boxstyle="round,pad=0.3",
                                    fc=bg_card, ec=border_purple, lw=2)
    ax.add_patch(box_q2)
    ax.text(7.0, 13.6, "Q2 KNOWLEDGE BASE ARCHITECTURE", ha="center", va="center",
            fontsize=12, fontweight="bold", color="#ffffff")

    q2_text = (
        "• Data Ingestion Pipeline (TXT, MD, CSV, JSON, HTML, PDF)\n"
        "• Deterministic Text Cleaning & PII Scrubbing (Regex)\n"
        "• Semantic Chunker (Header & Paragraph Boundaries)\n"
        "• ChromaDB Vector Index (gemini-embedding-001) + BM25 Sparse Index\n"
        "• Reciprocal Rank Fusion (RRF) + Optional Cohere Reranker\n"
        "• Traceable Citation Generator & FastAPI Endpoint (/kb/query)"
    )
    ax.text(7.0, 12.1, q2_text, ha="center", va="center", fontsize=9, color=text_color)

    # Connector Arrow from Q2 to Retrieval API
    ax.annotate("", xy=(7.0, 9.8), xytext=(7.0, 10.8),
                arrowprops=dict(arrowstyle="->", color=border_purple, lw=2.5))
    ax.text(7.0, 10.3, "Retrieval API (/kb/query)", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#ffffff", bbox=dict(boxstyle="round,pad=0.3", fc="#21262d", ec=border_purple))

    # Split Arrow to Q1 and Q3
    ax.annotate("", xy=(3.0, 9.0), xytext=(7.0, 9.7),
                arrowprops=dict(arrowstyle="->", color=border_blue, lw=2))
    ax.annotate("", xy=(11.0, 9.0), xytext=(7.0, 9.7),
                arrowprops=dict(arrowstyle="->", color=border_green, lw=2))

    # Q1 Box (Bottom Left)
    box_q1 = patches.FancyBboxPatch((0.5, 6.2), 5.0, 2.7, boxstyle="round,pad=0.3",
                                    fc=bg_card, ec=border_blue, lw=2)
    ax.add_patch(box_q1)
    ax.text(3.0, 8.5, "Q1 BUSINESS LOAN VOICE AGENT", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#ffffff")
    q1_text = (
        "• Domain: SME Business Loan Qualification\n"
        "• Telephony Integration: Vapi Webhooks + PSTN\n"
        "• Web Simulator: HTML/JS Inbound Interface\n"
        "• LLM Engine: Google Gemini API (gemini-1.5-flash)\n"
        "• RAG Tool: query_knowledge_base Tool Calling\n"
        "• Protocols: Grounded Fallback & Escalation"
    )
    ax.text(3.0, 7.3, q1_text, ha="center", va="center", fontsize=8.5, color=text_color)

    # Q3 Box (Bottom Right)
    box_q3 = patches.FancyBboxPatch((8.5, 6.2), 5.0, 2.7, boxstyle="round,pad=0.3",
                                    fc=bg_card, ec=border_green, lw=2)
    ax.add_patch(box_q3)
    ax.text(11.0, 8.5, "Q3 MULTILINGUAL VOICE BOTS", ha="center", va="center",
            fontsize=11, fontweight="bold", color="#ffffff")
    q3_text = (
        "• Philippines: Bancassurance Taglish (po/opo)\n"
        "  - Terms: premium, policy, rider, lapse, beneficiary\n"
        "• Indonesia: Multifinance Bahasa Indonesia\n"
        "  - Terms: cicilan, tenor, denda, DP, jatuh tempo\n"
        "  - Dialect: Javanese Medok Accent Tolerance\n"
        "• Speech Evaluation: Google Cloud TTS / Deepgram"
    )
    ax.text(11.0, 7.3, q3_text, ha="center", va="center", fontsize=8.5, color=text_color)

    # -------------------------------------------------------------
    # SECTION 2: Q4 REAL-TIME AGENT ASSISTANCE & NUDGE ENGINE
    # -------------------------------------------------------------
    ax.text(7.0, 5.4, "SECTION 2: Q4 REAL-TIME STREAMING & SUPERVISOR NUDGE PIPELINE",
            ha="center", va="center", fontsize=12, fontweight="bold", color=border_gold)

    q4_boxes = [
        ("Streaming Audio", "1.5s Chunk Stream\nReal-Time Replay"),
        ("Deepgram ASR", "Streaming Speech-to-Text\n(audio_received_ts)"),
        ("Transcript Chunks", "Speaker-Separated\nFrame History"),
        ("Gemini Signal Extractor", "Structured JSON Schema\n(transcription_ts → signal_ts)"),
        ("Nudge Policy Engine", "Cooldown & Suppression\nConfidence >= 0.75"),
        ("WebSocket Broadcaster", "FastAPI / asyncio\nEvent Stream"),
        ("Streamlit Live Dashboard", "P50/P95 Metrics Card\nActive & Suppressed Log")
    ]

    box_width = 1.6
    spacing = 1.95
    start_x = 0.5

    for i, (title, desc) in enumerate(q4_boxes):
        x = start_x + (i * spacing)
        y = 2.5
        b = patches.FancyBboxPatch((x, y), box_width, 2.0, boxstyle="round,pad=0.2",
                                   fc=bg_card, ec=border_gold, lw=1.5)
        ax.add_patch(b)
        ax.text(x + box_width/2, y + 1.6, title, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="#ffffff")
        ax.text(x + box_width/2, y + 0.8, desc, ha="center", va="center",
                fontsize=7.5, color=text_color)

        # Draw Arrow to next box except for last
        if i < len(q4_boxes) - 1:
            ax.annotate("", xy=(x + box_width + 0.3, y + 1.0), xytext=(x + box_width + 0.05, y + 1.0),
                        arrowprops=dict(arrowstyle="->", color=border_gold, lw=1.8))

    # Technology Stack Footer Bar
    footer_box = patches.FancyBboxPatch((0.5, 0.4), 13.0, 1.2, boxstyle="round,pad=0.2",
                                        fc="#21262d", ec="#30363d", lw=1)
    ax.add_patch(footer_box)
    tech_text = (
        "TECHNOLOGY STACK SUMMARY:\n"
        "• LLM & Embeddings: Google Gemini API (google-genai SDK, gemini-1.5-flash, gemini-embedding-001) [STRICT ZERO-OPENAI DEPENDENCY]\n"
        "• Web Framework & API: FastAPI, Uvicorn, Streamlit, WebSockets | • Vector Storage: ChromaDB | • Sparse Index: Rank-BM25\n"
        "• Telephony & Speech: Vapi Webhooks, Deepgram Streaming ASR (Nova-2), Google Cloud TTS | • Telemetry: SQLite, Optional LangSmith"
    )
    ax.text(7.0, 1.0, tech_text, ha="center", va="center", fontsize=8, color="#8b949e")

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 16)
    plt.tight_layout()
    plt.savefig("docs/architecture.png", dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print("Architecture diagram generated successfully at docs/architecture.png")

if __name__ == "__main__":
    generate_diagram()
