import json
import os
from datetime import datetime


LOG_PATH = "logs/prediction_logs.jsonl"


def save_prediction_log(data):
    os.makedirs("logs", exist_ok=True)

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": data.get("user_id"),
        "financial_status": data.get("financial_status"),
        "rule_status": data.get("rule_status"),
        "model_status": data.get("model_status"),
        "recommendation_method": data.get("recommendation_method"),
        "model_confidence": data.get("model_confidence"),
        "summary": data.get("summary")
    }

    with open(LOG_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(log_data, ensure_ascii=False) + "\n")