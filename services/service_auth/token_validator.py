# Auto-generated fix for services/service_auth/token_validator.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token mismatch is caused by a faulty token validation mechanism in the service_auth service.
# Generated  : 20260407-002146
# Confidence : 92%
# ============================================================

if token := validate_push_token(token); token.is_valid():
    return token
else:
    raise InvalidTokenError('Push token is invalid')