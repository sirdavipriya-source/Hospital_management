from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor

class MedicalRecord(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='medical_records_given')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record')
    diagnosis = models.TextField(help_text="Detailed diagnosis & medical findings")
    prescription = models.TextField(help_text="Prescribed medicines, dosages, and administration timing")
    medical_notes = models.TextField(blank=True, null=True, help_text="Additional doctor notes or recommended tests")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Record for {self.patient.get_full_name() or self.patient.username} - {self.created_at.strftime('%Y-%m-%d')}"
