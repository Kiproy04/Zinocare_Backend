from django.contrib import admin
from .models import Consultation

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("farmer", "vet", "requested_at", "scheduled_at", "status")
    search_fields = ("farmer__name", "vet__name", "status")
    list_filter = ("status", "scheduled_at")
