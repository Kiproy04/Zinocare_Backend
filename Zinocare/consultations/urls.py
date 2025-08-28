from django.urls import path
from .views import (
    ConsultationRequestView,
    ConsultationScheduleView,
    ConsultationCompleteView,
    ConsultationCancelView,
)

urlpatterns = [
    path("request/", ConsultationRequestView.as_view(), name="consultation-request"),
    path("schedule/<uuid:pk>/", ConsultationScheduleView.as_view(), name="consultation-schedule"),
    path("complete/<uuid:pk>/", ConsultationCompleteView.as_view(), name="consultation-complete"),
    path("cancel/<uuid:pk>/", ConsultationCancelView.as_view(), name="consultation-cancel"),
]