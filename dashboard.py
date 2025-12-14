import json
import os
from datetime import datetime

class DashboardLogger:
    def __init__(self, log_file="dashboard_log.json"):
        self.log_file = log_file

    def _load_log(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def log_ticket(self, entry_data):
        """
        Logs or updates a ticket in the dashboard.
        Fields kept: ticket_id, title, requested_by, status, timestamps, pr_url.
        Removed: ref_ticket, plan, diff_summary, qa_report.
        """
        logs = self._load_log()
        
        ticket_id = entry_data.get("ticket_id")
        if not ticket_id:
            print("  [Dashboard] Warning: No ticket_id provided, skipping log.")
            return

        # Find existing entry
        existing_entry = next((item for item in logs if item.get("ticket_id") == ticket_id), None)
        
        current_dt = datetime.now()
        
        # Parse created_at if provided, else current
        created_iso = entry_data.get("created_at", current_dt.isoformat())
        try:
            c_dt = datetime.fromisoformat(created_iso)
            c_date = c_dt.strftime("%Y-%m-%d")
            c_time = c_dt.strftime("%H:%M:%S")
        except:
            c_date = created_iso
            c_time = ""

        if existing_entry:
            # UPDATE existing
            existing_entry["status"] = entry_data.get("status", existing_entry["status"])
            existing_entry["completed_date"] = current_dt.strftime("%Y-%m-%d")
            existing_entry["completed_time"] = current_dt.strftime("%H:%M:%S")
            if "pr_url" in entry_data:
                existing_entry["pr_url"] = entry_data["pr_url"]
            print(f"  [Dashboard] Updated Ticket {ticket_id} to {entry_data.get('status')}")
            
        else:
            # CREATE new
            new_record = {
                "id": len(logs) + 1, # Internal ID
                "ticket_id": ticket_id,
                "title": entry_data.get("title"),
                "requested_by": entry_data.get("requested_by"),
                "created_date": c_date,
                "created_time": c_time,
                "status": entry_data.get("status", "NEW"),
                "pr_url": entry_data.get("pr_url", "")
            }
            logs.append(new_record)
            print(f"  [Dashboard] logged New Ticket {ticket_id}")

        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)
            
        return ticket_id
