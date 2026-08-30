

# Create your views here.
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Medicine
from patients.models import Patient
from .models import Medicine, MedicineBill, MedicineBillItem



# =========================================================
# MEDICINE LIST
# =========================================================

def medicine_list(request):
    medicines = Medicine.objects.all()

    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    stock_filter = request.GET.get("stock", "").strip()
    expiry_filter = request.GET.get("expiry", "").strip()

    if search:
        medicines = medicines.filter(
            medicine_name__icontains=search
        ) | medicines.filter(
            manufacturer__icontains=search
        ) | medicines.filter(
            category__icontains=search
        )

    if category:
        medicines = medicines.filter(category=category)

    if stock_filter == "low":
        medicines = medicines.filter(quantity__lt=10, quantity__gt=0)

    elif stock_filter == "out":
        medicines = medicines.filter(quantity=0)

    elif stock_filter == "available":
        medicines = medicines.filter(quantity__gt=0)

    today = timezone.localdate()

    if expiry_filter == "expired":
        medicines = medicines.filter(expiry_date__lt=today)

    elif expiry_filter == "expiring":
        medicines = medicines.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=30)
        )

    categories = (
        Medicine.objects
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    all_medicines = Medicine.objects.all()

    context = {
        "medicines": medicines,
        "categories": categories,
        "search": search,
        "selected_category": category,
        "selected_stock": stock_filter,
        "selected_expiry": expiry_filter,

        "total_medicines": all_medicines.count(),
        "low_stock_count": all_medicines.filter(
            quantity__lt=10,
            quantity__gt=0
        ).count(),
        "out_of_stock_count": all_medicines.filter(
            quantity=0
        ).count(),
        "expired_count": all_medicines.filter(
            expiry_date__lt=today
        ).count(),
    }

    return render(
        request,
        "pharmacy/medicine_list.html",
        context
    )


# =========================================================
# ADD MEDICINE
# =========================================================

def medicine_add(request):

    if request.method == "POST":

        medicine_name = request.POST.get("medicine_name", "").strip()
        category = request.POST.get("category", "").strip()
        manufacturer = request.POST.get("manufacturer", "").strip()
        price = request.POST.get("price", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        expiry_date = request.POST.get("expiry_date", "").strip()

        if not all([
            medicine_name,
            category,
            manufacturer,
            price,
            quantity,
            expiry_date
        ]):
            messages.error(
                request,
                "Please fill in all medicine details."
            )

            return render(
                request,
                "pharmacy/medicine_form.html",
                {"page_title": "Add Medicine"}
            )

        try:
            price_value = Decimal(price)
            quantity_value = int(quantity)

            if price_value < 0:
                raise ValueError

            if quantity_value < 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter valid price and quantity."
            )

            return render(
                request,
                "pharmacy/medicine_form.html",
                {"page_title": "Add Medicine"}
            )

        Medicine.objects.create(
            medicine_name=medicine_name,
            category=category,
            manufacturer=manufacturer,
            price=price_value,
            quantity=quantity_value,
            expiry_date=expiry_date,
        )

        messages.success(
            request,
            f"{medicine_name} added successfully."
        )

        return redirect("medicine_list")

    return render(
        request,
        "pharmacy/medicine_form.html",
        {
            "page_title": "Add Medicine",
            "medicine": None,
        }
    )


# =========================================================
# UPDATE MEDICINE
# =========================================================

def medicine_update(request, pk):

    medicine = get_object_or_404(
        Medicine,
        pk=pk
    )

    if request.method == "POST":

        medicine_name = request.POST.get("medicine_name", "").strip()
        category = request.POST.get("category", "").strip()
        manufacturer = request.POST.get("manufacturer", "").strip()
        price = request.POST.get("price", "").strip()
        quantity = request.POST.get("quantity", "").strip()
        expiry_date = request.POST.get("expiry_date", "").strip()

        if not all([
            medicine_name,
            category,
            manufacturer,
            price,
            quantity,
            expiry_date
        ]):
            messages.error(
                request,
                "Please fill in all medicine details."
            )

            return render(
                request,
                "pharmacy/medicine_form.html",
                {
                    "page_title": "Update Medicine",
                    "medicine": medicine,
                }
            )

        try:
            price_value = Decimal(price)
            quantity_value = int(quantity)

            if price_value < 0 or quantity_value < 0:
                raise ValueError

        except (ValueError, TypeError):
            messages.error(
                request,
                "Please enter valid price and quantity."
            )

            return render(
                request,
                "pharmacy/medicine_form.html",
                {
                    "page_title": "Update Medicine",
                    "medicine": medicine,
                }
            )

        medicine.medicine_name = medicine_name
        medicine.category = category
        medicine.manufacturer = manufacturer
        medicine.price = price_value
        medicine.quantity = quantity_value
        medicine.expiry_date = expiry_date

        medicine.save()

        messages.success(
            request,
            f"{medicine_name} updated successfully."
        )

        return redirect("medicine_list")

    return render(
        request,
        "pharmacy/medicine_form.html",
        {
            "page_title": "Update Medicine",
            "medicine": medicine,
        }
    )


# =========================================================
# DELETE MEDICINE
# =========================================================

def medicine_delete(request, pk):

    medicine = get_object_or_404(
        Medicine,
        pk=pk
    )

    if request.method == "POST":

        medicine_name = medicine.medicine_name

        medicine.delete()

        messages.success(
            request,
            f"{medicine_name} deleted successfully."
        )

        return redirect("medicine_list")

    return render(
        request,
        "pharmacy/medicine_confirm_delete.html",
        {"medicine": medicine}
    )


# =========================================================
# MEDICINE BILLING
# =========================================================

def medicine_billing(request):

    patients = Patient.objects.all().order_by("name")

    medicines = Medicine.objects.filter(
        quantity__gt=0
    ).order_by("medicine_name")

    if request.method == "POST":

        patient_id = request.POST.get("patient_id")

        medicine_ids = request.POST.getlist("medicine_id")
        quantities = request.POST.getlist("billing_quantity")

        # ================= PATIENT VALIDATION =================

        if not patient_id:
            messages.error(
                request,
                "Please select a patient."
            )

            return redirect("medicine_billing")

        try:
            patient = Patient.objects.get(
                pk=patient_id
            )

        except Patient.DoesNotExist:
            messages.error(
                request,
                "Selected patient does not exist."
            )

            return redirect("medicine_billing")


        # ================= MEDICINE VALIDATION =================

        if not medicine_ids:
            messages.error(
                request,
                "Please add at least one medicine to the bill."
            )

            return redirect("medicine_billing")


        total = Decimal("0.00")
        bill_items = []


        try:

            with transaction.atomic():

                # =============================================
                # CREATE BILL
                # =============================================

                bill = MedicineBill.objects.create(
                    patient=patient,
                    total_amount=Decimal("0.00")
                )


                # =============================================
                # PROCESS MEDICINES
                # =============================================

                for medicine_id, quantity in zip(
                    medicine_ids,
                    quantities
                ):

                    if not medicine_id:
                        continue

                    try:
                        quantity = int(quantity)

                    except (TypeError, ValueError):
                        raise ValueError(
                            "Please enter a valid medicine quantity."
                        )


                    if quantity <= 0:
                        raise ValueError(
                            "Medicine quantity must be greater than zero."
                        )


                    # Lock medicine row while billing
                    medicine = Medicine.objects.select_for_update().get(
                        pk=medicine_id
                    )


                    # =========================================
                    # STOCK CHECK
                    # =========================================

                    if medicine.quantity < quantity:

                        raise ValueError(
                            f"Only {medicine.quantity} units of "
                            f"{medicine.medicine_name} are available."
                        )


                    # =========================================
                    # CALCULATE TOTAL
                    # =========================================

                    unit_price = medicine.price

                    item_total = unit_price * quantity

                    total += item_total


                    # =========================================
                    # CREATE BILL ITEM
                    # =========================================

                    MedicineBillItem.objects.create(

                        bill=bill,

                        medicine=medicine,

                        quantity=quantity,

                        unit_price=unit_price,

                        total_price=item_total
                    )


                    # =========================================
                    # REDUCE STOCK
                    # =========================================

                    medicine.quantity -= quantity

                    medicine.save(
                        update_fields=[
                            "quantity",
                            "updated_at"
                        ]
                    )


                    # =========================================
                    # SUCCESS PAGE DATA
                    # =========================================

                    bill_items.append({

                        "medicine": medicine,

                        "quantity": quantity,

                        "price": unit_price,

                        "total": item_total,
                    })


                # =============================================
                # VALIDATE BILL
                # =============================================

                if not bill_items:

                    raise ValueError(
                        "Please add at least one valid medicine to the bill."
                    )


                # =============================================
                # UPDATE BILL TOTAL
                # =============================================

                bill.total_amount = total

                bill.save(
                    update_fields=[
                        "total_amount"
                    ]
                )


        # =============================================
        # ERROR HANDLING
        # =============================================

        except Medicine.DoesNotExist:

            messages.error(
                request,
                "One of the selected medicines no longer exists."
            )

            return redirect("medicine_billing")


        except ValueError as error:

            messages.error(
                request,
                str(error)
            )

            return redirect("medicine_billing")


        # =============================================
        # SUCCESS PAGE
        # =============================================

        context = {

            "bill": bill,

            "patient": patient,

            "bill_number": bill.bill_number,

            "bill_items": bill_items,

            "total": total,

            "bill_date": timezone.localdate(),

        }


        return render(
            request,
            "pharmacy/bill_success.html",
            context
        )


    # =============================================
    # BILLING PAGE
    # =============================================

    return render(
        request,
        "pharmacy/medicine_billing.html",
        {
            "patients": patients,
            "medicines": medicines,
        }
    )