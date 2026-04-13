# Auto-generated fix for services/service_auth/session_store.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The session store is unreachable, causing push notification token mismatches and authentication failures across services.
# Generated  : 20260413-195351
# Confidence : 92%
# ============================================================

import time
import random

def get_session_store():
    retry_count = 0
    while retry_count < 5:
        try:
            # Attempt to connect to primary session store
            return primary_session_store
        except Exception as e:
            retry_count += 1
            time.sleep(2**retry_count + random.uniform(0, 1))
            if retry_count == 5:
                # Fallback to secondary session store if available
                return secondary_session_store if secondary_session_store else None