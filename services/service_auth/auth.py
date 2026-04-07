# Auto-generated fix for services/service_auth/auth.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The authentication service's token expiration and invalidation mechanism is not properly synchronized with dependent services, causing upstream dependency failures.
# Generated  : 20260407-001420
# Confidence : 92%
# ============================================================

TOKEN_LIFETIME = 3600  # increase token lifetime to 1 hour
TOKEN_REFRESH_THRESHOLD = 300  # refresh token 5 minutes before expiration