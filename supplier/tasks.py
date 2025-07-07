import requests



@app.task(bind=True, max_retries=6)
def schedule_transfer_verification(reference, countdown):
    """Schedule a transaction verification with countdown"""
    
    transaction = Transaction.objects.get(tx_ref=tx_ref)
    if transaction.status == 'pending':
    
        if countdown <= 2400:
            check_supplier_withdrawal_transfer.delay(reference=reference)
            schedule_transaction_verification.apply_async(
                args=[tx_ref, countdown],
                countdown=countdown * 2
            )

@app.task(bind=True, max_retries=6)
def check_supplier_withdrawal_transfer(reference):
    
    verification_url = f'https://api.chapa.co/v1/transfers/verify/{reference}'
    secret_key = os.getenv('CHAPA_SECRET_KEY', None)

    headers = {
            'Authorization': f'Bearer {secret_key}',
            'Content/Type': 'application/json'
            }

    response = requests.get(url=verification_url, headers=headers)

    # add signals to send notifications and decrease wallet balance
    # if failed do the same
