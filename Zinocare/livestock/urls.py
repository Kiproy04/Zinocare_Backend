from django.urls import path
from .views import AnimalListCreateView, AnimalDetailView

urlpatterns = [
    path("animal-list", AnimalListCreateView.as_view(), name="animal-list-create"),
    path("animal-detail/<int:pk>/", AnimalDetailView.as_view(), name="animal-detail"),
]