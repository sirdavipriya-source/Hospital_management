from django.db import models
from django.contrib.auth.models import User
from departments.models import Department, Specialization

class Doctor(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    )

    doctor_id = models.CharField(max_length=30, unique=True, blank=True, null=True, help_text="e.g. DOC-001")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    specialization_ref = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    specialization = models.CharField(max_length=150, blank=True)
    qualification = models.CharField(max_length=200, help_text="e.g. MBBS, MD (Cardiology)")
    experience = models.PositiveIntegerField(help_text="Years of clinical experience", default=5)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    availability = models.CharField(max_length=200, default="Mon - Sat (09:00 AM - 05:00 PM)")
    about_doctor = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Reliable remote photo fallback")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        spec = self.specialization_ref.name if self.specialization_ref else self.specialization
        return f"Dr. {self.name} - {spec}"

    def save(self, *args, **kwargs):
        if not self.doctor_id and self.pk:
            self.doctor_id = f"DOC-{self.pk:04d}"
        if self.specialization_ref and not self.specialization:
            self.specialization = self.specialization_ref.name
        super().save(*args, **kwargs)
        if not self.doctor_id:
            self.doctor_id = f"DOC-{self.pk:04d}"
            Doctor.objects.filter(pk=self.pk).update(doctor_id=self.doctor_id)

    @property
    def get_specialization_name(self):
        if self.specialization_ref:
            return self.specialization_ref.name
        return self.specialization or "General"

    @property
    def get_photo(self):
        if self.profile_image:
            return self.profile_image.url
        elif self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&w=800&q=80'

