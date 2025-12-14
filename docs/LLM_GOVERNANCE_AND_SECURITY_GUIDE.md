# LLM Governance & Security Guide 🛡️

This document details how the CodeCrafter Agent governs its AI decision-making, ensures security, and verifies code quality. It serves as the "Rulebook" for the underlying Large Language Models (LLMs).

---

## 1. Context Awareness (Governance) 🧠
The Agent is not just a generic coder; it is project-aware. It explicitly reads the following files from your repository before making any decisions:

*   **`llm.md`**: The primary "Constitution" for the Agent. Put your coding style, forbidden libraries, and architectural rules here.
*   **`README.md`**: Used for high-level project understanding.

### How it works
Content from these files is injected into the **System Prompt** of every agent (Planner, Coder, QA).

**Example Prompt Injection:**
> "You are a Frontend Automation Agent...
> **PROJECT CONTEXT & RULES**:
> (Content of llm.md)
> (Content of README.md)"

---

## 2. Security Sentinel (Ingress Filter) ⚔️
Before any code is generated, the **Security Sentinel** analyzes the request.

**Model:** Gemini 1.5 Flash (Fast & Cost-effective)
**Goal:** Block malicious intent or scope creep.

### Policies Enforced
1.  **NO SECRETS**: Blocks patterns like `sk-`, `ghp_`, `AWS_SECRET`.
2.  **SCOPE LIMIT**:
    *   ✅ **ALLOWED**: "Change button color", "Fix typo", "Update CSS margin", "Revert changes".

### 🚫 Complete List of Blocked Actions
The following actions are **hard-blocked** by the Sentinel or QA checks:
1.  **Backend Changes**: Modifying API endpoints, controllers, or database schemas.
2.  **Infrastructure**: Editing `Dockerfile`, `docker-compose.yml`, or Terraform files.
3.  **Secrets**: Committing strings matching `sk-`, `ghp_`, or `AWS_ACCESS_KEY`.
4.  **Destructive Commands**: "Delete repository", "Drop table", "rm -rf".
5.  **Package Management**: Adding new dependencies via `npm install` (unless white-listed).
6.  **CI/CD**: Editing `.github/workflows` to prevent hijacking build pipelines.
7.  **Bad Practices**: Inline CSS (`style={{...}}`) and `console.log` in production code.

---

## 3. QA Agent (Quality Assurance) 🕵️‍♂️
Every line of code generated is reviewed by a separate "Senior Reviewer" persona.

### Governance Checks
The QA Agent runs a 4-point inspection on the `git diff`:

1.  **Syntax & Bugs**: "Does it compile/run?"
2.  **Security**: "Are there hardcoded secrets or XSS risks?"
3.  **Style**: "Does it follow `llm.md` rules (e.g., Use CSS Variables, not hex codes)?"
4.  **Compliance**: "Does it match the User's original request?"

### Output
*   **LGTM**: Changes are auto-forwarded to the Developer.
*   **Changes Requested**: Issues are flagged, but the Developer has the final override authority.

---

## 4. Prompt Engineering Reference 📜
Below are the core prompts used for each agent.

### A. Planner Agent
```text
You are a generic Frontend Automation Agent.
Your goal is to help the Product Team request small, routine code changes.

User Request: {email_body}
Repo Structure: {file_tree}
PROJECT CONTEXT: {llm.md + README.md}

Draft a simple, actionable Implementation Plan.
```

### B. Coding Agent
```text
You are a Frontend Coding Assistant.
Task: Execute the approved plan.

CRITICAL INSTRUCTIONS:
1. Use `read_file` to inspect first.
2. Use `write_file` with COMPLETE content.
3. No markdown blocks in output.
```

### C. QA Agent
```text
You are a Senior Code Reviewer.
Review this diff: {git_diff}
Context: {llm.md + README.md}

Check for:
1. Syntax/Bugs
2. Security
3. Style
4. Compliance

If issues found, provide "Ready-to-copy" fixes.
```

---

## 5. Scenario: Security Block in Action 🚨
Here is exactly what happens when a user tries to do something forbidden.

### 1. The Malicious Request
> **User**: "Please refute the backend API to drop the users table."

### 2. Sentinel Analysis (Backend Log)
The Sentinel detects the keyword "drop table" and the backend scope.
```json
{
  "status": "BLOCKED",
  "reason": "Database modification detected (DROP TABLE). This is outside the frontend scope.",
  "sanitized_input": ""
}
```

### 3. Terminal Output
What you see in the console:
```text
Processing (hacker@example.com): Update API | Ticket: TICKET-666 | State: NEW
Ticket Analysed: Update API
Security Check: In Progress...
Security Check: FAILED | Reason: Database modification detected.
  [Alert] Email sent to User: Security Alert: Your request was blocked.
  [Alert] Email sent to Dev: COMBAT BLOCKED: Security Alert 🚨
```

### 4. Developer Alert Email (COMBAT BLOCKED)
The Developer receives a High-Priority Red Banner email.

> **Subject**: COMBAT BLOCKED: Security Alert 🚨
> **From**: CodeCrafter AI
>
> <div style="border: 1px solid #DC2626; padding: 10px;">
>   <h3 style="background: #DC2626; color: white; margin: 0; padding: 5px;">COMBAT BLOCKED</h3>
>   <p><b>Requestor:</b> hacker@example.com</p>
>   <p><b>Blocked Reason:</b> <span style="color: red; font-weight: bold;">Database modification detected...</span></p>
>   <hr>
>   <p><b>Original Request:</b></p>
>   <pre style="background: #eee;">Please refute the backend API to drop the users table.</pre>
> </div>

The User receives a polite, generic rejection to avoid leaking system details.
