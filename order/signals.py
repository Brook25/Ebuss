from django.dispatch import Signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Transaction
from .tasks import record_supplier_earnings
from user.models import Notification

@receiver(post_save, sender=Transaction)
def transaction_status_change(sender, instance, created, **kwargs):

    if instance.status != 'pending': 
        notification_data = {
            'user': instance.order.user,
            'type': 'order_status',
            'uri': 'http://localhost/nots/1',
            'priority': 'high'
            }
    
    if instance.status == 'success':  # Only for updates, not new instances
        # Send email to customer
        subject = 'Payment Successful'
        message = f'Your payment for transaction {instance.tx_ref} has been successfully processed.'
        from_email = 'bekelebrook24@gmail.com'  # Replace with your email
        recipient_list = ['brook24bek@gmail.com']
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        notification_data['note'] =  f'Transaction with id {instance.pk} is successful. Order is in progress for delivery.'
        Notification.objects.create(**notification_data)
        # Record supplier earnings and notify them       
        record_supplier_earnings.delay(instance.id)

    if instance.status == 'failed':        
        notification_data['note'] = f'Transaction with id {instance.pk} has failed. Please try again'
        Notification.objects.create(**notification_data)