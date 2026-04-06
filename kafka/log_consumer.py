import json
import logging
from confluent_kafka import Consumer, KafkaException
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("log_consumer")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

def create_consumer(group_id="nexusmend_agents"):
    return Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id":          group_id,
        "auto.offset.reset": "earliest",
    })

def consume_logs(topics, handler, group_id="nexusmend_agents"):
    consumer = create_consumer(group_id)
    consumer.subscribe(topics)
    logger.info(f"Consuming from topics: {topics}")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            log_entry = json.loads(msg.value().decode("utf-8"))
            handler(log_entry)

    except KeyboardInterrupt:
        logger.info("Consumer stopped.")
    finally:
        consumer.close()

def print_handler(log_entry):
    level   = log_entry.get("level", "INFO")
    service = log_entry.get("service", "unknown")
    message = log_entry.get("message", "")

    if level == "ERROR":
        logger.error(f"[{service}] {message}")
    elif level == "WARNING":
        logger.warning(f"[{service}] {message}")
    else:
        logger.info(f"[{service}] {message}")

if __name__ == "__main__":
    all_topics = [
        "service_orders_logs",
        "service_payments_logs",
        "service_auth_logs",
        "service_notifications_logs",
        "nexusmend_alerts",
    ]
    consume_logs(all_topics, print_handler)
    