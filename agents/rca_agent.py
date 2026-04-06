import json
import logging
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict
from dotenv import load_dotenv
from groq import Groq

sys.path.insert(0, ".")
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rca_agent")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RCA_PROMPT = """
You are an expert Site Reliability Engineer (SRE) and DevOps architect.
You are analyzing failures in a microservices system called NexusMend.

You will be given a list of anomalies detected across services.
Your job is to:
1. Identify the ROOT CAUSE of the failures
2. Explain WHY it is happening in plain English
3. Provide a SPECIFIC CODE FIX
4. Rate your CONFIDENCE (0-100)

Respond ONLY in this exact JSON format:
{
  "root_cause": "one sentence root cause",
  "why": "2-3 sentence plain English explanation",
  "affected_services": ["service1", "service2"],
  "fix_description": "one sentence description of the fix",
  "fix_code": "the actual code fix as a string",
  "fix_filename": "the file to fix e.g. services/service_orders/main.py",
  "confidence": 85,
  "severity": "CRITICAL or HIGH or MEDIUM or LOW"
}
"""

KNOWN_FIXES = {
    "Database connectivity issue": {
        "fix_description": "Add retry logic with exponential backoff for database connections",
        "fix_code": """import time

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
""",
        "fix_filename": "services/service_orders/main.py"
    },
    "Session storage infrastructure failure": {
        "fix_description": "Add Redis connection fallback with in-memory session cache",
        "fix_code": """import redis
from functools import lru_cache

redis_client = None
local_cache = {}

def get_session_store():
    global redis_client
    try:
        if redis_client is None:
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        return redis_client
    except Exception:
        logger.warning("Redis unreachable — falling back to local cache")
        return None

def get_session(session_id: str):
    store = get_session_store()
    if store:
        return store.get(session_id)
    return local_cache.get(session_id)

def set_session(session_id: str, data: dict):
    store = get_session_store()
    if store:
        store.setex(session_id, 3600, json.dumps(data))
    else:
        local_cache[session_id] = data
""",
        "fix_filename": "services/service_auth/main.py"
    },
    "Payment gateway timeout": {
        "fix_description": "Add circuit breaker pattern to prevent cascade failures",
        "fix_code": """import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker OPEN — payment gateway unavailable")

        try:
            result = func(*args, **kwargs)
            self.reset()
            return result
        except Exception as e:
            self.record_failure()
            raise

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker OPENED after {self.failures} failures")

    def reset(self):
        self.failures = 0
        self.state = CircuitState.CLOSED

payment_circuit = CircuitBreaker(failure_threshold=5, timeout=60)
""",
        "fix_filename": "services/service_payments/main.py"
    },
    "Email infrastructure failure": {
        "fix_description": "Add fallback notification channels when SMTP is down",
        "fix_code": """async def send_notification_with_fallback(user_id: str, message: str):
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
""",
        "fix_filename": "services/service_notifications/main.py"
    },
    "Authentication token lifecycle issue": {
        "fix_description": "Add automatic token refresh before expiry",
        "fix_code": """import jwt
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
""",
        "fix_filename": "services/service_auth/main.py"
    }
}

class RCAAgent:
    def __init__(self):
        self.analyses = []

    def analyze(self, anomalies: list) -> dict:
        if not anomalies:
            return {}

        logger.info(f"RCA Agent analyzing {len(anomalies)} anomalies...")

        patterns = list({a.get("pattern", "Unknown") for a in anomalies})
        services = list({a.get("service", "unknown") for a in anomalies})
        primary_pattern = max(
            patterns,
            key=lambda p: sum(1 for a in anomalies if a.get("pattern") == p)
        )

        known_fix = KNOWN_FIXES.get(primary_pattern)

        if known_fix:
            logger.info(f"Known fix found for pattern: {primary_pattern}")
            result = self._build_result(anomalies, primary_pattern, services, known_fix)
        else:
            logger.info(f"Calling Groq AI for unknown pattern: {primary_pattern}")
            result = self._call_groq(anomalies, primary_pattern, services)

        self.analyses.append(result)
        self._print_analysis(result)
        return result

    def _build_result(self, anomalies, pattern, services, known_fix) -> dict:
        return {
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "root_cause":       pattern,
            "why":              f"Multiple services are experiencing {pattern.lower()}. "
                                f"The pattern has been detected {len(anomalies)} times "
                                f"across {len(services)} service(s) in the last 30 seconds.",
            "affected_services": services,
            "fix_description":  known_fix["fix_description"],
            "fix_code":         known_fix["fix_code"],
            "fix_filename":     known_fix["fix_filename"],
            "confidence":       92,
            "severity":         "CRITICAL" if len(anomalies) > 10 else "HIGH",
            "anomaly_count":    len(anomalies),
            "source":           "known_fix_database"
        }

    def _call_groq(self, anomalies, pattern, services) -> dict:
        anomaly_summary = json.dumps({
            "pattern":          pattern,
            "affected_services": services,
            "anomaly_count":    len(anomalies),
            "sample_messages":  [a.get("message") for a in anomalies[:5]],
            "sample_extras":    [a.get("extra") for a in anomalies[:5]]
        }, indent=2)

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": RCA_PROMPT},
                    {"role": "user",   "content": f"Analyze these anomalies:\n{anomaly_summary}"}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            content = response.choices[0].message.content
            result  = json.loads(content)
            result["timestamp"]     = datetime.now(timezone.utc).isoformat()
            result["anomaly_count"] = len(anomalies)
            result["source"]        = "groq_llm"
            return result

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return {
                "timestamp":         datetime.now(timezone.utc).isoformat(),
                "root_cause":        pattern,
                "why":               f"Automated analysis detected {pattern}",
                "affected_services": services,
                "fix_description":   "Manual investigation required",
                "fix_code":          "# TODO: Manual fix needed",
                "fix_filename":      "unknown",
                "confidence":        30,
                "severity":          "HIGH",
                "anomaly_count":     len(anomalies),
                "source":            "fallback"
            }

    def _print_analysis(self, result: dict):
        print("\n" + "🔍 " + "="*58)
        print(f"  ROOT CAUSE ANALYSIS — NexusMend")
        print("="*60)
        print(f"  Severity   : {result.get('severity')}")
        print(f"  Root Cause : {result.get('root_cause')}")
        print(f"  Services   : {result.get('affected_services')}")
        print(f"  Confidence : {result.get('confidence')}%")
        print(f"  Why        : {result.get('why')}")
        print(f"\n  Fix        : {result.get('fix_description')}")
        print(f"  File       : {result.get('fix_filename')}")
        print(f"  Source     : {result.get('source')}")
        print("="*60 + "\n")


if __name__ == "__main__":
    from kafka.log_consumer import consume_logs
    from agents.log_parser import LogParserAgent

    log_parser = LogParserAgent()
    rca_agent  = RCAAgent()

    anomaly_buffer = []
    BUFFER_SIZE    = 10

    def handle_log(log_entry):
        anomaly = log_parser.parse(log_entry)
        if anomaly and anomaly.get("is_critical"):
            anomaly_buffer.append(anomaly)
            if len(anomaly_buffer) >= BUFFER_SIZE:
                rca_agent.analyze(anomaly_buffer.copy())
                anomaly_buffer.clear()

    all_topics = [
        "service_orders_logs",
        "service_payments_logs",
        "service_auth_logs",
        "service_notifications_logs",
    ]

    logger.info("RCA Agent started — analyzing anomalies in real time...")
    consume_logs(all_topics, handle_log, group_id="rca_agent")