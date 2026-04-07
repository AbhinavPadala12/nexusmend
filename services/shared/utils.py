# Auto-generated fix for services/shared/utils.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The root cause of the failures is a combination of issues with upstream service dependencies, including invalid push tokens, unreachable inventory services, expired tokens, and gateway timeouts.
# Generated  : 20260407-001956
# Confidence : 92%
# ============================================================

from tenacity import retry, stop_after_attempt, wait_exponential

def call_upstream_service(func):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper