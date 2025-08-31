from django.urls import path
from .views import (
    VaccineListCreateView, VaccineDetailView,
    VaccinationScheduleListCreateView, VaccinationScheduleDetailView,
    VaccinationRecordListCreateView, VaccinationRecordDetailView
)

urlpatterns = [
    path("vaccines/", VaccineListCreateView.as_view(), name="vaccine-list-create"),
    path("vaccines-details/<uuid:pk>/", VaccineDetailView.as_view(), name="vaccine-detail"),
    path("schedules/", VaccinationScheduleListCreateView.as_view(), name="schedule-list-create"),
    path("schedules-details/<uuid:pk>/", VaccinationScheduleDetailView.as_view(), name="schedule-detail"),
    path("records/", VaccinationRecordListCreateView.as_view(), name="record-list-create"),
    path("records-details/<uuid:pk>/", VaccinationRecordDetailView.as_view(), name="record-detail"),
]