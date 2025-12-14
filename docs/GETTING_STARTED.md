# 🚀 Getting Started with CodeCrafter

This guide will help you set up the CodeCrafter Agent on your local machine for testing and development.

## 📋 Prerequisites
*   Python 3.10 or higher
*   Git installed
*   A Google Cloud Project (for Gemini API)
*   A Gmail account (for IMAP/SMTP)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd CodeCrafterAgentLocal
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
The agent uses an `.env` file to store credentials. We have provided a template for you.

1.  Copy the example file:
    ```bash
    cp .env.example .env
    # OR on Windows PowerShell:
    Copy-Item .env.example .env
    ```

2.  Open `.env` in your text editor and fill in the following:

    | Variable | Description | Example |
    | :--- | :--- | :--- |
    | `EMAIL_USER` | Your Gmail address | `agent@gmail.com` |
    | `EMAIL_PASS` | Your App Password (Not your login password!) | `abcd efgh ijkl mnop` |
    | `GOOGLE_API_KEY` | Gemini API Key | `AIzaSy...` |
    | `GITHUB_TOKEN` | Personal Access Token (Classic) with `repo` scope | `ghp_...` |
    | `REPO_URL` | The target repo you want the agent to work on | `https://github.com/user/test-repo.git` |

### 4. Run the Agent
```bash
python main.py
```
You should see output like:
```text
Starting CodeCrafter Agent (Version 1)...
[Git] Pulling changes...
Polling for emails...
```

---

## 🧪 How to Test
1.  Send an email to your `EMAIL_USER` address.
2.  **Subject**: "Update README" (or any coding task).
3.  **Body**: Describe what you want the agent to do.
4.  Wait for the "In Progress" email reply.
5.  Watch the logs for the Plan and QA report.

## ❓ Troubleshooting
*   **IMAP Error**: Ensure you enabled 2FA and created an App Password for your Gmail account.
*   **Git Error**: Ensure your `GITHUB_TOKEN` has permissions to push to `REPO_URL`.
