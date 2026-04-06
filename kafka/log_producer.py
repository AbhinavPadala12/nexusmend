import json
import time
import logging
from datetime import datetime, timezone
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import threading
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log_producer")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

SERVICES = {
    "service_orders":        "http://localhost:8001",
    "service_payments":      "http://localhost:8002",
    "service_auth":          "http://localhost:8003",
    "service_notifications": "http://localhost:8004",
}

TOPICS = [
    "service_orders_logs",
    "service_payments_logs",
    "service_auth_logs",
    "service_notifications_logs",
    "nexusmend_alerts",
]

def create_topics():
    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
    new_topics = [
        NewTopic(topic, num_partitions=1, replication_factor=1)
        for topic in TOPICS
    ]
    futures = admin.create_topics(new_topics)
    for topic, future in futures.items():
        try:
            future.result()
            logger.info(f"Topic created: {topic}")
        except Exception as e:
            logger.info(f"Topic {topic} already exists or error: {e}")

def delivery_report(err, msg):
    if err:
        logger.error(f"Delivery failed: {err}")
    else:
        logger.debug(f"Delivered to {msg.topic()} [{msg.partition()}]")

def produce_log(producer, service_name, log_entry):
    topic = f"{service_name}_logs"
    producer.produce(
        topic,
        key=service_name,
        value=json.dumps(log_entry),
        callback=delivery_report
    )
    producer.poll(0)

def simulate_service_log(service_name):
    import random
    levels = ["INFO", "INFO", "INFO", "WARNING", "ERROR"]
    messages = {
        "service_orders": [
            ("INFO",    "Order ORD-{id} received",           {}),
            ("INFO",    "Order ORD-{id} processed",          {}),
            ("ERROR",   "Order ORD-{id} failed",             {"failure_type": "database_timeout"}),
            ("ERROR",   "Order ORD-{id} failed",             {"failure_type": "inventory_unreachable"}),
            ("WARNING", "Order processing slow",              {"latency_ms": 3200}),
        ],
        "service_payments": [
            ("INFO",    "Payment TXN-{id} processing",       {}),
            ("INFO",    "Payment TXN-{id} successful",       {}),
            ("ERROR",   "Payment TXN-{id} failed",           {"failure_type": "card_declined"}),
            ("ERROR",   "Payment TXN-{id} failed",           {"failure_type": "gateway_timeout"}),
            ("WARNING", "Payment gateway latency high",       {"latency_ms": 5100}),
        ],
        "service_auth": [
            ("INFO",    "Auth attempt for user_{id}",        {}),
            ("INFO",    "Auth successful for user_{id}",     {}),
            ("ERROR",   "Auth failed for user_{id}",         {"failure_type": "token_expired"}),
            ("ERROR",   "Session store unreachable",         {"failure_type": "session_store_down"}),
            ("WARNING", "Rate limit hit for user_{id}",      {"requests_per_min": 450}),
        ],
        "service_notifications": [
            ("INFO",    "Notification NOTIF-{id} sending",   {}),
            ("INFO",    "Notification NOTIF-{id} delivered", {}),
            ("ERROR",   "Notification NOTIF-{id} failed",    {"failure_type": "smtp_server_down"}),
            ("ERROR",   "Notification NOTIF-{id} failed",    {"failure_type": "push_token_invalid"}),
            ("WARNING", "Notification queue filling up",      {"queue_size": 950}),
        ],
    }

    level, message, extra = random.choice(messages[service_name])
    rand_id = random.randint(1000, 9999)
    message = message.replace("{id}", str(rand_id))

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service":   service_name,
        "level":     level,
        "message":   message,
        "extra":     extra
    }

def run_producer():
    logger.info("Waiting for Kafka to be ready...")
    time.sleep(5)

    logger.info("Creating Kafka topics...")
    create_topics()

    producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
    logger.info("Kafka producer started — streaming logs from all services...")

    import random
    while True:
        for service_name in SERVICES.keys():
            log_entry = simulate_service_log(service_name)
            produce_log(producer, service_name, log_entry)

            if log_entry["level"] == "ERROR":
                alert = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "service":   service_name,
                    "alert":     "ERROR detected",
                    "message":   log_entry["message"],
                    "extra":     log_entry["extra"]
                }
                producer.produce(
                    "nexusmend_alerts",
                    key=service_name,
                    value=json.dumps(alert),
                    callback=delivery_report
                )
                producer.poll(0)

        producer.flush()
        time.sleep(random.uniform(0.5, 1.5))

if __name__ == "__main__":
    run_producer()
