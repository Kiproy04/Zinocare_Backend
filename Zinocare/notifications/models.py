import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Notification(models.Model):
    """
    Represents a notification to be sent to a user (farmer or vet)
    regarding vaccination schedules or related updates.

    Payload field (JSONField) should follow this recommended schema:
    {
        "subject": "Vaccination Reminder",
        "body": "Your cow needs vaccination on 2025-08-23",
        "metadata": { "animal_id": "...", "schedule_id": "..." }
    }
    """

    class Channel(models.TextChoices):
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"
        PUSH = "PUSH", "Push Notification"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    schedule = models.ForeignKey(
        "vaccinations.VaccinationSchedule",
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Vaccination schedule this notification belongs to",
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The farmer or vet who will receive this notification",
    )

    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.SMS,
        db_index=True,
    )

    send_at = models.DateTimeField(
        help_text="When the notification should be sent",
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    payload = models.JSONField(
        null=True,
        blank=True,
        help_text="Optional structured data (e.g. subject, body, metadata)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-send_at", "-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "recipient", "channel", "send_at"],
                name="uniq_notification_sched_recipient_channel_sendat",
            )
        ]
        indexes = [
            # Composite index optimizes queries like:
            # Notification.objects.filter(status="PENDING", send_at__lte=timezone.now())
            models.Index(fields=["status", "send_at"]),
            models.Index(fields=["send_at"]),
        ]

    def clean(self):
        if self.send_at and self.send_at <= timezone.now():
            raise ValidationError({"send_at": "Send time must be in the future."})

        # Optional domain safeguard:
        # Ensure recipient is schedule owner or assigned vet
        # if hasattr(self.schedule, "animal") and self.schedule.animal.owner != self.recipient:
        #     raise ValidationError("Recipient must be the animal owner or assigned vet.")

    def save(self, *args, **kwargs):
        self.full_clean()  # ensures validation always runs
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.channel} to {self.recipient} at {self.send_at:%Y-%m-%d %H:%M} ({self.status})"

