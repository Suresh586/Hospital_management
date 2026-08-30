from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render
from django.utils import timezone

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from pharmacy.models import Medicine
from billing.models import Bill


@login_required
def dashboard(request):

    today = timezone.localdate()

    # =========================================================
    # DATE RANGES
    # =========================================================

    first_day_current_month = today.replace(day=1)

    if first_day_current_month.month == 1:
        first_day_previous_month = first_day_current_month.replace(
            year=first_day_current_month.year - 1,
            month=12
        )
    else:
        first_day_previous_month = first_day_current_month.replace(
            month=first_day_current_month.month - 1
        )

    # =========================================================
    # PATIENTS
    # =========================================================

    total_patients = Patient.objects.count()

    patients_before_current_month = Patient.objects.filter(
        created_at__lt=first_day_current_month
    ).count()

    if patients_before_current_month > 0:
        patient_growth = (
            (total_patients - patients_before_current_month)
            / patients_before_current_month
        ) * 100
    else:
        patient_growth = 0

    # =========================================================
    # DOCTORS
    # =========================================================

    total_doctors = Doctor.objects.count()

    available_doctors = Doctor.objects.filter(
        status="Available"
    ).count()

    doctor_specializations = (
        Doctor.objects
        .values("specialization")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # =========================================================
    # TODAY'S APPOINTMENTS
    # =========================================================

    today_appointments = (
        Appointment.objects
        .filter(date=today)
        .select_related("patient", "doctor")
        .order_by("time")
    )

    today_appointment_count = today_appointments.count()

    remaining_appointments = today_appointments.filter(
        status__in=["Pending", "Confirmed"]
    ).count()

    # =========================================================
    # MONTHLY REVENUE
    # =========================================================

    monthly_revenue_result = (
        Bill.objects
        .filter(
            created_at__date__gte=first_day_current_month,
            created_at__date__lte=today
        )
        .aggregate(total=Sum("amount_paid"))
    )

    monthly_revenue = (
        monthly_revenue_result["total"]
        or Decimal("0.00")
    )

    # =========================================================
    # PREVIOUS MONTH REVENUE
    # =========================================================

    previous_month_revenue_result = (
        Bill.objects
        .filter(
            created_at__date__gte=first_day_previous_month,
            created_at__date__lt=first_day_current_month
        )
        .aggregate(total=Sum("amount_paid"))
    )

    previous_month_revenue = (
        previous_month_revenue_result["total"]
        or Decimal("0.00")
    )

    if previous_month_revenue > 0:
        revenue_growth = (
            (monthly_revenue - previous_month_revenue)
            / previous_month_revenue
        ) * 100
    else:
        revenue_growth = 0

    # =========================================================
    # CURRENT MONTH APPOINTMENTS BY DEPARTMENT
    # =========================================================

    departments = (
        Appointment.objects
        .filter(
            date__gte=first_day_current_month,
            date__lte=today
        )
        .values(
            "doctor__specialization"
        )
        .annotate(
            total=Count("id")
        )
        .order_by("-total")[:4]
    )

    # =========================================================
    # LOW STOCK MEDICINES
    # =========================================================

    low_stock_medicines = Medicine.objects.filter(
        quantity__lt=10
    ).count()

    out_of_stock_medicines = Medicine.objects.filter(
        quantity=0
    ).count()

    # =========================================================
    # RECENT BILLS
    # =========================================================

    recent_bills = (
        Bill.objects
        .select_related("patient", "doctor")
        .order_by("-created_at")[:5]
    )

    # =========================================================
    # DASHBOARD CONTEXT
    # =========================================================

    context = {

        # Patients
        "total_patients": total_patients,
        "patient_growth": round(patient_growth, 1),

        # Doctors
        "total_doctors": total_doctors,
        "available_doctors": available_doctors,
        "doctor_specializations": doctor_specializations,

        # Appointments
        "today_appointments": today_appointments,
        "today_appointment_count": today_appointment_count,
        "remaining_appointments": remaining_appointments,

        # Revenue
        "monthly_revenue": monthly_revenue,
        "revenue_growth": round(revenue_growth, 1),

        # Departments
        "departments": departments,

        # Pharmacy
        "low_stock_medicines": low_stock_medicines,
        "out_of_stock_medicines": out_of_stock_medicines,

        # Bills
        "recent_bills": recent_bills,

        # Date
        "today": today,
    }

    return render(
        request,
        "home.html",
        context
    )