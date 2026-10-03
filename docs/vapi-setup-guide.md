# Vapi Dashboard Setup & Integration Guide for Q1 Voice Agent

This step-by-step guide explains how to configure the Knowledge-Grounded Business Loan Qualification Assistant in the [Vapi Dashboard](https://dashboard.vapi.ai/).

---

## 1. Environment & API Key Verification

Ensure the following environment variables are present in your `.env` file:

```env
GEMINI_API_KEY=<your_gemini_api_key>
VAPI_API_KEY=<your_vapi_api_key>
VAPI_PUBLIC_KEY=<your_vapi_public_key>
```

---

## 2. Step-by-Step Vapi Assistant Configuration

### Step 1: Create New Assistant
1. Log into your [Vapi Dashboard](https://dashboard.vapi.ai/).
2. Navigate to **Assistants** -> Click **+ Create Assistant**.
3. Select **Blank Template**.
4. Set **Assistant Name**: `Q1 Business Loan Qualification Agent`.

---

### Step 2: Model Configuration (Google Gemini)
In the Assistant configuration panel under **Model**:
- **Provider**: `Custom LLM` or `Google / Gemini` *(Verify exact dropdown label in your current Vapi UI)*.
- **Model Name**: `gemini-2.5-flash` or `gemini-1.5-flash`.
- **Temperature**: `0.3` *(Low temperature ensures deterministic policy grounding)*.
- **Max Tokens**: `250` *(Keeps voice turn responses short and conversational)*.

---

### Step 3: System Prompt
In the **System Prompt** / **Instructions** field, paste the exact contents from [`q1_business_loan/prompts/system_prompt.py`](file:///C:/Users/user/OneDrive/Desktop/Darwix%20A/ai-engineer-assessment/q1_business_loan/prompts/system_prompt.py):

```text
You are a professional, polite, and empathetic Senior Business Loan Qualification Representative for SME Financial Services.

YOUR OBJECTIVE:
Qualify small and medium-sized business owners for a commercial loan by collecting essential business details, evaluating preliminary eligibility, and addressing questions or objections using verified policy information.

[Insert complete prompt from system_prompt.py]
```

---

### Step 4: First Message (Greeting)
Under **First Message** / **Greeting**:
- Set text:
  `"Hello! I'm your Senior Business Loan Representative. I'd like to understand your business and loan requirements to see whether this may be a suitable fit for our commercial borrowing programs. What is the name of your business?"`

---

### Step 5: Voice & Speech Synthesis (TTS)
Under **Voice**:
- **Provider**: `ElevenLabs` or `Deepgram` or `Azure` *(or default Vapi Voice)*.
- **Voice ID**: Choose a natural, clear professional voice (e.g. `Rachel` / `Brian` / `Jenny`).

---

### Step 6: Server Webhook & Tool Configuration
Under **Server URL** / **Webhooks**:
- Set **Server URL**: `https://your-public-domain.ngrok-free.app/q1/webhook`
  *(Use `ngrok http 8000` to expose your local FastAPI server).*

Under **Tools** -> Add **Custom Function Tool**:
- **Function Name**: `query_knowledge_base`
- **Description**: `Retrieves verified business loan policies, interest rates, eligibility criteria, and objection handling scripts from Q2 Knowledge Base.`
- **Parameters Schema (JSON)**:
  ```json
  {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The customer's question or objection regarding business loans."
      }
    },
    "required": ["query"]
  }
  ```
- **Server Webhook Target**: Enable `Server Webhook` so function calls are routed to your `/q1/webhook` endpoint.

---

### Step 7: Call Behavior & End of Call
- **Silence Timeout**: `10 seconds`.
- **End Call Phrases**: `"goodbye"`, `"thank you bye"`, `"have a good day"`.
- **End Call Function**: Trigger webhook report on call finish.

---

## 3. Testing Your Voice Agent

### Option A: Web Browser Voice Call Simulator
Click the **Test Call** button in the Vapi Dashboard or open the built-in local web simulator at `http://localhost:8000/q1/simulator` (after starting FastAPI server).

### Option B: Real Phone Number (Optional)
If a phone number is assigned in your Vapi account:
1. Go to **Phone Numbers** in Vapi Dashboard.
2. Link your phone number to the `Q1 Business Loan Qualification Agent` assistant.
3. Dial the number from your phone to execute live audio testing.
