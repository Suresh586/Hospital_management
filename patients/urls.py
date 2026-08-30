from django.urls import path
from .views import patients_home
from . import views

urlpatterns=[
    path('',patients_home,name='patients'),
    path(
        "add/",
        views.add_patient,
        name="add_patient"
    ),

    path(
        "<str:patient_id>/",
        views.patient_detail,
        name="patient_detail"
    ),

    path(
        "<str:patient_id>/delete/",
        views.delete_patient,
        name="delete_patient"
    ),
]