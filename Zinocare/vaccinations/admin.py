from django.contrib import admin
from .models import Vaccine, VaccinationSchedule, VaccinationRecord

@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "manufacturer", "dose", "route", "recommended_interval_days", "created_at")
    search_fields = ("name", "manufacturer", "route")
    list_filter = ("manufacturer", "route")  

@admin.register(VaccinationSchedule)
class VaccinationScheduleAdmin(admin.ModelAdmin):
    list_display = ("animal", "vaccine", "interval_days", "status", "next_due")
    search_fields = ("animal__name", "vaccine__name", "status")
    list_filter = ("status", "interval_days")

@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ("animal", "vaccine", "performed_by", "date_administered", "batch_number")
    search_fields = ("schedule__animal__name", "performed_by__username", "vaccine__name", "batch_number")
    list_filter = ("date_administered", "batch_number")
