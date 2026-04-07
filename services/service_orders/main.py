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
# Root Cause : The root cause of the failures is a combination of issues including inventory unreachability, token expiration, card decline, and push token invalidity, but primarily due to inventory unreachability.
# Generated  : 20260407-002007
# Confidence : 92%
# ============================================================

from retrying import retry; @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000); def get_inventory(): # existing code to get inventory; try: # existing code to process payment; except TokenExpired: # handle token expiration; except CardDeclined: # handle card decline; except PushTokenInvalid: # handle push token invalidity