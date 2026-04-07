# Auto-generated fix for services/service_payments/payment_processor.py

# ============================================================
# NexusMend Auto-Fix
# Root Cause : The payment processor is experiencing gateway timeouts and card declines due to insufficient retry mechanisms and lack of card validation
# Generated  : 20260407-000824
# Confidence : 92%
# ============================================================

import time

def process_payment(card_info, retry_count=3, backoff_factor=1):
    for i in range(retry_count):
        try:
            # Process payment using payment gateway
            payment_gateway.process_payment(card_info)
            return True
        except GatewayTimeout:
            if i < retry_count - 1:
                time.sleep(backoff_factor * (2 ** i))
            else:
                raise
        except CardDeclined:
            # Perform card validation checks
            if not validate_card(card_info):
                raise
            # If card is valid, retry payment processing
            if i < retry_count - 1:
                time.sleep(backoff_factor * (2 ** i))
            else:
                raise
    return False