# Auto-generated fix for services/service_auth/session_store.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The session store service is down, causing a cascade of failures across dependent services
# Generated  : 20260413-180914
# Confidence : 92%
# ============================================================

session_store = redis.Redis(host='session-store-primary', port=6379, socket_timeout=5)
try:
    session_store.ping()
except redis.exceptions.ConnectionError:
    session_store = redis.Redis(host='session-store-secondary', port=6379, socket_timeout=5)