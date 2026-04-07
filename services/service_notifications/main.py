import time
import random
import logging
import json
import threading
from datetime import datetime
from fastapi import FastAPI
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("service_notifications")

app = FastAPI(title="Notifications Service")

FAILURE_RATE = 0.3

CHANNELS = ["email", "sms", "push", "webhook"]

def emit_log(level, message, extra=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "service_notifications",
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
    return {"status": "ok", "service": "notifications"}

@app.post("/notify")
def send_notification(user_id: str = "user_001", message: str = "Your order is confirmed"):
    notif_id = f"NOTIF-{random.randint(10000, 99999)}"
    channel = random.choice(CHANNELS)

    emit_log("INFO", f"Sending notification {notif_id} via {channel}", {
        "notif_id": notif_id,
        "user_id": user_id,
        "channel": channel
    })

    if random.random() < FAILURE_RATE:
        failure_type = random.choice([
            "smtp_server_down",
            "sms_gateway_timeout",
            "push_token_invalid",
            "webhook_unreachable",
            "queue_overflow"
        ])

        if failure_type == "queue_overflow":
            emit_log("WARNING", f"Notification queue is filling up", {
                "queue_size": random.randint(800, 1000),
                "max_size": 1000
            })

        if failure_type == "smtp_server_down":
            emit_log("ERROR", "SMTP server unreachable — email notifications blocked", {
                "notif_id": notif_id,
                "smtp_host": "mail.nexusmend.internal",
                "retry_count": random.randint(1, 5)
            })

        emit_log("ERROR", f"Notification {notif_id} failed", {
            "notif_id": notif_id,
            "failure_type": failure_type,
            "channel": channel,
            "user_id": user_id
        })
        return {"status": "failed", "notif_id": notif_id, "reason": failure_type}

    time.sleep(random.uniform(0.1, 0.5))
    emit_log("INFO", f"Notification {notif_id} delivered successfully", {
        "notif_id": notif_id,
        "channel": channel,
        "user_id": user_id
    })
    return {"status": "success", "notif_id": notif_id, "channel": channel}

def simulate_traffic():
    import requests
    time.sleep(3)
    while True:
        try:
            requests.post("http://localhost:8004/notify", params={
                "user_id": f"user_00{random.randint(1,5)}",
                "message": random.choice([
                    "Your order is confirmed",
                    "Payment received",
                    "Your session expires soon",
                    "New login detected"
                ])
            })
        except:
            pass
        time.sleep(random.uniform(0.5, 3))

if __name__ == "__main__":
    t = threading.Thread(target=simulate_traffic, daemon=True)
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8004)
# ============================================================
# NexusMend Auto-Fix
# Root Cause : Email infrastructure failure
# Generated  : 20260407-001424
# Confidence : 92%
# ============================================================

async def send_notification_with_fallback(user_id: str, message: str):
    channels = ["email", "sms", "push"]

    for channel in channels:
        try:
            if channel == "email":
                result = await send_email(user_id, message)
            elif channel == "sms":
                result = await send_sms(user_id, message)
            elif channel == "push":
                result = await send_push(user_id, message)

            logger.info(f"Notification sent via fallback channel: {channel}")
            return {"status": "success", "channel": channel}

        except Exception as e:
            logger.warning(f"Channel {channel} failed: {e}, trying next...")
            continue

    logger.error("All notification channels failed")
    return {"status": "failed", "reason": "all_channels_exhausted"}
