# Auto-generated fix for services/service_notifications/notifications.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token mismatch is caused by a missing token validation step in the service_notifications service.
# Generated  : 20260413-180728
# Confidence : 92%
# ============================================================

if not validate_push_token(token): raise InvalidTokenError('Invalid push notification token')