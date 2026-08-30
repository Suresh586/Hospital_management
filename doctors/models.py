from django.db import models


class Doctor(models.Model):

    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Unavailable", "Unavailable"),
        ("On Leave", "On Leave"),
    ]

    SPECIALIZATION_CHOICES = [
        ("Cardiology", "Cardiology"),
        ("Neurology", "Neurology"),
        ("Orthopedics", "Orthopedics"),
        ("Dermatology", "Dermatology"),
        ("Pediatrics", "Pediatrics"),
        ("General Medicine", "General Medicine"),
        ("ENT", "ENT"),
        ("Gynecology", "Gynecology"),
        ("Ophthalmology", "Ophthalmology"),
        ("Dentistry", "Dentistry"),
        ("Other", "Other"),
    ]

    doctor_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15
    )

    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES
    )

    qualification = models.CharField(
        max_length=150
    )

    experience = models.PositiveIntegerField(
        help_text="Experience in years"
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    available_days = models.CharField(
        max_length=100,
        help_text="Example: Mon, Tue, Wed, Thu, Fri"
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Available"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):

        if not self.doctor_id:

            last_doctor = (
                Doctor.objects
                .filter(doctor_id__startswith="DOC-")
                .order_by("-id")
                .first()
            )

            if last_doctor:
                try:
                    last_number = int(
                        last_doctor.doctor_id.split("-")[1]
                    )
                except (ValueError, IndexError):
                    last_number = 0
            else:
                last_number = 0

            self.doctor_id = f"DOC-{last_number + 1:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor_id} - {self.name}"
