from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Vaccine, VaccinationSchedule, VaccinationRecord
from .serializers import (
    VaccineSerializer,
    VaccinationScheduleSerializer,
    VaccinationRecordSerializer,
)


class VaccineListView(generics.ListAPIView):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer
    permission_classes = [permissions.IsAuthenticated]


class VaccinationScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = VaccinationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "mkulima":
            return VaccinationSchedule.objects.filter(mkulima=user.mkulimaprofile)
        elif user.role == "vet":
            return VaccinationSchedule.objects.all()
        return VaccinationSchedule.objects.none()

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class VaccinationScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VaccinationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "mkulima":
            return VaccinationSchedule.objects.filter(mkulima=user.mkulimaprofile)
        elif user.role == "vet":
            return VaccinationSchedule.objects.all()
        return VaccinationSchedule.objects.none()

    def update(self, request, *args, **kwargs):
        if request.user.role == "vet":
            return Response({"detail": "Vets cannot update schedules."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role == "vet":
            return Response({"detail": "Vets cannot delete schedules."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class VaccinationRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "vet":
            return VaccinationRecord.objects.all()
        elif user.role == "mkulima":
            return VaccinationRecord.objects.filter(animal__mkulima=user.mkulimaprofile)
        return VaccinationRecord.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.role != "vet":
            return Response({"detail": "Only vets can create records."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class VaccinationRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "vet":
            return VaccinationRecord.objects.all()
        elif user.role == "mkulima":
            return VaccinationRecord.objects.filter(animal__mkulima=user.mkulimaprofile)
        return VaccinationRecord.objects.none()

    def update(self, request, *args, **kwargs):
        if request.user.role != "vet":
            return Response({"detail": "Only vets can update records."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "vet":
            return Response({"detail": "Only vets can delete records."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx