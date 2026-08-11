from django.urls import path
from .views import doctors_view

urlpatterns = [
    path("", doctors_view, name="doctors"),
]