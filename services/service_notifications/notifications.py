# Auto-generated fix for services/service_notifications/notifications.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token mismatch is caused by an invalid or outdated token being used to send notifications.
# Generated  : 20260407-000732
# Confidence : 92%
# ============================================================

def update_push_token(user_id, new_token):
    # Validate the new token
    if not validate_token(new_token):
        raise ValueError('Invalid push token')
    # Update the token in the database
    db.update_push_token(user_id, new_token)
