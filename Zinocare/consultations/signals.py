from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Consultation
from notifications.models import Notification

@receiver(post_save, sender=Consultation)
def create_consultation_notifications(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            consultation=instance,  
            recipient=instance.farmer,
            channel=Notification.Channel.PUSH,
            send_at=timezone.now(),
            payload={
                "subject": "Consultation Booked",
                "body": f"Your consultation with vet {instance.vet} is scheduled for {instance.date}.",
                "metadata": {"consultation_id": str(instance.id)},
            },
        )
        Notification.objects.create(
            consultation=instance,
            recipient=instance.vet,
            channel=Notification.Channel.PUSH,
            send_at=timezone.now(),
            payload={
                "subject": "New Consultation Assigned",
                "body": f"You have a new consultation with farmer {instance.farmer} on {instance.date}.",
                "metadata": {"consultation_id": str(instance.id)},
            },
        )

    elif instance.status == Consultation.Status.CANCELLED:
        Notification.objects.create(
            consultation=instance,
            recipient=instance.farmer,
            channel=Notification.Channel.PUSH,
            send_at=timezone.now(),
            payload={
                "subject": "Consultation Cancelled",
                "body": f"Your consultation with {instance.vet} on {instance.date} has been cancelled.",
                "metadata": {"consultation_id": str(instance.id)},
            },
        )
        Notification.objects.create(
            consultation=instance,
            recipient=instance.vet,
            channel=Notification.Channel.PUSH,
            send_at=timezone.now(),
            payload={
                "subject": "Consultation Cancelled",
                "body": f"The consultation with farmer {instance.farmer} on {instance.date} has been cancelled.",
                "metadata": {"consultation_id": str(instance.id)},
            },
        )