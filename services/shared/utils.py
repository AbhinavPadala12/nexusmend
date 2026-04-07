# Auto-generated fix for services/shared/utils.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The upstream service dependency failure is caused by a faulty implementation of circuit breakers and retries in the services.
# Generated  : 20260407-002205
# Confidence : 92%
# ============================================================

from tenacity import retry, wait_exponential, stop_after_attempt

def call_upstream_service(func):
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper