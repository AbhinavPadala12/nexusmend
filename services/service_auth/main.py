import time
import random
import logging
import json
import threading
from datetime import datetime
from fastapi import FastAPI
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("service_auth")

app = FastAPI(title="Auth Service")

FAILURE_RATE = 0.25

VALID_USERS = ["user_001", "user_002", "user_003", "user_004", "user_005"]

def emit_log(level, message, extra=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "service_auth",
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
    return {"status": "ok", "service": "auth"}

@app.post("/authenticate")
def authenticate(user_id: str = "user_001", token: str = "abc123"):
    session_id = f"SES-{random.randint(100000, 999999)}"
    emit_log("INFO", f"Authentication attempt for {user_id}", {
        "session_id": session_id,
        "user_id": user_id
    })

    if user_id not in VALID_USERS:
        emit_log("WARNING", f"Unknown user attempted login: {user_id}", {
            "session_id": session_id,
            "user_id": user_id
        })
        return {"status": "failed", "reason": "unknown_user"}

    if random.random() < FAILURE_RATE:
        failure_type = random.choice([
            "token_expired",
            "token_invalid",
            "session_store_unreachable",
            "rate_limit_exceeded",
            "mfa_failed"
        ])

        if failure_type == "session_store_unreachable":
            emit_log("ERROR", "Session store is down — cannot validate tokens", {
                "session_id": session_id,
                "affected_service": "redis"
            })
        elif failure_type == "rate_limit_exceeded":
            emit_log("WARNING", f"Rate limit hit for {user_id}", {
                "session_id": session_id,
                "requests_per_minute": random.randint(100, 500)
            })

        emit_log("ERROR", f"Authentication failed for {user_id}", {
            "session_id": session_id,
            "failure_type": failure_type,
            "user_id": user_id
        })
        return {"status": "failed", "session_id": session_id, "reason": failure_type}

    emit_log("INFO", f"Authentication successful for {user_id}", {
        "session_id": session_id,
        "user_id": user_id
    })
    return {"status": "success", "session_id": session_id}

def simulate_traffic():
    import requests
    time.sleep(3)
    while True:
        try:
            user = random.choice(VALID_USERS + ["hacker_001", "unknown_999"])
            requests.post("http://localhost:8003/authenticate", params={
                "user_id": user,
                "token": f"tok_{random.randint(1000,9999)}"
            })
        except:
            pass
        time.sleep(random.uniform(0.5, 2))

if __name__ == "__main__":
    t = threading.Thread(target=simulate_traffic, daemon=True)
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8003)
# ============================================================
# NexusMend Auto-Fix
# Root Cause : Authentication token lifecycle issue
# Generated  : 20260413-180634
# Confidence : 92%
# ============================================================

import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = os.getenv("JWT_SECRET", "nexusmend-secret")

def create_token(user_id: str, expires_in_minutes: int = 60) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validate_and_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        time_left = (exp - datetime.now(timezone.utc)).total_seconds()

        if time_left < 300:
            new_token = create_token(payload["user_id"])
            return {"valid": True, "refreshed": True, "new_token": new_token}

        return {"valid": True, "refreshed": False}

    except jwt.ExpiredSignatureError:
        return {"valid": False, "reason": "token_expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "reason": "token_invalid"}
