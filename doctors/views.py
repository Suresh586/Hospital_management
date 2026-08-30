# from django.shortcuts import render

# # Create your views here.
# def doctors_view(request):
#     return render (request,'doctors/doctors.html')

from datetime import date

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Doctor


def doctors_home(request):

    doctors = Doctor.objects.all()

    # =====================================================
    # SEARCH
    # =====================================================

    search = request.GET.get("search", "").strip()

    if search:

        doctors = doctors.filter(
            Q(name__icontains=search)
            | Q(doctor_id__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
        )


    # =====================================================
    # SPECIALIZATION FILTER
    # =====================================================

    specialization = request.GET.get(
        "specialization",
        ""
    ).strip()

    if specialization:

        doctors = doctors.filter(
            specialization=specialization
        )


    # =====================================================
    # STATUS FILTER
    # =====================================================

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:

        doctors = doctors.filter(
            status=status
        )


    # =====================================================
    # STATISTICS
    # =====================================================

    total_doctors = Doctor.objects.count()

    available_doctors = Doctor.objects.filter(
        status="Available"
    ).count()

    specialists = (
        Doctor.objects
        .exclude(specialization="General Medicine")
        .values("specialization")
        .distinct()
        .count()
    )

    departments = (
        Doctor.objects
        .values("specialization")
        .distinct()
        .count()
    )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        doctors,
        6
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )


    context = {

        "doctors": page_obj,

        "page_obj": page_obj,

        "total_doctors": total_doctors,

        "available_doctors": available_doctors,

        "specialists": specialists,

        "departments": departments,

        "search": search,

        "selected_specialization":
            specialization,

        "selected_status":
            status,
        
        "specialization_choices":
            Doctor.SPECIALIZATION_CHOICES,

    }

    return render(
        request,
        "doctors/doctors.html",
        context
    )


# =========================================================
# ADD DOCTOR
# =========================================================

def add_doctor(request):

    if request.method == "POST":

        Doctor.objects.create(

            name=request.POST.get("name"),

            email=request.POST.get("email"),

            phone=request.POST.get("phone"),

            specialization=request.POST.get(
                "specialization"
            ),

            qualification=request.POST.get(
                "qualification"
            ),

            experience=request.POST.get(
                "experience"
            ),

            consultation_fee=request.POST.get(
                "consultation_fee"
            ),

            available_days=request.POST.get(
                "available_days"
            ),

            start_time=request.POST.get(
                "start_time"
            ),

            end_time=request.POST.get(
                "end_time"
            ),

            status=request.POST.get(
                "status"
            ),

        )

        return redirect("doctors")


    return render(
        request,
        "doctors/add_doctor.html",
    {
        "specialization_choices":
            Doctor.SPECIALIZATION_CHOICES
    }
    )
    


# =========================================================
# EDIT DOCTOR
# =========================================================

def edit_doctor(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        doctor_id=doctor_id
    )

    if request.method == "POST":

        doctor.name = request.POST.get("name")

        doctor.email = request.POST.get("email")

        doctor.phone = request.POST.get("phone")

        doctor.specialization = request.POST.get(
            "specialization"
        )

        doctor.qualification = request.POST.get(
            "qualification"
        )

        doctor.experience = request.POST.get(
            "experience"
        )

        doctor.consultation_fee = request.POST.get(
            "consultation_fee"
        )

        doctor.available_days = request.POST.get(
            "available_days"
        )

        doctor.start_time = request.POST.get(
            "start_time"
        )

        doctor.end_time = request.POST.get(
            "end_time"
        )

        doctor.status = request.POST.get(
            "status"
        )

        doctor.save()

        return redirect("doctors")


    return render(
    request,
    "doctors/add_doctor.html",
    {
        "doctor": doctor,
        "edit_mode": True,
        "specialization_choices":
            Doctor.SPECIALIZATION_CHOICES,
    }

    )


# =========================================================
# DELETE DOCTOR
# =========================================================

def delete_doctor(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        doctor_id=doctor_id
    )

    doctor.delete()

    return redirect("doctors")