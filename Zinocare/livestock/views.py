from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Animal
from .serializers import AnimalSerializer


class AnimalDetailView(generics.RetrieveAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "mkulima":
            return Animal.objects.filter(mkulima=user.mkulimaprofile)
        elif user.role == "vet":
            return Animal.objects.all()
        return Animal.objects.none()

    def put(self, request, *args, **kwargs):
        if request.user.role != "mkulima":
            return Response(
                {"detail": "Only mkulima can update animals."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if request.user.role != "mkulima":
            return Response(
                {"detail": "Only mkulima can update animals."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if request.user.role != "mkulima":
            return Response(
                {"detail": "Only mkulima can delete animals."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return self.destroy(request, *args, **kwargs)

class AnimalListCreateView(generics.ListCreateAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "mkulima":
            return Animal.objects.filter(mkulima=user.mkulimaprofile)
        elif user.role == "vet":
            return Animal.objects.all()  
        return Animal.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.role != "mkulima":
            return Response(
                {"detail": "Only mkulima can add animals."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(mkulima=self.request.user.mkulimaprofile)