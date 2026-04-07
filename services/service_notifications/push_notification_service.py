# Auto-generated fix for services/service_notifications/push_notification_service.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token validation is failing due to outdated or incorrect tokens being stored in the database.
# Generated  : 20260407-000727
# Confidence : 92%
# ============================================================

def update_push_token(user_id, new_token):
    # Update the token in the database
    db.query(PushToken).filter_by(user_id=user_id).update({'token': new_token})
    return True