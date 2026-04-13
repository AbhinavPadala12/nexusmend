# Auto-generated fix for services/service_auth/token_manager.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token mismatch is caused by an outdated or invalid token being used across multiple services.
# Generated  : 20260413-181041
# Confidence : 92%
# ============================================================

def update_push_token(user_id, new_token):
    # Update the token in the database
    db.update_push_token(user_id, new_token)
    # Notify all services of the token update
    notify_services(user_id, new_token)
    return True