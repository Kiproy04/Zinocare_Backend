from rest_framework import serializers
from django.utils import timezone
from .models import Vaccine, VaccinationSchedule, VaccinationRecord
from notifications.models import Notification


class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = "__all__"


class VaccinationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationSchedule
        fields = ["id", "mkulima", "animal", "vaccine", "scheduled_date", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at", "mkulima"]

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.role == "mkulima":
            validated_data["mkulima"] = request.user.mkulimaprofile

        schedule = super().create(validated_data)

        self.create_farmer_notification(schedule)
        return schedule

    def create_farmer_notification(self, schedule):
        """
        Creates a notification for the farmer 1 day before scheduled_date.
        """
        send_at = schedule.scheduled_date - timezone.timedelta(days=1)
        if send_at > timezone.now():  
            Notification.objects.create(
                schedule=schedule,
                recipient=schedule.animal.mkulima.user,  
                send_at=send_at,
                channel=Notification.Channel.SMS,
                payload={
                    "subject": "Vaccination Reminder",
                    "body": f"Reminder: Your {schedule.animal.species} "
                            f"({schedule.animal.tag_id}) is scheduled for "
                            f"{schedule.vaccine.name} on {schedule.scheduled_date:%Y-%m-%d}.",
                    "metadata": {
                        "animal_id": str(schedule.animal.id),
                        "schedule_id": str(schedule.id),
                    }
                }
            )

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        method = request.method

        if user.role == "vet" and method in ("POST", "PUT", "PATCH", "DELETE"):
            raise serializers.ValidationError("Vets cannot create or modify schedules. Only mkulima can.")
        return attrs


class VaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = ["id", "schedule", "animal", "vaccine", "vet", "date_administered", "notes", "created_at"]
        read_only_fields = ["id", "vet", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        if user.role != "vet":
            raise serializers.ValidationError("Only vets can create vaccination records.")

        validated_data["vet"] = user.vetprofile
        record = super().create(validated_data)

        if record.schedule:
            record.schedule.status = "completed"
            record.schedule.save()

        return record

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        method = request.method

        if user.role == "mkulima" and method in ("POST", "PUT", "PATCH", "DELETE"):
            raise serializers.ValidationError("Mkulima cannot modify vaccination records.")
        return attrs