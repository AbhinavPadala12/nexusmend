import time
import random
import logging
import json
from datetime import datetime
from fastapi import FastAPI
import uvicorn
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("service_orders")

app = FastAPI(title="Orders Service")

FAILURE_RATE = 0.3

def emit_log(level, message, extra=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "service_orders",
        "level": level,
        "message": message,
        "extra": extra or {}
    }
    print(json.dumps(log_entry))
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

@app.get("/health")
def health():
    return {"status": "ok", "service": "orders"}

@app.post("/order")
def create_order(item: str = "laptop", quantity: int = 1):
    order_id = f"ORD-{random.randint(1000,9999)}"
    emit_log("INFO", f"Received order {order_id}", {"item": item, "quantity": quantity})

    if random.random() < FAILURE_RATE:
        failure_type = random.choice([
            "database_timeout",
            "inventory_service_unreachable",
            "payment_validation_failed"
        ])
        emit_log("ERROR", f"Order {order_id} failed", {
            "order_id": order_id,
            "failure_type": failure_type,
            "item": item
        })
        return {"status": "failed", "order_id": order_id, "reason": failure_type}

    emit_log("INFO", f"Order {order_id} processed successfully", {"order_id": order_id})
    return {"status": "success", "order_id": order_id}

def simulate_traffic():
    import requests
    time.sleep(3)
    while True:
        try:
            requests.post("http://localhost:8001/order", params={"item": random.choice(["laptop","phone","tablet"]), "quantity": random.randint(1,5)})
        except:
            pass
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    t = threading.Thread(target=simulate_traffic, daemon=True)
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8001)
# ============================================================
# NexusMend Auto-Fix
# Root Cause : Database connectivity issue
# Generated  : 20260413-181143
# Confidence : 92%
# ============================================================

import time

def connect_with_retry(max_retries=3, backoff=2):
    for attempt in range(max_retries):
        try:
            # Replace with your actual DB connection
            connection = create_db_connection()
            return connection
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = backoff ** attempt
            logger.warning(f"DB connection failed, retrying in {wait}s...")
            time.sleep(wait)
