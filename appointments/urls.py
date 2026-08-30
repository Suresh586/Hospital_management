# from django.urls import path
# from .views import appointments_view
# from .views import patient_view

from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.appointments_home,
        name="appointments_home"
    ),

]