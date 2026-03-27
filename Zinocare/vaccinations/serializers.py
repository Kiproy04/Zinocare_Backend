from rest_framework import serializers
from .models import Vaccine, VaccinationSchedule, VaccinationRecord, VaccineTargetSpecies


class VaccineSerializer(serializers.ModelSerializer):
    target_species = serializers.SlugRelatedField(
        slug_field="species",
        queryset=VaccineTargetSpecies.objects.all(),
        many=True
    )
    class Meta:
        model = Vaccine
        fields = "__all__"


class VaccinationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationSchedule
        fields = ["id", "animal", "vaccine", "next_due", "interval_days", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.role == "vet":
            raise serializers.ValidationError("Vets cannot create or modify schedules.")
        return attrs


class VaccinationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationRecord
        fields = ["id", "animal", "vaccine", "performed_by", "date_administered", "batch_number", "notes", "created_at"]
        read_only_fields = ["id", "performed_by", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        if user.role != "vet":
            raise serializers.ValidationError("Only vets can create vaccination records.")
        validated_data["performed_by"] = user
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.role == "mkulima":
            method = request.method
            if method in ("POST", "PUT", "PATCH", "DELETE"):
                raise serializers.ValidationError("Mkulima cannot modify vaccination records.")
        return attrs