# Auto-generated fix for services/service_auth/auth_utils.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token is not being updated correctly when a user's authentication token is refreshed or expires.
# Generated  : 20260407-001430
# Confidence : 92%
# ============================================================

def update_push_token(user_id, new_auth_token):
    # Update push notification token using the new auth token
    push_token = generate_push_token(new_auth_token)
    update_user_push_token(user_id, push_token)
    return push_token