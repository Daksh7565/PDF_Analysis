import json
import os
from datetime import datetime
from typing import Dict, Any
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class AnalyticsLogger:
    def __init__(self):
        self.log_file = os.path.join(Config.LOG_DIR, f"queries_{datetime.now().strftime('%Y%m')}.jsonl")
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs(Config.LOG_DIR, exist_ok=True)
    
    def log_query(self, query: str, response: Dict, metadata: Dict[str, Any]):
        """Log query and response for analysis"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "query": query,
            "response": response,
            "metadata": metadata
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_analytics(self) -> Dict:
        """Generate analytics from logs"""
        if not os.path.exists(self.log_file):
            return {}
        
        stats = {
            "total_queries": 0,
            "queries_today": 0,
            "common_pdfs": {},
            "feedback_distribution": {"thumbs_up": 0, "thumbs_down": 0}
        }
        
        today = datetime.now().date()
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    stats["total_queries"] += 1
                    
                    entry_date = datetime.fromisoformat(entry["timestamp"]).date()
                    if entry_date == today:
                        stats["queries_today"] += 1
                    
                    for pdf in entry["metadata"].get("pdf_names", []):
                        stats["common_pdfs"][pdf] = stats["common_pdfs"].get(pdf, 0) + 1
                    
                    feedback = entry["metadata"].get("user_feedback")
                    if feedback == "up":
                        stats["feedback_distribution"]["thumbs_up"] += 1
                    elif feedback == "down":
                        stats["feedback_distribution"]["thumbs_down"] += 1
        except Exception as e:
            print(f"Error reading analytics: {e}")
        
        return stats