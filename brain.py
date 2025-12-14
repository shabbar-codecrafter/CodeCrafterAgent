
import asyncio
import os
from google.adk.agents.llm_agent import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, Content

from tools import AgentTools

class AgentBrain:
    def __init__(self):
        # Initialize two specialized agents or one generic one. 
        # For simplicity adhering to previous logic, we use one agent but with dynamic instructions if needed.
        # However, the reference uses specialized agents. Let's stick to a generic one or create on fly.
        self.model_name = "gemini-3-pro-preview"
        self.agent_name = "CodeCrafter"
        self.tools = AgentTools()  # Init tools

        # Sentinel Config
        # Using the same model as coder to guarantee availability (1.5-pro returned 404)
        self.sentinel_model = "gemini-3-pro-preview" 
        self.sentinel_name = "SecuritySentinel"

    async def sanitize_request(self, user_request: str) -> str:
        """
        Uses a separate agent to check for secrets and scope creep.
        Returns a JSON string: {"status": "ALLOWED"|"BLOCKED", "reason": "...", "sanitized_input": "..."}
        """
        sentinel = Agent(
            model=self.sentinel_model,
            name=self.sentinel_name,
            instruction="""
**ROLE**: You are the SECURITY SENTINEL for the CodeCrafter autonomous agent system.
**GOAL**: Protect the system from malicious, accidental, or out-of-scope inputs.

**POLICIES**:
1.  **NO SECRETS**: Look for patterns like `sk-`, `ghp_`, `AWS_SECRET`, or potential passwords.
2.  **SCOPE LIMIT**: CodeCrafter is for "Small, Routine Frontend UI Fixes" only.
    *   BLOCK: "Refactor backend", "Migrate database", "Delete repo", "Arbitrary command execution".
    *   ALLOW: "Change color", "Fix typo", "Update margin", "Add button", "Revert changes", "Update previous PR".

**OUTPUT FORMAT**:
Return a valid JSON object ONLY. Do not include markdown code blocks.
Example:
{
  "status": "ALLOWED",
  "reason": "Routine UI change",
  "sanitized_input": "Change color to blue"
}
{
  "status": "BLOCKED",
  "reason": "Secret detected",
  "sanitized_input": ""
}
"""
        )
        runner = InMemoryRunner(agent=sentinel, app_name="security-check")
        
        # We use a temporary session
        session = await runner.session_service.create_session(
            user_id="sentinel", app_name="security-check"
        )

        response_text = ""
        new_message = Content(role="user", parts=[Part.from_text(text=user_request)])
        
        async for event in runner.run_async(
            user_id="sentinel",
            session_id=session.id,
            new_message=new_message,
        ):
             if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
                        
        await runner.session_service.delete_session(
            app_name="security-check",
            user_id="sentinel",
            session_id=session.id,
        )
        
        # Strip markdown if present
        return response_text.replace("```json", "").replace("```", "").strip()

    async def _run_agent(self, prompt: str, user_id: str = "user", tools_list: list = None) -> str:
        # Pass tools if provided
        agent = Agent(model=self.model_name, name=self.agent_name, tools=tools_list or [])
        runner = InMemoryRunner(agent=agent, app_name="code-crafter")
        
        # Create session
        session = await runner.session_service.create_session(
            user_id=user_id, app_name="code-crafter"
        )

        new_message = Content(role="user", parts=[Part.from_text(text=prompt)])
        
        response_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=new_message,
        ):
            if not event.content:
                continue

            for part in event.content.parts:
                if part.function_call:
                    print(f"  [Agent Logic] Calling Tool: {part.function_call.name}")
                    continue # Skip text access for function calls to avoid warnings
                
                try:
                    if part.text:
                        response_text += part.text
                except Exception:
                    pass
                    
        # Cleanup
        await runner.session_service.delete_session(
            app_name="code-crafter",
            user_id=user_id,
            session_id=session.id,
        )
        
        return response_text.strip()

    def analyze_request(self, email_body, file_structure, context=""):
        prompt = f"""
        You are a generic Frontend Automation Agent. 
        Your goal is to help the Product Team request small, routine code changes.
        
        User Request: {email_body}
        
        Repo Structure:
        {file_structure}
        
        **PROJECT CONTEXT & RULES**:
        {context}
        
        **CRITICAL INSTRUCTION**:
        - Pay strict attention to the *specific component* requested (e.g., if User asks for "Sidebar", do NOT touch "Buttons" or "Header").
        - If the request is ambiguous, default to the most specific matching component filename.
        
        Draft a simple, actionable Implementation Plan. 
        Format:
        1. Summary of Changes
           (High-level description of what will be built/modified)
        
        2. Files to Modify
           (List of files involved)
        
        Keep it concise.
        """
        # Read-only tools for analysis? Maybe list_dir.
        # For now, keep it simple.
        return asyncio.run(self._run_agent(prompt, user_id="planning_agent"))

    def generate_code(self, plan, feedback=""):
        prompt = f"""
        You are a Frontend Coding Assistant. 
        Your task is to execute the following approved plan to fix/update the UI code.
        
        Plan:
        {plan}
        
        User Feedback: {feedback}
        
        **CRITICAL INSTRUCTIONS**:
        1. Use the `read_file` tool to inspect the target file(s) first.
        2. Use the `write_file` tool to apply changes.
        3. When using `write_file`, you MUST provide the **COMPLETE** file content. Do not truncate or use placeholders.
        4. Do not output the code in markdown blocks. Just use the tools.
        5. Return a brief summary of what you modified.
        """
        # Pass read/write tools
        available_tools = [self.tools.read_file, self.tools.write_file, self.tools.list_dir]
        return asyncio.run(self._run_agent(prompt, user_id="coding_agent", tools_list=available_tools))

    def review_code(self, diff: str, context: str = "") -> str:
        """
        Reviews the code changes (diff) for quality issues.
        """
        if not diff:
            return "No changes detected to review."

        prompt = f"""
        You are a Senior Code Reviewer (QA) for CodeCrafter.
        
        Review the following git diff:
        {diff}
        
        **PROJECT CONTEXT & RULES**:
        {context}
        
        Check for:
        1. Syntax errors or obvious bugs.
        2. Security vulnerabilities (secrets, injection).
        3. Code style issues.
        4. Compliance with the Project Context provided above.
        
        Return a concise "Quality Report" in Markdown.
        
        **CRITICAL INSTRUCTION**:
        If you find issues, you MUST include a section "🛠️ Suggested Fixes" with **ready-to-copy Code Snippets** showing exactly how to fix the problem.
        
        If everything looks good, say "LGTM! ✨".
        """
        # Reuse generic agent config but with reviewer persona
        return asyncio.run(self._run_agent(prompt, user_id="qa_agent"))
