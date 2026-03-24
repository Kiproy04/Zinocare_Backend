from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    source_type = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "channel",
            "status",
            "send_at",
            "payload",
            "source_type",
            "source",
            "created_at",
        ]

    @extend_schema_field(serializers.CharField())
    def get_source_type(self, obj) -> str:
        if obj.schedule:
            return "vaccination"
        elif obj.consultation:
            return "consultation"
        return "system"

    @extend_schema_field(serializers.DictField())
    def get_source(self, obj) -> dict:
        if obj.schedule:
            return {
                "schedule_id": str(obj.schedule.id),
                "animal": {
                    "id": str(obj.schedule.animal.id),
                    "name": obj.schedule.animal.name,
                    "species": obj.schedule.animal.species,
                },
                "date": obj.schedule.date,
                "vaccine": obj.schedule.vaccine.name if obj.schedule.vaccine else None,
            }
        elif obj.consultation:
            return {
                "consultation_id": str(obj.consultation.id),
                "farmer": str(obj.consultation.farmer),
                "vet": str(obj.consultation.vet),
                "date": obj.consultation.date,
                "status": obj.consultation.status,
            }
        return {}