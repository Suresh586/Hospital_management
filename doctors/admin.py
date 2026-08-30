from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):

    list_display = (
        "doctor_id",
        "name",
        "specialization",
        "qualification",
        "experience",
        "consultation_fee",
        "phone",
        "status",
    )

    search_fields = (
        "doctor_id",
        "name",
        "email",
        "phone",
        "specialization",
        "qualification",
    )

    list_filter = (
        "specialization",
        "status",
        "experience",
    )

    ordering = ("name",)

    readonly_fields = (
        "doctor_id",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Doctor Information",
            {
                "fields": (
                    "doctor_id",
                    "name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Professional Information",
            {
                "fields": (
                    "specialization",
                    "qualification",
                    "experience",
                    "consultation_fee",
                )
            },
        ),
        (
            "Availability",
            {
                "fields": (
                    "available_days",
                    "start_time",
                    "end_time",
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