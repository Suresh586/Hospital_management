# from django.shortcuts import render

# # Create your views here.
# def appointments_view(request):
#     return render (request,'appointment/appointment_list.html')

from datetime import date

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from doctors.models import Doctor
from patients.models import Patient

from .models import Appointment


def appointments_home(request):

    # =====================================================
    # BOOK NEW APPOINTMENT
    # =====================================================

    if request.method == "POST":

        patient_id = request.POST.get("patient")
        doctor_id = request.POST.get("doctor")
        appointment_date = request.POST.get("date")
        appointment_time = request.POST.get("time")
        reason = request.POST.get("reason")

        if not all([
            patient_id,
            doctor_id,
            appointment_date,
            appointment_time,
            reason
        ]):
            messages.error(
                request,
                "Please fill all appointment fields."
            )
            return redirect("appointments_home")

        patient = Patient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)

        # Prevent duplicate doctor booking
        already_booked = Appointment.objects.filter(
            doctor=doctor,
            date=appointment_date,
            time=appointment_time,
            status__in=["Pending", "Confirmed"]
        ).exists()

        if already_booked:
            messages.error(
                request,
                "This doctor is already booked at the selected date and time."
            )
            return redirect("appointments_home")

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=appointment_date,
            time=appointment_time,
            reason=reason,
            status="Pending"
        )

        messages.success(
            request,
            "Appointment booked successfully."
        )

        return redirect("appointments_home")

    # =====================================================
    # REAL PATIENTS & DOCTORS
    # =====================================================

    patients = Patient.objects.all().order_by("name")

    doctors = Doctor.objects.all().order_by("name")

    # =====================================================
    # APPOINTMENT QUERYSET
    # =====================================================

    appointments = Appointment.objects.select_related(
        "patient",
        "doctor"
    ).all()

    # =====================================================
    # SEARCH
    # =====================================================

    search = request.GET.get("search", "").strip()

    if search:
        appointments = appointments.filter(
            Q(appointment_id__icontains=search)
            | Q(patient__name__icontains=search)
            | Q(doctor__name__icontains=search)
            | Q(reason__icontains=search)
        )

    # =====================================================
    # STATUS FILTER
    # =====================================================

    status = request.GET.get("status", "").strip()

    if status:
        appointments = appointments.filter(
            status=status
        )

    # =====================================================
    # DATE FILTER
    # =====================================================

    selected_date = request.GET.get("date", "").strip()

    if selected_date:
        appointments = appointments.filter(
            date=selected_date
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    total_appointments = Appointment.objects.count()

    pending_appointments = Appointment.objects.filter(
        status="Pending"
    ).count()

    confirmed_appointments = Appointment.objects.filter(
        status="Confirmed"
    ).count()

    today_appointments = Appointment.objects.filter(
        date=date.today()
    ).count()

    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        appointments,
        10
    )

    page_number = request.GET.get("page")

    appointments_page = paginator.get_page(
        page_number
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "patients": patients,
        "doctors": doctors,
        "appointments": appointments_page,

        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "confirmed_appointments": confirmed_appointments,
        "today_appointments": today_appointments,
    }

    return render(
        request,
        "appointments/appointments.html",
        context
    )