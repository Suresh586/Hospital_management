from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        "patient_id",
        "name",
        "gender",
        "date_of_birth",
        "blood_group",
        "phone",
        "status",
        "created_at",
    )

    search_fields = (
        "patient_id",
        "name",
        "email",
        "phone",
        "blood_group",
    )

    list_filter = (
        "gender",
        "blood_group",
        "status",
        "date_of_birth",
    )

    ordering = ("name",)

    readonly_fields = (
        "patient_id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Patient Information",
            {
                "fields": (
                    "patient_id",
                    "name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "gender",
                    "date_of_birth",
                    "blood_group",
                    "address",
                )
            },
        ),
        (
            "Emergency Contact",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
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