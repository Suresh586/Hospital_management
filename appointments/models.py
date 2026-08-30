# from django.db import models

# Create your models here.
from django.db import models
from doctors.models import Doctor
from patients.models import Patient


class Appointment(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    appointment_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    date = models.DateField()

    time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-date", "-time"]

    def save(self, *args, **kwargs):

        if not self.appointment_id:
            last_appointment = Appointment.objects.order_by("-id").first()

            if last_appointment:
                number = last_appointment.id + 1
            else:
                number = 1

            self.appointment_id = f"AP-{number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.appointment_id} - {self.patient.name}"