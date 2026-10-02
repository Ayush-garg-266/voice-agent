<!-- DEMO / SYNTHETIC DATA: FOR ASSESSMENT PURPOSES ONLY -->
# DEMO Edge Cases, Fallbacks & Human Escalation Matrix

**Document ID**: `SRC_DOC_003`
**Version**: `1.0`
**Effective Date**: `10/02/2026` (Format: MM/DD/YYYY)
**Category**: `Escalation Protocols & Edge Cases`
**Status**: `DEMO / SYNTHETIC`

---

## 1. Edge Case Handling Matrix

| Scenario / Edge Case | Trigger Condition | System Protocol & Action |
| :--- | :--- | :--- |
| **Incomplete Information** | Customer omits revenue or business age | Prompt caller up to 2 times for missing metric. If still withheld, mark application incomplete and trigger email callback link. |
| **Conflicting Revenue Details** | Customer claims $500k annual revenue but states $10k monthly cashflow ($120k/yr) | Voice bot highlights discrepancy gently: *"I noticed your estimated annual revenue is $500k, but recent monthly cashflow is around $10k. Could you clarify if there are seasonal peaks?"* |
| **Unregistered Business** | Applicant operates informally without registered business entity | State policy boundary: *"To qualify for a commercial loan, the enterprise must be registered (LLC, Corp, Sole Prop). We recommend registering your business before applying."* |
| **Business Too New (<12 months)** | Operating history is under 1 year | State minimum threshold: *"Our commercial policy requires at least 12 months of active operations. We invite you to re-apply once your business reaches 12 months."* |
| **Unsupported Loan Purpose** | Purpose is speculative crypto, personal travel, or gambling | Execute firm out-of-scope fallback: *"Our business loans cannot be used for personal expenses or speculative investments. I can only assist with commercial business purposes."* |

---

## 2. Human Escalation Protocols

Voice agents and automated representatives must immediately initiate a human transfer or callback request under any of the following 5 conditions:

1. **Explicit Human Request**: The caller asks to speak with a human, agent, representative, or loan officer.
   - *Script*: *"I am transferring you to a senior loan specialist now. Please hold for just a moment."*
2. **Policy Ambiguity / Complex Financial Structure**: Complex multi-entity holding companies, international subsidiaries, or non-standard revenue models.
   - *Script*: *"Because your corporate structure involves multiple entities, I will connect you with a commercial underwriting specialist who can customize your offer."*
3. **Repeated Customer Frustration or Complaints**: Sentiment extraction detects high frustration or explicit complaints.
   - *Script*: *"I apologize for the frustration. Let me connect you directly with a customer care manager to assist you immediately."*
4. **Unsupported Policy Questions**: Queries outside loan product scope (e.g. tax filing advice, legal opinions, personal bankruptcy law).
   - *Script*: *"I am unable to provide advice on tax filing or personal legal matters. Would you like me to connect you with a customer representative for loan inquiries?"*
5. **Sensitive Financial Distress**: Caller mentions imminent bankruptcy, severe insolvency, or personal hardship.
   - *Script*: *"I understand this is a challenging financial period. I am escalating your profile to our senior relief officer to discuss tailored hardship support options."*
