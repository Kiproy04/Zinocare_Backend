from rest_framework import serializers
from django.utils import timezone
from .models import Consultation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name"]

class ConsultationRequestSerializer(serializers.ModelSerializer):
    farmer_detail = UserBasicSerializer(source='farmer', read_only=True)
    vet_detail = UserBasicSerializer(source='vet', read_only=True)

    class Meta:
        model = Consultation
        fields = ["id", "farmer", "farmer_detail", "vet", "vet_detail", 
                  "status", "notes", "scheduled_at", "requested_at"]
        read_only_fields = ["id", "farmer", "farmer_detail", "vet", 
                           "vet_detail", "status", "scheduled_at", "requested_at"]

    def create(self, validated_data):
        validated_data["farmer"] = self.context["request"].user
        return super().create(validated_data)

class ConsultationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ["id", "vet", "scheduled_at", "status"]
        read_only_fields = ["id", "status"]

    def validate_scheduled_at(self, value):
        if not value:
            raise serializers.ValidationError("Scheduled time is required.")
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future.")
        return value

    def update(self, instance, validated_data):
        vet = self.context["request"].user  # force current vet
        scheduled_at = validated_data.get("scheduled_at")

        if instance.status != Consultation.Status.REQUESTED:
            raise serializers.ValidationError("Only requested consultations can be scheduled.")

        instance.schedule(vet=vet, scheduled_at=scheduled_at)
        return instance


class ConsultationCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ["id", "notes", "status"]
        read_only_fields = ["id", "status"]

    def update(self, instance, validated_data):
        if instance.status != Consultation.Status.SCHEDULED:
            raise serializers.ValidationError("Only scheduled consultations can be completed.")

        notes = validated_data.get("notes", "")
        instance.complete(notes=notes)
        return instance


class ConsultationCancelSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Consultation
        fields = ["id", "reason", "status", "notes"]
        read_only_fields = ["id", "status", "notes"]

    def update(self, instance, validated_data):
        reason = validated_data.get("reason", "")
        instance.cancel(reason=reason)
        return instance