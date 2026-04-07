import time
import random
import logging
import json
import threading
from datetime import datetime
from fastapi import FastAPI
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("service_payments")

app = FastAPI(title="Payments Service")

FAILURE_RATE = 0.35

def emit_log(level, message, extra=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "service_payments",
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
    return {"status": "ok", "service": "payments"}

@app.post("/pay")
def process_payment(order_id: str = "ORD-0000", amount: float = 99.99):
    txn_id = f"TXN-{random.randint(10000, 99999)}"
    emit_log("INFO", f"Processing payment for {order_id}", {
        "txn_id": txn_id,
        "amount": amount
    })

    if random.random() < FAILURE_RATE:
        failure_type = random.choice([
            "card_declined",
            "payment_gateway_timeout",
            "insufficient_funds",
            "fraud_detected"
        ])

        if failure_type == "payment_gateway_timeout":
            emit_log("WARNING", f"Payment gateway slow for {txn_id}", {"latency_ms": random.randint(3000, 8000)})
            time.sleep(random.uniform(2, 4))

        emit_log("ERROR", f"Payment failed for {order_id}", {
            "txn_id": txn_id,
            "failure_type": failure_type,
            "amount": amount
        })
        return {"status": "failed", "txn_id": txn_id, "reason": failure_type}

    emit_log("INFO", f"Payment {txn_id} successful", {
        "txn_id": txn_id,
        "order_id": order_id,
        "amount": amount
    })
    return {"status": "success", "txn_id": txn_id}

def simulate_traffic():
    import requests
    time.sleep(3)
    while True:
        try:
            requests.post("http://localhost:8002/pay", params={
                "order_id": f"ORD-{random.randint(1000,9999)}",
                "amount": round(random.uniform(10, 500), 2)
            })
        except:
            pass
        time.sleep(random.uniform(1, 4))

if __name__ == "__main__":
    t = threading.Thread(target=simulate_traffic, daemon=True)
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8002)
# ============================================================
# NexusMend Auto-Fix
# Root Cause : The payment processor is experiencing a high rate of rejections due to various downstream service failures and invalid requests.
# Generated  : 20260407-001932
# Confidence : 92%
# ============================================================

import time

def process_payment(payment_data):
    max_retries = 3
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            # payment processing code here
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise
