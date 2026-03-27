from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Consultation
from .serializers import (
    ConsultationRequestSerializer,
    ConsultationScheduleSerializer,
    ConsultationCompleteSerializer,
    ConsultationCancelSerializer,
)
from .permissions import IsFarmer, IsVet, IsOwnerOrVet


class ConsultationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "mkulima":
            return Consultation.objects.filter(farmer=user)
        elif user.role == "vet":
            return (
                Consultation.objects.filter(vet=user) |
                Consultation.objects.filter(status=Consultation.Status.REQUESTED)
            )
        return Consultation.objects.none()

    def get_serializer_class(self):
        return ConsultationRequestSerializer


class ConsultationRequestView(generics.CreateAPIView):
    serializer_class = ConsultationRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmer]


class ConsultationScheduleView(generics.UpdateAPIView):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsVet, IsOwnerOrVet]


class ConsultationCompleteView(generics.UpdateAPIView):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationCompleteSerializer
    permission_classes = [permissions.IsAuthenticated, IsVet, IsOwnerOrVet]


class ConsultationCancelView(generics.UpdateAPIView):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationCancelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrVet]

    def perform_update(self, serializer):
        consultation = self.get_object()
        if consultation.status in [Consultation.Status.COMPLETED, Consultation.Status.CANCELLED]:
            raise PermissionDenied("This consultation can no longer be cancelled.")
        serializer.save()