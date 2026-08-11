from django.shortcuts import render

# Create your views here.
def appointments_view(request):
    return render (request,'appointment/appointment_list.html')