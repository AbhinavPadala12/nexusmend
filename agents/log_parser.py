import json
import logging
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict
from dotenv import load_dotenv

sys.path.insert(0, ".")

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log_parser")

ERROR_THRESHOLD = 3
TIME_WINDOW_SECONDS = 30

class LogParserAgent:
    def __init__(self):
        self.error_counts = defaultdict(list)
        self.anomalies = []

    def parse(self, log_entry: dict) -> dict | None:
        service = log_entry.get("service", "unknown")
        level   = log_entry.get("level", "INFO")
        message = log_entry.get("message", "")
        extra   = log_entry.get("extra", {})
        now     = datetime.now(timezone.utc)

        if level == "ERROR":
            self.error_counts[service].append(now)
            self.error_counts[service] = [
                t for t in self.error_counts[service]
                if (now - t).total_seconds() < TIME_WINDOW_SECONDS
            ]
            error_count = len(self.error_counts[service])

            anomaly = {
                "timestamp":   now.isoformat(),
                "service":     service,
                "level":       level,
                "message":     message,
                "extra":       extra,
                "error_count": error_count,
                "is_critical": error_count >= ERROR_THRESHOLD,
                "pattern":     self._detect_pattern(service, message, extra)
            }

            if error_count >= ERROR_THRESHOLD:
                logger.warning(
                    f"ANOMALY DETECTED in {service} — "
                    f"{error_count} errors in {TIME_WINDOW_SECONDS}s | "
                    f"Pattern: {anomaly['pattern']}"
                )

            self.anomalies.append(anomaly)
            return anomaly

        elif level == "WARNING":
            logger.info(f"[WARNING] {service}: {message}")

        return None

    def _detect_pattern(self, service: str, message: str, extra: dict) -> str:
        failure_type = extra.get("failure_type", "")

        patterns = {
            "database_timeout":       "Database connectivity issue",
            "inventory_unreachable":  "Upstream service dependency failure",
            "card_declined":          "Payment processor rejection",
            "gateway_timeout":        "Payment gateway timeout",
            "token_expired":          "Authentication token lifecycle issue",
            "session_store_down":     "Session storage infrastructure failure",
            "smtp_server_down":       "Email infrastructure failure",
            "push_token_invalid":     "Push notification token mismatch",
            "queue_overflow":         "Message queue capacity issue",
        }

        if failure_type in patterns:
            return patterns[failure_type]

        if "timeout" in message.lower():
            return "Timeout pattern detected"
        if "unreachable" in message.lower():
            return "Service unreachability pattern"
        if "failed" in message.lower():
            return "General failure pattern"

        return "Unknown pattern"

    def get_anomaly_summary(self) -> dict:
        critical = [a for a in self.anomalies if a.get("is_critical")]
        return {
            "total_anomalies":    len(self.anomalies),
            "critical_anomalies": len(critical),
            "services_affected":  list({a["service"] for a in critical}),
            "top_patterns":       self._top_patterns()
        }

    def _top_patterns(self) -> list:
        pattern_counts = defaultdict(int)
        for a in self.anomalies:
            pattern_counts[a.get("pattern", "Unknown")] += 1
        sorted_patterns = sorted(
            pattern_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [{"pattern": p, "count": c} for p, c in sorted_patterns[:5]]


if __name__ == "__main__":
    from kafka.log_consumer import consume_logs

    agent = LogParserAgent()

    def handle_log(log_entry):
        anomaly = agent.parse(log_entry)
        if anomaly and anomaly.get("is_critical"):
            print("\n" + "="*60)
            print(f"CRITICAL ANOMALY DETECTED")
            print(f"Service  : {anomaly['service']}")
            print(f"Pattern  : {anomaly['pattern']}")
            print(f"Errors   : {anomaly['error_count']} in 30s")
            print(f"Message  : {anomaly['message']}")
            print("="*60 + "\n")

    all_topics = [
        "service_orders_logs",
        "service_payments_logs",
        "service_auth_logs",
        "service_notifications_logs",
    ]

    logger.info("Log Parser Agent started — watching all services...")
    consume_logs(all_topics, handle_log, group_id="log_parser_agent")