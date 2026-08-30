from django.contrib import admin
from .models import (
    Medicine,
    MedicineBill,
    MedicineBillItem,
)


# =========================================================
# MEDICINE BILL ITEM INLINE
# =========================================================

class MedicineBillItemInline(admin.TabularInline):

    model = MedicineBillItem

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


# =========================================================
# MEDICINE ADMIN
# =========================================================

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "medicine_name",
        "category",
        "manufacturer",
        "price",
        "quantity",
        "stock_status",
        "expiry_date",
        "created_at",
    )

    search_fields = (
        "medicine_name",
        "category",
        "manufacturer",
    )

    list_filter = (
        "category",
        "expiry_date",
    )

    ordering = (
        "medicine_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 25

    @admin.display(
        description="Stock Status",
        ordering="quantity",
    )
    def stock_status(self, obj):

        if obj.is_out_of_stock:
            return "Out of Stock"

        if obj.is_low_stock:
            return "Low Stock"

        return "In Stock"


# =========================================================
# MEDICINE BILL ADMIN
# =========================================================

@admin.register(MedicineBill)
class MedicineBillAdmin(admin.ModelAdmin):

    list_display = (
        "bill_number",
        "patient",
        "total_amount",
        "created_at",
    )

    search_fields = (
        "bill_number",
        "patient__patient_id",
        "patient__name",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "bill_number",
        "created_at",
    )

    list_select_related = (
        "patient",
    )

    inlines = (
        MedicineBillItemInline,
    )

    fieldsets = (
        (
            "Bill Information",
            {
                "fields": (
                    "bill_number",
                    "patient",
                    "total_amount",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )


# =========================================================
# MEDICINE BILL ITEM ADMIN
# =========================================================

@admin.register(MedicineBillItem)
class MedicineBillItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "bill",
        "medicine",
        "quantity",
        "unit_price",
        "total_price",
    )

    search_fields = (
        "bill__bill_number",
        "medicine__medicine_name",
        "medicine__manufacturer",
    )

    list_filter = (
        "medicine__category",
    )

    ordering = (
        "-id",
    )

    list_select_related = (
        "bill",
        "medicine",
    )