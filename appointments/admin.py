from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "appointment_id",
        "patient",
        "doctor",
        "date",
        "time",
        "status",
        "created_at",
    )

    search_fields = (
        "appointment_id",
        "patient__patient_id",
        "patient__name",
        "doctor__doctor_id",
        "doctor__name",
        "reason",
    )

    list_filter = (
        "status",
        "date",
        "doctor__specialization",
    )

    ordering = (
        "-date",
        "-time",
    )

    readonly_fields = (
        "appointment_id",
        "created_at",
        "updated_at",
    )

    date_hierarchy = "date"

    list_select_related = (
        "patient",
        "doctor",
    )

    fieldsets = (
        (
            "Appointment Information",
            {
                "fields": (
                    "appointment_id",
                    "patient",
                    "doctor",
                )
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "date",
                    "time",
                    "reason",
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