# Auto-generated fix for services/service_notifications/notifications.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token is being incorrectly validated or updated, resulting in a mismatch.
# Generated  : 20260407-000743
# Confidence : 92%
# ============================================================

if token := get_push_token(); token and validate_push_token(token):
    send_notification(token)
else:
    update_push_token()
    send_notification(get_push_token())