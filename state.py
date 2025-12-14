import json
import os
from datetime import datetime

DB_FILE = "db.json"

class StateManager:
    """Simple file-based state management for conversation threads."""
    
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self._load_db()

    def _load_db(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def _save_db(self):
        with open(self.db_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def generate_ticket_id(self):
        """Generates a sequential Ticket ID: TICKET-YYYYMMDD-NNN"""
        today = datetime.now().strftime("%Y%m%d")
        count = 0
        for data in self.data.values():
            t_id = data.get("ticket_id", "")
            if t_id.startswith(f"TICKET-{today}-"):
                try:
                    current_count = int(t_id.split("-")[-1])
                    if current_count > count:
                        count = current_count
                except:
                    pass
        return f"TICKET-{today}-{count + 1:03d}"

    def get_state(self, thread_id):
        return self.data.get(thread_id, {}).get("state", "NEW")

    def get_plan(self, thread_id):
        return self.data.get(thread_id, {}).get("plan")

    def update_state(self, thread_id, state, plan=None, extra_data=None):
        if thread_id not in self.data:
            self.data[thread_id] = {"created_at": datetime.now().isoformat()}
        
        self.data[thread_id]["state"] = state
        self.data[thread_id]["updated_at"] = datetime.now().isoformat()
        
        if plan:
            self.data[thread_id]["plan"] = plan
        
        if extra_data:
            self.data[thread_id].update(extra_data)
            
        self._save_db()

    def get_thread_data(self, thread_id):
        """Returns the full data dict for a thread."""
        return self.data.get(thread_id, {})

    def find_thread_id_by_subject(self, subject):
        """Fuzzy lookup for thread ID by matching subject (ignoring Re:)."""
        clean_subj = subject.replace("Re:", "").replace("Fwd:", "").strip()
        for t_id, data in self.data.items():
            data_subj = data.get("title", "").replace("Re:", "").replace("Fwd:", "").strip()
            # Simple substring or exact match
            if clean_subj and (clean_subj in data_subj or data_subj in clean_subj):
                # Return if not completed/blocked? Or just return match.
                # Prioritize active threads
                if data.get("state") not in ["COMPLETED", "BLOCKED"]:
                    return t_id
        return None