# from django.shortcuts import render

# # Create your views here.
# def patients_view(request):
#     return render(request,'patients/patients_list.html')
from datetime import date

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Patient


def patients_home(request):

    patients = Patient.objects.all().order_by("-created_at")

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        patients = patients.filter(
            Q(name__icontains=search)
            | Q(patient_id__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )

    # Status
    status = request.GET.get("status", "").strip()

    if status in ["Active", "Inactive"]:
        patients = patients.filter(status=status)

    # Gender
    gender = request.GET.get("gender", "").strip()

    if gender in ["Male", "Female", "Other"]:
        patients = patients.filter(gender=gender)

    # Statistics
    total_patients = Patient.objects.count()

    active_patients = Patient.objects.filter(
        status="Active"
    ).count()

    today = date.today()

    new_patients = Patient.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month
    ).count()

    # Pagination
    paginator = Paginator(patients, 6)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "patients": page_obj,
        "page_obj": page_obj,

        "total_patients": total_patients,
        "new_patients": new_patients,
        "active_patients": active_patients,

        # Will connect to appointments later
        "todays_visits": 0,

        "search": search,
        "selected_status": status,
        "selected_gender": gender,
    }

    return render(
        request,
        "patients/patients_list.html",
        context
    )


def add_patient(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        gender = request.POST.get(
            "gender"
        )

        date_of_birth = request.POST.get(
            "date_of_birth"
        )

        blood_group = request.POST.get(
            "blood_group"
        )

        address = request.POST.get(
            "address",
            ""
        ).strip()

        emergency_contact_name = request.POST.get(
            "emergency_contact_name",
            ""
        ).strip()

        emergency_contact_phone = request.POST.get(
            "emergency_contact_phone",
            ""
        ).strip()

        status = request.POST.get(
            "status",
            "Active"
        )

        # ======================================
        # BASIC VALIDATION
        # ======================================

        if not name or not phone or not gender or not date_of_birth or not blood_group:
            messages.error(
                request,
                "Please fill all required fields."
            )

            return render(
                request,
                "patients/add_patient.html"
            )

        # ======================================
        # CREATE PATIENT
        # ======================================

        Patient.objects.create(
            name=name,
            email=email,
            phone=phone,
            gender=gender,
            date_of_birth=date_of_birth,
            blood_group=blood_group,
            address=address,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_contact_phone,
            status=status,
        )

        messages.success(
            request,
            "Patient registered successfully."
        )

        return redirect(
            "patients"
        )

    return render(
        request,
        "patients/add_patient.html"
    )


def patient_detail(request, patient_id):

    patient = get_object_or_404(
        Patient,
        patient_id=patient_id
    )

    return render(
        request,
        "patients/patient_detail.html",
        {
            "patient": patient
        }
    )


def delete_patient(request, patient_id):

    patient = get_object_or_404(
        Patient,
        patient_id=patient_id
    )

    if request.method == "POST":

        patient.delete()

        messages.success(
            request,
            "Patient deleted successfully."
        )

        return redirect(
            "patients"
        )

    return render(
        request,
        "patients/delete_patient.html",
        {
            "patient": patient
        }
    )