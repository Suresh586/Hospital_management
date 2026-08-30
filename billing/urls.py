from django.urls import path

from . import views


app_name = "billing"


urlpatterns = [

    path(
        "",
        views.billing_create,
        name="create"
    ),

    path(
        "history/",
        views.billing_history,
        name="history"
    ),

    path(
        "detail/<int:bill_id>/",
        views.billing_detail,
        name="detail"
    ),
    path(
    "success/<int:bill_id>/",
    views.billing_success,
    name="success"
),

    path(
        "cancel/<int:bill_id>/",
        views.billing_cancel,
        name="cancel"
    ),

    path(
        "patient/<int:patient_id>/",
        views.patient_details,
        name="patient_details"
    ),

    path(
        "doctor/<int:doctor_id>/",
        views.doctor_details,
        name="doctor_details"
    ),

    path(
        "medicine/<int:medicine_id>/",
        views.medicine_details,
        name="medicine_details"
    ),
]