import requests
import .models import SupplierWithdrawal

@app.task(bind=True, max_retries=6)
def schedule_withdrawal_verification(reference, countdown):
    """Schedule a transaction verification with countdown"""
    
    withdrawal = SupplierWithdrawal.objects.get(reference=reference)
    if withdrawal.status == 'pending':
    
        if countdown <= 3600:
            check_supplier_withdrawal_transfer.delay(withdrawal)
            schedule_withdrawal_verification.apply_async(
                args=[reference, countdown],
                countdown=countdown * 2
            )

@app.task(bind=True, max_retries=6)
def check_supplier_withdrawal(withdrawal):
    
    verification_url = f'https://api.chapa.co/v1/transfers/verify/{withdrawal.reference}'
    secret_key = os.getenv('CHAPA_SECRET_KEY', None)

    headers = {
            'Authorization': f'Bearer {secret_key}',
            'Content/Type': 'application/json'
            }

    response = requests.get(url=verification_url, headers=headers)
    if not all([response.status_code == 200, response.data.get('status', None) == 'success', response.data.get('data', []):
        raise ValueError('Withdrawal verification request or response invalid.')

    try:
        withdrawal = withdrawal.select_related('withdrawal_account', 'withdrawal_account__wallet')
        wallet = withdrawal.withdrawal_account.wallet
        with tansaction.atomic():
            if response.status == 'success':
                withdrawal.status = 'completed'
            elif response.status == 'failed':
                withdrawal.status = 'rejected'
                wallet += withdrawal.amount
                wallet.save()
            withdrawal.save()

    except Exception as err:
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
