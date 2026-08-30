from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Bill(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Partial", "Partial"),
        ("Cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("UPI", "UPI"),
        ("Insurance", "Insurance"),
        ("Other", "Other"),
    ]

    bill_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="hospital_bills"
    )

    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.PROTECT,
        related_name="hospital_bills"
    )

    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="billing_records"
    )

    payment_date = models.DateField(
        null=True,
        blank=True
    )

    consultation_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    medicine_charges = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    lab_charges = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    room_charges = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    is_cancelled = models.BooleanField(
        default=False
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.bill_number:

            last_bill = (
                Bill.objects
                .order_by("-id")
                .first()
            )

            if last_bill:
                next_number = last_bill.id + 1
            else:
                next_number = 1

            self.bill_number = (
                f"CP-BILL-{next_number:05d}"
            )

        self.total_amount = (
            self.consultation_fee
            + self.medicine_charges
            + self.lab_charges
            + self.room_charges
        )

        super().save(*args, **kwargs)

    @property
    def balance_amount(self):

        balance = (
            self.total_amount
            - self.amount_paid
        )

        return max(
            balance,
            Decimal("0.00")
        )

    def clean(self):

        if self.amount_paid > self.total_amount:

            raise ValidationError(
                "Amount paid cannot be greater than total amount."
            )

        if self.payment_status == "Paid":

            if self.amount_paid != self.total_amount:

                raise ValidationError(
                    "Paid bill must have the complete amount paid."
                )

        if self.payment_status == "Pending":

            if self.amount_paid != Decimal("0.00"):

                raise ValidationError(
                    "Pending bill cannot have an amount paid."
                )

        if self.payment_status == "Partial":

            if not (
                Decimal("0.00")
                < self.amount_paid
                < self.total_amount
            ):

                raise ValidationError(
                    "Partial payment must be between 0 and total amount."
                )


class BillMedicineItem(models.Model):

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="medicine_items"
    )

    medicine = models.ForeignKey(
        "pharmacy.Medicine",
        on_delete=models.PROTECT,
        related_name="hospital_bill_items"
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def save(self, *args, **kwargs):

        self.total_price = (
            self.unit_price
            * self.quantity
        )

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.medicine.medicine_name} "
            f"x {self.quantity}"
        )
