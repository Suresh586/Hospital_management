from django.urls import path
from .views import appointments_view

urlpatterns=[
    path('',appointments_view,name='appointment')
]