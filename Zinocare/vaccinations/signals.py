from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import VaccinationSchedule
from notifications.models import Notification


@receiver(post_save, sender=VaccinationSchedule)
def create_vaccination_notification(sender, instance, created, **kwargs):
    if not created:
        return

    send_at = timezone.make_aware(
        timezone.datetime.combine(instance.next_due, timezone.datetime.min.time())
    ) - timedelta(days=1)

    if send_at <= timezone.now():
        return

    try:
        recipient = instance.animal.mkulima.user
    except AttributeError:
        return

    Notification.objects.get_or_create(
        schedule=instance,
        recipient=recipient,
        channel=Notification.Channel.SMS,
        send_at=send_at,
        defaults={
            "payload": {
                "subject": "Vaccination Reminder",
                "body": (
                    f"Reminder: Your {instance.animal.species} "
                    f"({instance.animal.tag_id}) is due for "
                    f"{instance.vaccine.name} on {instance.next_due:%Y-%m-%d}."
                ),
                "metadata": {
                    "animal_id": str(instance.animal.id),
                    "schedule_id": str(instance.id),
                }
            }
        }
    )