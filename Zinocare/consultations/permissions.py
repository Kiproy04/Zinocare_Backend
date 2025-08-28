from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Consultation

class IsFarmer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "mkulima"


class IsVet(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "vet"


class IsOwnerOrVet(BasePermission):
    def has_object_permission(self, request, view, obj: Consultation):
        role = getattr(request.user, "role", None)
        if role == "mkulima":
            return obj.farmer_id == request.user.id
        if role == "vet":
            return obj.vet_id == request.user.id or obj.status == Consultation.Status.REQUESTED
        return False