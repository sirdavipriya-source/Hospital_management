from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from doctors.models import Doctor
from departments.models import Department

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
    )

    TIME_SLOT_CHOICES = (
        ('09:00:00', '09:00 AM'),
        ('09:30:00', '09:30 AM'),
        ('10:00:00', '10:00 AM'),
        ('10:30:00', '10:30 AM'),
        ('11:00:00', '11:00 AM'),
        ('11:30:00', '11:30 AM'),
        ('12:00:00', '12:00 PM'),
        ('14:00:00', '02:00 PM'),
        ('14:30:00', '02:30 PM'),
        ('15:00:00', '03:00 PM'),
        ('15:30:00', '03:30 PM'),
        ('16:00:00', '04:00 PM'),
        ('16:30:00', '04:30 PM'),
        ('17:00:00', '05:00 PM'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=255, help_text="Primary reason for consultation")
    symptoms = models.TextField(blank=True, null=True, help_text="Describe any current symptoms")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"Appointment #{self.id} - {self.patient.get_full_name() or self.patient.username} with Dr. {self.doctor.name} on {self.appointment_date}"

    def clean(self):
        super().clean()
        if self.doctor and self.appointment_date and self.appointment_time:
            # Check for double booking collision for active appointments
            collision = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time
            ).exclude(status__in=['Cancelled', 'Rejected'])
            
            if self.pk:
                collision = collision.exclude(pk=self.pk)
                
            if collision.exists():
                raise ValidationError(
                    f"Dr. {self.doctor.name} is already booked at {self.appointment_time.strftime('%I:%M %p')} on {self.appointment_date}. Please select another time slot."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
