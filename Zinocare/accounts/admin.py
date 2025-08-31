from django.contrib import admin
from .models import User, MkulimaProfile, VetProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "role", "is_active", "is_staff")
    search_fields = ("username", "email", "role")
    list_filter = ("date_joined", "is_staff", "role")


@admin.register(MkulimaProfile)
class MkulimaProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "farm_name", "location")
    search_fields = ("user__username", "farm_name")
    list_filter = ("location",)


@admin.register(VetProfile)
class VetProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "license_number", "specialization")
    search_fields = ("user__username", "specialization")
    list_filter = ("license_number", "specialization")
