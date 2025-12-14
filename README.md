# CodeCrafter Agent (Version 1) 🤖✨
**An Autonomous Dual-Approval Coding Agent**.

CodeCrafter listens to emails, plans code changes, modifies your local repository, and opens Pull Requests—all while enforcing strict security and governance policies.

---

## 🚀 Features
*   **Version 1 Workflow**: 
    1.  **Plan Approval**: User approves the Strategy (Blue Email).
    2.  **Code Review**: Developer approves the final QA Report (Indigo Email).
*   **Security Sentinel**: Blocks malicious requests (e.g., "Drop DB", "Exfiltrate Keys") using Gemini 1.5.
*   **Context Aware**: Reads your repo's `llm.md` and `README.md` to adhere to *your* coding standards.
*   **Automated QA**: Runs syntax, style, and security checks on every generated line of code.

---

## 🛠️ Setup Guide

### 1. Prerequisites
*   Python 3.10+
*   Git installed and available in PATH.
*   A dedicated Gmail account (enabled for IMAP).
*   A GitHub Personal Access Token (Classic) with `repo` scope.

### 2. Installation
```bash
# Clone this agent repository
git clone https://github.com/your-username/CodeCrafterAgent.git
cd CodeCrafterAgent

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration (.env)
Create a `.env` file in the root directory:

```ini
# Google Cloud / Gemini
GOOGLE_API_KEY=AIza...
GOOGLE_CLOUD_PROJECT=your-project-id

# Email (Ingress/Egress)
EMAIL_USER=agent@your-domain.com
EMAIL_PASS=your-app-password
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com

# GitHub (Target Repo)
# The URL of the repo you want the Agent to work on
REPO_URL=https://github.com/Start-Up/Osmos-Pulse-Dashboard.git
GITHUB_TOKEN=ghp_...

# Agent Identity
AGENT_NAME=CodeCrafter
```

### 4. Running the Agent
```bash
python main.py
```
The agent will:
1.  Clone the target `REPO_URL` into `./repo_clone`.
2.  Start polling your email inbox.
3.  Wait for requests!

---

## 📚 Documentation
*   [**Architecture & Guide**](ARCHITECTURE_AND_GUIDE.md): Technical deep dive into the system.
*   [**LLM Governance**](LLM_GOVERNANCE_AND_SECURITY_GUIDE.md): Security policies, blocked actions, and prompt engineering.
*   [**Walkthrough**](WALKTHROUGH_LAST_RUN.md): Example of a real ticket lifecycle.

---

## 🔒 Security
This agent is designed for **Frontend UI Tasks** only.
*   **Blocked**: Backend changes, Docker edits, Secret commits.
*   **Allowed**: CSS fixes, React component updates, Text changes.

See `LLM_GOVERNANCE_AND_SECURITY_GUIDE.md` for the full blocklist.
