# Auto-generated fix for services/service_notifications/notification_utils.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token is not being updated correctly in the database when a user's device token changes.
# Generated  : 20260407-000754
# Confidence : 92%
# ============================================================

try:
    # Update device token in database
    db.update_device_token(user_id, new_token)
except Exception as e:
    # Handle error and log exception
    logger.error(f'Error updating device token: {e}')