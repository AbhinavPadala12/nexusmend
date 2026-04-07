# Auto-generated fix for services/service_orders/inventory_client.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The inventory service is unreachable, causing a cascade failure in the service_orders service
# Generated  : 20260407-000857
# Confidence : 92%
# ============================================================

from tenacity import retry, wait_exponential, stop_after_attempt

class InventoryClient:
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def get_inventory(self, item_id):
        # existing code to call inventory service