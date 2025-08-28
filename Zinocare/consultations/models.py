import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class ConsultationQuerySet(models.QuerySet):
    def requested(self):
        return self.filter(status=Consultation.Status.REQUESTED)

    def scheduled(self):
        return self.filter(status=Consultation.Status.SCHEDULED)

    def completed(self):
        return self.filter(status=Consultation.Status.COMPLETED)

    def cancelled(self):
        return self.filter(status=Consultation.Status.CANCELLED)

    def upcoming(self):
        return self.scheduled().filter(scheduled_at__gt=timezone.now())

    def past_due(self):
        return self.scheduled().filter(scheduled_at__lt=timezone.now())


class Consultation(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consultations_requested",
        help_text="Farmer requesting veterinary consultation",
    )
    vet = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="consultations_received",
        help_text="Vet assigned to handle the consultation",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time scheduled for consultation",
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
    )
    notes = models.TextField(blank=True, help_text="Notes or summary after consultation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ConsultationQuerySet.as_manager()

    class Meta:
        ordering = ["-scheduled_at", "-requested_at"]
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["vet", "status", "scheduled_at"]),
        ]

    def clean(self):
        if self.vet and self.vet_id == self.farmer_id:
            raise ValidationError("Farmer and Vet must be different users.")

        farmer_role = getattr(self.farmer, "role", None)
        vet_role = getattr(self.vet, "role", None) if self.vet else None

        if farmer_role and farmer_role != "mkulima":
            raise ValidationError({"farmer": "Farmer must have role 'mkulima'."})
        if self.vet and vet_role != "vet":
            raise ValidationError({"vet": "Assigned user must have role 'vet'."})

        now = timezone.now()

        if self.status == self.Status.SCHEDULED:
            if not self.scheduled_at:
                raise ValidationError(
                    {"scheduled_at": "Scheduled consultations must have a scheduled time."}
                )
            if self.scheduled_at < now:
                raise ValidationError({"scheduled_at": "Scheduled time must be in the future."})

        if self.status == self.Status.COMPLETED:
            if not self.scheduled_at:
                raise ValidationError({"scheduled_at": "Completed consultations must have been scheduled."})
            if self.scheduled_at > now:
                raise ValidationError({"scheduled_at": "Completed consultations cannot be in the future."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def schedule(self, vet, scheduled_at):
        self.vet = vet
        self.scheduled_at = scheduled_at
        self.status = self.Status.SCHEDULED
        self.save(update_fields=["vet", "scheduled_at", "status", "updated_at"])

    def complete(self, notes=""):
        self.status = self.Status.COMPLETED
        self.notes = notes
        self.save(update_fields=["status", "notes", "updated_at"])

    def cancel(self, reason=""):
        if self.status == self.Status.CANCELLED:
            raise ValidationError("This consultation is already cancelled.")
        if self.status == self.Status.COMPLETED:
            raise ValidationError("Completed consultations cannot be cancelled.")

        self.status = self.Status.CANCELLED

        if not self.notes:
            self.notes = ""

        if reason:
            self.notes = (self.notes + f"\n[CANCELLED]: {reason}").strip()

        self.save(update_fields=["status", "notes", "updated_at"])
        return self

    def __str__(self):
        vet_label = self.vet or "Unassigned"
        return f"Consultation [{self.status}] - Farmer: {self.farmer} | Vet: {vet_label}"