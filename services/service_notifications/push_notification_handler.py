# Auto-generated fix for services/service_notifications/push_notification_handler.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The push notification token mismatch is caused by an outdated or incorrect push notification token being stored in the database.
# Generated  : 20260407-000738
# Confidence : 92%
# ============================================================

device_token = request.json['device_token']; user_device = UserDevice.query.filter_by(user_id=user_id).first(); user_device.device_token = device_token; db.session.commit()