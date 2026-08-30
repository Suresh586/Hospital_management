

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Medicine(models.Model):
    medicine_name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=150)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["medicine_name"]

    def __str__(self):
        return f"{self.medicine_name} - {self.category}"

    @property
    def is_low_stock(self):
        return self.quantity < 10

    @property
    def is_out_of_stock(self):
        return self.quantity == 0
    
    from django.db import models


class MedicineBill(models.Model):
    bill_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="medicine_bills"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if not self.bill_number:
            last_bill = MedicineBill.objects.order_by("-id").first()

            if last_bill:
                next_id = last_bill.id + 1
            else:
                next_id = 1

            self.bill_number = f"BILL-{next_id:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.bill_number


class MedicineBillItem(models.Model):

    bill = models.ForeignKey(
        MedicineBill,
        on_delete=models.CASCADE,
        related_name="items"
    )

    medicine = models.ForeignKey(
        "pharmacy.Medicine",
        on_delete=models.PROTECT,
        related_name="bill_items"
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.medicine.medicine_name} - {self.quantity}"