from rest_framework import serializers
from .models import Animal

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ["id", "name", "species", "mkulima", "breed", "sex", "date_of_birth", "created_at"]
        read_only_fields = ["id", "mkulima", "created_at"]  