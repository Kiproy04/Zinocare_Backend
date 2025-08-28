import uuid
from django.db import models
from livestock.models import Animal
from django.conf import settings
from django.core.exceptions import ValidationError


class Vaccine(models.Model):
    class Route(models.TextChoices):
        INTRAMUSCULAR = "IM", "Intramuscular (into muscle)"
        SUBCUTANEOUS = "SC", "Subcutaneous (under skin)"
        ORAL = "ORAL", "Oral (by mouth)"
        NASAL = "NASAL", "Nasal (spray)"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    dose = models.CharField(max_length=100, help_text="Dosage info: 2ml per 10kg bodyweight or 5ml fixed dose")
    route = models.CharField(
        max_length=20,
        choices=Route.choices,
        blank=True,
        help_text="How the vaccine should be administered"
    )
    recommended_interval_days = models.PositiveIntegerField(null=True, blank=True, help_text="Interval before next dose/booster (in days)")
    created_at = models.DateTimeField(auto_now_add=True)
    target_species = models.ManyToManyField(
        "VaccineTargetSpecies",
        related_name="vaccines",
        blank=True
    )

    def __str__(self):
        return self.name

class VaccineTargetSpecies(models.Model):
    class Species(models.TextChoices):
        CATTLE = "cattle", "Cattle"
        GOAT = "goat", "Goat"
        SHEEP = "sheep", "Sheep"
        POULTRY = "poultry", "Poultry"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    species = models.CharField(max_length=20, choices=Species.choices, unique=True)

    def __str__(self):
        return self.get_species_display()

class VaccinationSchedule(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        PAUSED = "PAUSED", "Paused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, related_name="vaccination_schedules"
    )
    vaccine = models.ForeignKey(
        Vaccine, on_delete=models.CASCADE, related_name="schedules"
    )
    next_due = models.DateField(db_index=True)
    interval_days = models.PositiveIntegerField(
        help_text="Interval in days before the next dose is due"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.vaccine.target_species.exists():
            allowed_species = [s.species for s in self.vaccine.target_species.all()]
            if self.animal.species not in allowed_species:
                raise ValidationError({
                    "animal": f"Cannot schedule {self.vaccine.name} for {self.animal.species}. "
                              f"Allowed species: {', '.join(allowed_species)}"
                })

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Schedule: {self.animal.tag_id} - {self.vaccine.name}"

class VaccinationRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, related_name="vaccination_records"
    )
    vaccine = models.ForeignKey(
        Vaccine, on_delete=models.CASCADE, related_name="records"
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="performed_vaccinations",
        help_text="Vet or staff who administered the vaccine"
    )
    date_administered = models.DateField()
    batch_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.vaccine.target_species.exists():
            allowed_species = [s.species for s in self.vaccine.target_species.all()]
            if self.animal.species not in allowed_species:
                raise ValidationError({
                    "animal": f"Cannot record {self.vaccine.name} for {self.animal.species}. "
                              f"Allowed species: {', '.join(allowed_species)}"
                })

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        if self.performed_by:
            performer = getattr(self.performed_by, "full_name", None) \
                        or " ".join(filter(None, [self.performed_by.first_name, self.performed_by.last_name])) \
                        or str(self.performed_by)
        else:
            performer = "Unknown"
        return f"{self.vaccine.name} for {self.animal.tag_id} by {performer}"