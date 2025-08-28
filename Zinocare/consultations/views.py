from rest_framework import generics, permissions
from .models import Consultation
from .serializers import (
    ConsultationRequestSerializer,
    ConsultationScheduleSerializer,
    ConsultationCompleteSerializer,
    ConsultationCancelSerializer,
)
from .permissions import IsFarmer, IsVet, IsOwnerOrVet


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