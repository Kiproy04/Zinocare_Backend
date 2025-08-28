from django.urls import path
from .views import (
    VaccineListView,
    VaccinationScheduleListCreateView, VaccinationScheduleDetailView,
    VaccinationRecordListCreateView, VaccinationRecordDetailView
)

urlpatterns = [
    path("vaccines/", VaccineListView.as_view(), name="vaccine-list"),
    path("schedules/", VaccinationScheduleListCreateView.as_view(), name="schedule-list-create"),
    path("schedules/<uuid:pk>/", VaccinationScheduleDetailView.as_view(), name="schedule-detail"),
    path("records/", VaccinationRecordListCreateView.as_view(), name="record-list-create"),
    path("records/<uuid:pk>/", VaccinationRecordDetailView.as_view(), name="record-detail"),
]