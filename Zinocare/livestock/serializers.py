from rest_framework import serializers
from .models import Animal
from accounts.serializers import UserSerializer

class AnimalSerializer(serializers.ModelSerializer):
    mkulima = UserSerializer(read_only=True)

    class Meta:
        model = Animal
        fields = ["id", "name", "species", "age", "mkulima", "created_at"]