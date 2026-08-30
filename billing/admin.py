from django.contrib import admin
from .models import Bill, BillMedicineItem


class BillMedicineItemInline(admin.TabularInline):

    model = BillMedicineItem

    extra = 0

    fields = (
        "medicine",
        "quantity",
        "unit_price",
        "total_price",
    )

    readonly_fields = (
        "total_price",
    )


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):

    list_display = (
        "bill_number",
        "patient",
        "doctor",
        "total_amount",
        "amount_paid",
        "balance_display",
        "payment_status",
        "payment_method",
        "payment_date",
        "created_at",
    )

    search_fields = (
        "bill_number",
        "patient__patient_id",
        "patient__name",
        "doctor__doctor_id",
        "doctor__name",
    )

    list_filter = (
        "payment_status",
        "payment_method",
        "payment_date",
        "is_cancelled",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "bill_number",
        "total_amount",
        "created_at",
        "updated_at",
        "cancelled_at",
    )

    list_select_related = (
        "patient",
        "doctor",
        "appointment",
    )

    inlines = (
        BillMedicineItemInline,
    )

    fieldsets = (
        (
            "Bill Information",
            {
                "fields": (
                    "bill_number",
                    "patient",
                    "doctor",
                    "appointment",
                    "payment_date",
                )
            },
        ),
        (
            "Charges",
            {
                "fields": (
                    "consultation_fee",
                    "medicine_charges",
                    "lab_charges",
                    "room_charges",
                    "total_amount",
                )
            },
        ),
        (
            "Payment",
            {
                "fields": (
                    "amount_paid",
                    "payment_status",
                    "payment_method",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
                    "is_cancelled",
                    "cancelled_at",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(
        description="Balance",
        ordering="total_amount",
    )
    def balance_display(self, obj):
        return obj.balance_amount