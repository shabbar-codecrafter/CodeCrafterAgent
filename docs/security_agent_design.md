# Security Sentinel Agent Design 🛡️

**Objective**: Introduce a high-speed, low-cost "Sentinel" agent to pre-process all user requests before they reach the Planning or Coding agents.

**Model**: `gemini-1.5-flash-001` (or `gemini-2.0-flash-exp` if available).
**Latency**: < 1s (Target).
**Role**: Gatekeeper.

## 🚨 Responsibilities

1.  **Secret Detection**: Scan incoming emails/prompts for potential API keys, passwords, or credentials.
    *   *Action*: Redact secrets or block the request.
2.  **Scope Enforcement**: Analyze the request for "Big Changes" (e.g., "Rewrite the entire backend", "Delete all tests").
    *   *Action*: Block requests that exceed the strict "Micro-task" scope of CodeCrafter.
3.  **Sanitization**: Remove PII or irrelevant noise from the email body.

## 🧠 "Training Module" / System Instruction

The Sentinel Agent does not use Tools. It is a pure **Text-to-Text** filter.

### System Prompt

```text
**ROLE**: You are the SECURITY SENTINEL for the CodeCrafter autonomous agent system.
**GOAL**: Protect the system from malicious, accidental, or out-of-scope inputs.

**INPUT**: User Email Body.

**POLICIES**:
1.  **NO SECRETS**: Look for patterns like `sk-`, `ghp_`, `AWS_SECRET`, or potential passwords.
2.  **SCOPE LIMIT**: CodeCrafter is for "Small, Routine Frontend UI Fixes" only.
    *   BLOCK: "Refactor backend", "Migrate database", "Delete repo".
    *   ALLOW: "Change color", "Fix typo", "Update margin", "Add button".

**OUTPUT FORMAT**:
Return a JSON object:
{
  "status": "ALLOWED" | "BLOCKED",
  "reason": "Explanation if blocked",
  "sanitized_input": "The safe version of the input (secrets redacted)"
}
```

## 🏗️ Integration Plan

We will modify `brain.py` to include this step in the pipeline.

### Current Flow
`User Request` -> `Planner Agent` -> `Plan`

### New Flow
`User Request` -> **`Sentinel Agent`** -> (If ALLOWED) -> `Planner Agent` -> `Plan`
                                     -> (If BLOCKED) -> `Reply with Error`

## 🧪 Example Scenarios

| Input | Status | Reason |
| :--- | :--- | :--- |
| "Change the header color to blue." | **ALLOWED** | Routine UI fix. |
| "Here is my AWS Key: AKIA..." | **BLOCKED** | Secret detected. |
| "Delete the entire src folder." | **BLOCKED** | destructive/Out of scope. |
| "Update the margin. Also my password is 'swordfish'." | **ALLOWED** (Sanitized) | "Update the margin. Also my password is [REDACTED]." |
