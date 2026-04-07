# Auto-generated fix for services/service_payments/payment_processor.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The payment processor is rejecting transactions due to a combination of card declines and gateway timeouts.
# Generated  : 20260407-000815
# Confidence : 92%
# ============================================================

import time

def process_payment(payment):
    retry_count = 0
    while retry_count < 3:
        try:
            # Call payment processor API
            response = payment_processor_api(payment)
            if response.status_code == 200:
                return response
            elif response.status_code == 504: # Gateway timeout
                retry_count += 1
                time.sleep(2 ** retry_count)
            else:
                # Handle card declines
                if response.json()['failure_type'] == 'card_declined':
                    return {'error': 'Card declined. Please check your card details.'}
                else:
                    return {'error': 'Payment failed. Please try again.'}
        except Exception as e:
            return {'error': str(e)}