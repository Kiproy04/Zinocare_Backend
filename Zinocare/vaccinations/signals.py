from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import VaccinationSchedule
from notifications.models import Notification

@receiver(post_save, sender=VaccinationSchedule)
def create_vaccination_notification(sender, instance, created, **kwargs):
    if created:
        send_at = instance.date - timedelta(days=1)
        if send_at <= timezone.now():
            send_at = instance.date

        Notification.objects.create(
            schedule=instance,   
            recipient=instance.animal.owner,
            channel=Notification.Channel.PUSH,
            send_at=send_at,
            payload={
                "subject": "Vaccination Reminder",
                "body": f"Your {instance.animal.species} ({instance.animal.name}) "
                        f"needs vaccination on {instance.date}",
                "metadata": {"schedule_id": str(instance.id)},
            },
        )