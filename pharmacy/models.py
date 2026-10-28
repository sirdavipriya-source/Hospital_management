from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor
from departments.models import Department
import datetime

class MedicineCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Medicine Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Medicine(models.Model):
    STATUS_CHOICES = (
        ('In Stock', 'In Stock'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
        ('Expired', 'Expired'),
    )

    medicine_id = models.CharField(max_length=30, unique=True, blank=True, null=True, help_text="e.g. MED-1001")
    name = models.CharField(max_length=200, help_text="Brand / Trade name")
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(MedicineCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicines')
    category_name = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Antibiotic, Analgesic, Antipyretic")
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, help_text="Available stock units")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expiry_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='In Stock')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.medicine_id or 'MED'}) - Stock: {self.quantity}"

    def save(self, *args, **kwargs):
        # Auto-compute status
        if self.expiry_date and self.expiry_date < datetime.date.today():
            self.status = 'Expired'
        elif self.quantity == 0:
            self.status = 'Out of Stock'
        elif self.quantity < 15:
            self.status = 'Low Stock'
        else:
            self.status = 'In Stock'

        if self.category and not self.category_name:
            self.category_name = self.category.name

        super().save(*args, **kwargs)
        if not self.medicine_id:
            self.medicine_id = f"MED-{self.pk:04d}"
            Medicine.objects.filter(pk=self.pk).update(medicine_id=self.medicine_id)

    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < datetime.date.today())

    @property
    def is_low_stock(self):
        return self.quantity > 0 and self.quantity < 15


class Prescription(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    prescription_id = models.CharField(max_length=30, unique=True, blank=True, null=True, help_text="e.g. RX-2026-001")
    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    patient_name = models.CharField(max_length=150, help_text="Patient Full Name")
    patient_id_number = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. PAT-001")
    patient_age = models.PositiveIntegerField(blank=True, null=True)
    patient_gender = models.CharField(max_length=10, blank=True, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions_written')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    prescription_date = models.DateField(default=datetime.date.today)
    diagnosis = models.TextField(help_text="Clinical findings and diagnosis")
    notes = models.TextField(blank=True, null=True, help_text="Doctor advice, dietary recommendations, follow-up date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-prescription_date', '-created_at']

    def __str__(self):
        return f"Prescription #{self.prescription_id or self.pk} - {self.patient_name} by Dr. {self.doctor.name}"

    def save(self, *args, **kwargs):
        if not self.department and self.doctor and self.doctor.department:
            self.department = self.doctor.department
        if self.patient and not self.patient_name:
            self.patient_name = self.patient.get_full_name() or self.patient.username
        super().save(*args, **kwargs)
        if not self.prescription_id:
            self.prescription_id = f"RX-{datetime.date.today().year}-{self.pk:04d}"
            Prescription.objects.filter(pk=self.pk).update(prescription_id=self.prescription_id)


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='prescription_items')
    dosage = models.CharField(max_length=100, help_text="e.g. 500 mg, 1 tablet, 5 ml")
    frequency = models.CharField(max_length=100, default="1-0-1", help_text="e.g. 1-0-1 (Morning & Night), 1-1-1, Once Daily")
    duration = models.CharField(max_length=100, default="5 days", help_text="e.g. 5 days, 2 weeks")
    quantity = models.PositiveIntegerField(default=10, help_text="Number of units to dispense")
    instructions = models.CharField(max_length=255, default="After food", help_text="e.g. After food, Before food, With warm water")

    def __str__(self):
        return f"{self.medicine.name} - {self.dosage} ({self.frequency})"
