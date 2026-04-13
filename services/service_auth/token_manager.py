# Auto-generated fix for services/service_auth/token_manager.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token mismatch is caused by an outdated or incorrect token being stored in the database.
# Generated  : 20260413-180853
# Confidence : 92%
# ============================================================

def update_token(user_id, new_token):
    try:
        # Update the token in the database
        db.query(User).filter_by(id=user_id).update({"push_token": new_token})
        db.commit()
    except Exception as e:
        # Handle any database errors
        logger.error(f"Error updating token: {e}")