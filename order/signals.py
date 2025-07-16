from django.dispatch import Signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Transaction
from .tasks import record_supplier_earnings


@receiver(post_save, sender=Transaction)
def transaction_status_change(sender, instance, created, **kwargs):
    if instance.status == 'success':  # Only for updates, not new instances
        # Send email to customer
        print('signal sent for success.')
        subject = 'Payment Successful'
        message = f'Your payment for transaction {instance.tx_ref} has been successfully processed.'
        from_email = 'bekelebrook@gmail.com'  # Replace with your email
        recipient_list = [instance.order.user.email]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        # Record supplier earnings and notify them
        record_supplier_earnings.delay(instance.id)
