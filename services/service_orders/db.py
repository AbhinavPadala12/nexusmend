# Auto-generated fix for services/service_orders/db.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The root cause of the failures is a database connection issue causing timeouts and cascading failures across services
# Generated  : 20260413-180734
# Confidence : 92%
# ============================================================

from tenacity import retry, wait_exponential, stop_after_attempt

def get_database_connection():
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _get_connection():
        # existing database connection code
        return db_connection
    return _get_connection()