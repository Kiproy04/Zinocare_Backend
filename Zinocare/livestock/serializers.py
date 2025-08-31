from rest_framework import serializers
from .models import Animal
from accounts.serializers import MkulimaProfileSerializer

class AnimalSerializer(serializers.ModelSerializer):
    mkulima = MkulimaProfileSerializer(read_only=True)

    class Meta:
        model = Animal
        fields = ["id", "name", "species", "mkulima", "breed", "sex", "date_of_birth", "created_at"]