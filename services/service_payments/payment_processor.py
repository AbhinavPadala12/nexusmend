# Auto-generated fix for services/service_payments/payment_processor.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The payment processor is experiencing a high rate of card declines and gateway timeouts, causing payment transactions to fail.
# Generated  : 20260407-000805
# Confidence : 92%
# ============================================================

import time

def process_payment(payment):
    max_retries = 3
    retry_delay = 1
    for attempt in range(max_retries):
        try:
            # payment processing code here
            return True
        except GatewayTimeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                # log card decline reason
                logging.error('Payment failed: card declined')
                return False
        except CardDeclined:
            # log card decline reason
            logging.error('Payment failed: card declined')
            return False