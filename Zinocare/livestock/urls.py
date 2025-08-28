from django.urls import path
from .views import AnimalListCreateView, AnimalDetailView

urlpatterns = [
    path("Animal-list", AnimalListCreateView.as_view(), name="animal-list-create"),
    path("Animal-detail/<int:pk>/", AnimalDetailView.as_view(), name="animal-detail"),
]