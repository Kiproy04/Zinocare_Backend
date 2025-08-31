from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "status", "created_at", "channel", "payload")
    search_fields = ("recipient__username", "status", "send_at")
    list_filter = ("status", "created_at")
