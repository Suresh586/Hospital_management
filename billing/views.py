from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment
from pharmacy.models import Medicine

from .models import Bill, BillMedicineItem


# =========================================================
# DECIMAL HELPER
# =========================================================

def decimal_value(value):
    try:
        return Decimal(value or "0")

    except (
        InvalidOperation,
        TypeError,
        ValueError
    ):
        return Decimal("0.00")


# =========================================================
# CREATE BILL
# =========================================================

def billing_create(request):

    patients = (
        Patient.objects
        .filter(status="Active")
        .order_by("name")
    )

    doctors = (
        Doctor.objects
        .order_by("name")
    )

    medicines = (
        Medicine.objects
        .filter(quantity__gt=0)
        .order_by("medicine_name")
    )

    if request.method == "POST":

        try:

            with transaction.atomic():

                # =========================================
                # PATIENT
                # =========================================

                patient_id = request.POST.get("patient")

                if not patient_id:
                    raise ValueError(
                        "Please select a patient."
                    )

                patient = get_object_or_404(
                    Patient.objects.select_for_update(),
                    pk=patient_id
                )

                if patient.status != "Active":
                    raise ValueError(
                        "Selected patient is not active."
                    )

                # =========================================
                # DOCTOR
                # =========================================

                doctor_id = request.POST.get("doctor")

                if not doctor_id:
                    raise ValueError(
                        "Please select a doctor."
                    )

                doctor = get_object_or_404(
                    Doctor.objects.select_for_update(),
                    pk=doctor_id
                )

                # =========================================
                # APPOINTMENT
                # =========================================

                appointment = None

                appointment_id = (
                    request.POST.get("appointment")
                )

                if appointment_id:

                    appointment = get_object_or_404(
                        Appointment,
                        pk=appointment_id
                    )

                    if appointment.patient_id != patient.id:

                        raise ValueError(
                            "Selected appointment does not belong "
                            "to the selected patient."
                        )

                    if appointment.doctor_id != doctor.id:

                        raise ValueError(
                            "Selected appointment does not belong "
                            "to the selected doctor."
                        )

                    if appointment.status == "Cancelled":

                        raise ValueError(
                            "Cancelled appointments cannot be billed."
                        )

                # =========================================
                # CHARGES
                # =========================================

                consultation_fee = decimal_value(
                    request.POST.get(
                        "consultation_fee"
                    )
                )

                lab_charges = decimal_value(
                    request.POST.get(
                        "lab_charges"
                    )
                )

                room_charges = decimal_value(
                    request.POST.get(
                        "room_charges"
                    )
                )

                if (
                    consultation_fee < 0
                    or lab_charges < 0
                    or room_charges < 0
                ):
                    raise ValueError(
                        "Charges cannot be negative."
                    )

                # =========================================
                # MEDICINES
                # =========================================

                medicine_ids = request.POST.getlist(
                    "medicine_id[]"
                )

                medicine_quantities = request.POST.getlist(
                    "medicine_qty[]"
                )

                medicine_items = []

                medicine_total = Decimal("0.00")

                for medicine_id, qty_value in zip(
                    medicine_ids,
                    medicine_quantities
                ):

                    if not medicine_id:
                        continue

                    try:
                        quantity = int(qty_value or 0)

                    except (TypeError, ValueError):

                        raise ValueError(
                            "Invalid medicine quantity."
                        )

                    if quantity <= 0:
                        continue

                    medicine = get_object_or_404(
                        Medicine.objects.select_for_update(),
                        pk=medicine_id
                    )

                    if medicine.quantity < quantity:

                        raise ValueError(
                            f"Only {medicine.quantity} units of "
                            f"{medicine.medicine_name} are available."
                        )

                    unit_price = Decimal(
                        medicine.price
                    )

                    item_total = (
                        unit_price * quantity
                    )

                    medicine_total += item_total

                    medicine_items.append(
                        (
                            medicine,
                            quantity,
                            unit_price,
                            item_total
                        )
                    )

                # =========================================
                # TOTAL
                # =========================================

                total_amount = (
                    consultation_fee
                    + medicine_total
                    + lab_charges
                    + room_charges
                )

                if total_amount <= Decimal("0.00"):

                    raise ValueError(
                        "Bill amount must be greater than zero."
                    )

                # =========================================
                # PAYMENT
                # =========================================

                payment_status = request.POST.get(
                    "payment_status",
                    "Pending"
                )

                allowed_statuses = {
                    "Paid",
                    "Pending",
                    "Partial",
                    "Cancelled",
                }

                if payment_status not in allowed_statuses:

                    raise ValueError(
                        "Invalid payment status."
                    )

                payment_method = request.POST.get(
                    "payment_method",
                    ""
                )

                amount_paid = decimal_value(
                    request.POST.get(
                        "amount_paid"
                    )
                )

                if amount_paid < Decimal("0.00"):

                    raise ValueError(
                        "Amount paid cannot be negative."
                    )

                if payment_status == "Paid":

                    amount_paid = total_amount

                elif payment_status == "Pending":

                    amount_paid = Decimal("0.00")

                elif payment_status == "Partial":

                    if not (
                        Decimal("0.00")
                        < amount_paid
                        < total_amount
                    ):

                        raise ValueError(
                            "Partial payment must be greater than "
                            "zero and less than the total amount."
                        )

                elif payment_status == "Cancelled":

                    raise ValueError(
                        "A new bill cannot be created as Cancelled."
                    )

                # =========================================
                # PAYMENT METHOD VALIDATION
                # =========================================

                if (
                    amount_paid > 0
                    and not payment_method
                ):

                    raise ValueError(
                        "Please select a payment method."
                    )

                # =========================================
                # CREATE BILL
                # =========================================

                bill = Bill.objects.create(

                    patient=patient,

                    doctor=doctor,

                    appointment=appointment,

                    payment_date=(
                        request.POST.get(
                            "payment_date"
                        )
                        or timezone.localdate()
                    ),

                    consultation_fee=consultation_fee,

                    medicine_charges=medicine_total,

                    lab_charges=lab_charges,

                    room_charges=room_charges,

                    total_amount=total_amount,

                    amount_paid=amount_paid,

                    payment_status=payment_status,

                    payment_method=payment_method,

                    notes=request.POST.get(
                        "notes",
                        ""
                    )
                )

                # =========================================
                # CREATE MEDICINE ITEMS + STOCK
                # =========================================

                for (
                    medicine,
                    quantity,
                    unit_price,
                    item_total
                ) in medicine_items:

                    BillMedicineItem.objects.create(

                        bill=bill,

                        medicine=medicine,

                        quantity=quantity,

                        unit_price=unit_price,

                        total_price=item_total
                    )

                    medicine.quantity -= quantity

                    medicine.save(
                        update_fields=[
                            "quantity",
                            "updated_at"
                        ]
                    )

            messages.success(
                request,
                f"Bill {bill.bill_number} generated successfully."
            )

            return redirect(
                "billing:success",
                bill_id=bill.id
            )

        except ValueError as error:

            messages.error(
                request,
                str(error)
            )

    context = {

        "patients": patients,

        "doctors": doctors,

        "medicines": medicines,

        "payment_date": timezone.localdate(),

    }

    return render(
        request,
        "billing/billing.html",
        context
    )


# =========================================================
# PATIENT DETAILS
# =========================================================

@require_GET
def patient_details(
    request,
    patient_id
):

    patient = get_object_or_404(
        Patient,
        pk=patient_id
    )

    appointments = (
        Appointment.objects
        .filter(
            patient_id=patient.id
        )
        .exclude(
            status="Cancelled"
        )
        .select_related(
            "doctor"
        )
        .order_by(
            "-date",
            "-time"
        )
    )

    bills = (
        Bill.objects
        .filter(
            patient_id=patient.id
        )
        .select_related(
            "doctor"
        )
        .order_by(
            "-created_at"
        )[:10]
    )

    appointment_data = []

    for appointment in appointments:

        appointment_data.append({

            "id": appointment.id,

            "doctor_id": appointment.doctor_id,

            "doctor_name": (
                appointment.doctor.name
            ),

            "date": (
                appointment.date.strftime("%d-%m-%Y")
                if appointment.date
                else ""
            ),

            "time": (
                appointment.time.strftime("%I:%M %p")
                if appointment.time
                else ""
            ),

            "status": appointment.status,

        })

    bill_data = []

    for bill in bills:

        bill_data.append({

            "id": bill.id,

            "bill_number": bill.bill_number,

            "doctor": bill.doctor.name,

            "total": str(
                bill.total_amount
            ),

            "paid": str(
                bill.amount_paid
            ),

            "balance": str(
                bill.balance_amount
            ),

            "status": bill.payment_status,

            "date": (
                bill.payment_date.strftime(
                    "%d-%m-%Y"
                )
                if bill.payment_date
                else ""
            ),

        })

    return JsonResponse({

        "patient": {

            "id": patient.id,

            "patient_id": patient.patient_id,

            "name": patient.name,

        },

        "appointments": appointment_data,

        "bills": bill_data,

    })


# =========================================================
# DOCTOR CONSULTATION FEE
# =========================================================

@require_GET
def doctor_details(
    request,
    doctor_id
):

    doctor = get_object_or_404(
        Doctor,
        pk=doctor_id
    )

    return JsonResponse({

        "id": doctor.id,

        "doctor_id": doctor.doctor_id,

        "name": doctor.name,

        "specialization": doctor.specialization,

        "consultation_fee": str(
            doctor.consultation_fee
        )
    })


# =========================================================
# MEDICINE DETAILS
# =========================================================

@require_GET
def medicine_details(
    request,
    medicine_id
):

    medicine = get_object_or_404(
        Medicine,
        pk=medicine_id
    )

    return JsonResponse({

        "id": medicine.id,

        "name": medicine.medicine_name,

        "price": str(
            medicine.price
        ),

        "quantity": medicine.quantity,

        "out_of_stock": (
            medicine.quantity == 0
        )
    })


def billing_success(request, bill_id):

    bill = get_object_or_404(
        Bill.objects
        .select_related(
            "patient",
            "doctor"
        ),
        pk=bill_id
    )

    return render(
        request,
        "billing/bill_success.html",
        {
            "bill": bill
        }
    )
# =========================================================
# BILLING HISTORY
# =========================================================

def billing_history(request):

    bills = (
        Bill.objects
        .select_related(
            "patient",
            "doctor"
        )
        .all()
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    )

    if search:

        bills = bills.filter(

            Q(
                bill_number__icontains=search
            )

            | Q(
                patient__name__icontains=search
            )

            | Q(
                patient__patient_id__icontains=search
            )

            | Q(
                doctor__name__icontains=search
            )

            | Q(
                doctor__doctor_id__icontains=search
            )
        )

    if status:

        bills = bills.filter(
            payment_status=status
        )

    return render(

        request,

        "billing/history.html",

        {
            "bills": bills,

            "search": search,

            "selected_status": status,
        }
    )


# =========================================================
# BILL DETAILS
# =========================================================

def billing_detail(
    request,
    bill_id
):

    bill = get_object_or_404(

        Bill.objects
        .select_related(
            "patient",
            "doctor",
            "appointment"
        )
        .prefetch_related(
            "medicine_items__medicine"
        ),

        pk=bill_id
    )

    return render(

        request,

        "billing/detail.html",

        {
            "bill": bill
        }
    )


# =========================================================
# CANCEL BILL
# =========================================================

@require_POST
@transaction.atomic
def billing_cancel(
    request,
    bill_id
):

    bill = get_object_or_404(

        Bill.objects
        .select_for_update(),

        pk=bill_id
    )

    if bill.is_cancelled:

        messages.warning(
            request,
            "This bill is already cancelled."
        )

        return redirect(
            "billing:detail",
            bill_id=bill.id
        )

    medicine_items = (
        bill.medicine_items
        .select_related("medicine")
        .select_for_update()
    )

    # =========================================
    # RESTORE MEDICINE STOCK
    # =========================================

    for item in medicine_items:

        medicine = (
            Medicine.objects
            .select_for_update()
            .get(
                pk=item.medicine_id
            )
        )

        medicine.quantity += item.quantity

        medicine.save(
            update_fields=[
                "quantity",
                "updated_at"
            ]
        )

    # =========================================
    # CANCEL BILL
    # =========================================

    bill.is_cancelled = True

    bill.payment_status = "Cancelled"

    bill.cancelled_at = timezone.now()

    bill.save(
        update_fields=[
            "is_cancelled",
            "payment_status",
            "cancelled_at",
            "updated_at"
        ]
    )

    messages.success(
        request,
        f"Bill {bill.bill_number} cancelled successfully."
    )

    return redirect(
        "billing:detail",
        bill_id=bill.id
    )

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Bill


@login_required
def billing_history(request):
    bills = (
        Bill.objects
        .select_related("patient", "doctor", "appointment")
        .prefetch_related("medicine_items__medicine")
        .order_by("-created_at")
    )

    return render(
        request,
        "billing/billing_history.html",
        {
            "bills": bills,
        }
    )