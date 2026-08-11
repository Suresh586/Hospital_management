from django.shortcuts import render

# Create your views here.
def patients_view(request):
    return render(request,'patients/patients_list.html')