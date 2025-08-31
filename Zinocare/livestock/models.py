import uuid
from django.db import models

class Animal(models.Model):
    SPECIES_CHOICES = [
        ("cattle", "Cattle"),
        ("goat", "Goat"),
        ("sheep", "Sheep"),
        ("poultry", "Poultry"),
        ("other", "Other"),
    ]

    SEX_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mkulima = models.ForeignKey(
        "accounts.MkulimaProfile", on_delete=models.CASCADE, related_name="livestock"
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100, blank=True, null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tag_id = models.CharField(max_length=50, blank=True, null=True)  
    health_status = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def age_in_months(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return (today.year - self.date_of_birth.year) * 12 + (today.month - self.date_of_birth.month)
        return None

    def __str__(self):
        try:
            owner = self.mkulima.user.full_name or self.mkulima.user.email
        except AttributeError:
            owner = "Unknown Owner"
        return f"{self.get_species_display()} ({self.tag_id}) - {owner}"


