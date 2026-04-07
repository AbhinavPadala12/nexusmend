import time
import random
import logging
import json
import sys
import os
import requests
import threading
from datetime import datetime, timezone
from dotenv import load_dotenv

sys.path.insert(0, ".")
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chaos_engine")

SERVICES = {
    "service_orders":        "http://localhost:8001",
    "service_payments":      "http://localhost:8002",
    "service_auth":          "http://localhost:8003",
    "service_notifications": "http://localhost:8004",
}

CHAOS_SCENARIOS = [
    {
        "name":        "database_overload",
        "description": "Flood orders service with requests to simulate DB overload",
        "severity":    "CRITICAL",
        "target":      "service_orders",
        "duration":    15,
    },
    {
        "name":        "payment_gateway_storm",
        "description": "Hammer payments service to trigger gateway timeouts",
        "severity":    "HIGH",
        "target":      "service_payments",
        "duration":    15,
    },
    {
        "name":        "auth_token_flood",
        "description": "Flood auth with invalid tokens to trigger rate limiting",
        "severity":    "HIGH",
        "target":      "service_auth",
        "duration":    10,
    },
    {
        "name":        "notification_queue_overflow",
        "description": "Overwhelm notification service to trigger queue overflow",
        "severity":    "CRITICAL",
        "target":      "service_notifications",
        "duration":    10,
    },
    {
        "name":        "cascading_failure",
        "description": "Attack all services simultaneously to trigger cascade",
        "severity":    "CRITICAL",
        "target":      "all",
        "duration":    20,
    },
]


class ChaosEngine:
    def __init__(self):
        self.active         = False
        self.scenarios_run  = []
        self.current_scenario = None

    def run_scenario(self, scenario: dict):
        self.current_scenario = scenario
        name        = scenario["name"]
        description = scenario["description"]
        severity    = scenario["severity"]
        target      = scenario["target"]
        duration    = scenario["duration"]

        self._print_chaos_start(scenario)

        start_time = time.time()
        threads    = []

        if target == "all":
            for svc_name, svc_url in SERVICES.items():
                t = threading.Thread(
                    target=self._flood_service,
                    args=(svc_name, svc_url, duration),
                    daemon=True
                )
                threads.append(t)
                t.start()
        else:
            svc_url = SERVICES.get(target)
            if svc_url:
                t = threading.Thread(
                    target=self._flood_service,
                    args=(target, svc_url, duration),
                    daemon=True
                )
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        elapsed = round(time.time() - start_time, 2)
        self.scenarios_run.append({
            "scenario":  name,
            "severity":  severity,
            "target":    target,
            "duration":  elapsed,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        self._print_chaos_end(scenario, elapsed)
        self.current_scenario = None

    def _flood_service(self, svc_name: str, svc_url: str, duration: int):
        end_time   = time.time() + duration
        request_count = 0

        endpoints = {
            "service_orders": (
                "POST", f"{svc_url}/order",
                {"item": "chaos_item", "quantity": 999}
            ),
            "service_payments": (
                "POST", f"{svc_url}/pay",
                {"order_id": "CHAOS-0000", "amount": 99999.99}
            ),
            "service_auth": (
                "POST", f"{svc_url}/authenticate",
                {"user_id": "chaos_attacker", "token": "invalid_chaos_token"}
            ),
            "service_notifications": (
                "POST", f"{svc_url}/notify",
                {"user_id": "chaos_user", "message": "CHAOS " * 100}
            ),
        }

        method, url, params = endpoints.get(
            svc_name,
            ("GET", f"{svc_url}/health", {})
        )

        while time.time() < end_time:
            try:
                if method == "POST":
                    requests.post(url, params=params, timeout=2)
                else:
                    requests.get(url, timeout=2)
                request_count += 1
            except Exception:
                pass
            time.sleep(0.05)

        logger.info(
            f"Chaos flooded {svc_name} with "
            f"{request_count} requests in {duration}s"
        )

    def _print_chaos_start(self, scenario: dict):
        print("\n" + "💥 " + "="*57)
        print(f"  CHAOS ENGINE ACTIVATED")
        print("="*60)
        print(f"  Scenario : {scenario['name']}")
        print(f"  Target   : {scenario['target']}")
        print(f"  Severity : {scenario['severity']}")
        print(f"  Duration : {scenario['duration']}s")
        print(f"  Attack   : {scenario['description']}")
        print("="*60)

    def _print_chaos_end(self, scenario: dict, elapsed: float):
        print("\n" + "✅ " + "="*57)
        print(f"  CHAOS SCENARIO COMPLETE")
        print("="*60)
        print(f"  Scenario : {scenario['name']}")
        print(f"  Duration : {elapsed}s")
        print(f"  Waiting for NexusMend to detect and fix...")
        print("="*60 + "\n")

    def run_random_scenario(self):
        scenario = random.choice(CHAOS_SCENARIOS)
        self.run_scenario(scenario)

    def run_all_scenarios(self, delay_between: int = 30):
        logger.info(f"Running all {len(CHAOS_SCENARIOS)} chaos scenarios...")
        for i, scenario in enumerate(CHAOS_SCENARIOS):
            logger.info(
                f"Scenario {i+1}/{len(CHAOS_SCENARIOS)}: "
                f"{scenario['name']}"
            )
            self.run_scenario(scenario)
            if i < len(CHAOS_SCENARIOS) - 1:
                logger.info(f"Waiting {delay_between}s before next scenario...")
                time.sleep(delay_between)

        logger.info("All chaos scenarios complete!")
        self._print_summary()

    def _print_summary(self):
        print("\n" + "📊 " + "="*57)
        print(f"  CHAOS ENGINE SUMMARY")
        print("="*60)
        print(f"  Total scenarios run : {len(self.scenarios_run)}")
        for s in self.scenarios_run:
            print(
                f"  {s['scenario']:<35} "
                f"{s['severity']:<10} "
                f"{s['duration']}s"
            )
        print("="*60 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NexusMend Chaos Engine")
    parser.add_argument(
        "--mode",
        choices=["random", "all", "single"],
        default="random",
        help="Chaos mode"
    )
    parser.add_argument(
        "--scenario",
        type=int,
        default=0,
        help="Scenario index for single mode (0-4)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=30,
        help="Delay between scenarios in seconds"
    )
    args = parser.parse_args()

    engine = ChaosEngine()

    print("\n" + "="*60)
    print("  NEXUSMEND CHAOS ENGINE")
    print("  Deliberately breaking services to test AI healing...")
    print("="*60)
    print("\nAvailable scenarios:")
    for i, s in enumerate(CHAOS_SCENARIOS):
        print(f"  {i}. {s['name']:<35} [{s['severity']}]")
    print()

    if args.mode == "random":
        engine.run_random_scenario()
    elif args.mode == "all":
        engine.run_all_scenarios(delay_between=args.delay)
    elif args.mode == "single":
        if 0 <= args.scenario < len(CHAOS_SCENARIOS):
            engine.run_scenario(CHAOS_SCENARIOS[args.scenario])
        else:
            print(f"Invalid scenario index. Choose 0-{len(CHAOS_SCENARIOS)-1}")