# from django.urls import path
# from .views import doctors_view

# urlpatterns = [
#     path("", doctors_view, name="doctors"),
# ]
from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.doctors_home,
        name="doctors"
    ),

    path(
        "add/",
        views.add_doctor,
        name="add_doctor"
    ),

    path(
        "edit/<str:doctor_id>/",
        views.edit_doctor,
        name="edit_doctor"
    ),

    path(
        "delete/<str:doctor_id>/",
        views.delete_doctor,
        name="delete_doctor"
    ),

]