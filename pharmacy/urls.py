from django.urls import path
from . import views


urlpatterns = [

    # Medicine
    path(
        "",
        views.medicine_list,
        name="medicine_list"
    ),

    path(
        "add/",
        views.medicine_add,
        name="medicine_add"
    ),

    path(
        "update/<int:pk>/",
        views.medicine_update,
        name="medicine_update"
    ),

    path(
        "delete/<int:pk>/",
        views.medicine_delete,
        name="medicine_delete"
    ),

    # Billing
    path(
        "billing/",
        views.medicine_billing,
        name="medicine_billing"
    ),
]