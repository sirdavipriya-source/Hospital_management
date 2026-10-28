from django import forms
from .models import Appointment
from doctors.models import Doctor
from departments.models import Department
import datetime

class AppointmentBookingForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': datetime.date.today().strftime('%Y-%m-%d'),
            'id': 'id_appointment_date'
        })
    )
    appointment_time = forms.ChoiceField(
        choices=Appointment.TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_appointment_time'
        })
    )

    class Meta:
        model = Appointment
        fields = ['department', 'doctor', 'appointment_date', 'appointment_time', 'reason', 'symptoms']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select', 'id': 'id_department'}),
            'doctor': forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Regular Checkup / Chest Pain / Routine Consultation'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of symptoms...'}),
        }

    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        doctor_id = kwargs.pop('doctor_id', None)
        super().__init__(*args, **kwargs)

        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_available=True)

        if department_id:
            self.fields['department'].initial = department_id
            self.fields['doctor'].queryset = Doctor.objects.filter(department_id=department_id, is_available=True)

        if doctor_id:
            try:
                doctor = Doctor.objects.get(pk=doctor_id)
                self.fields['doctor'].initial = doctor_id
                self.fields['department'].initial = doctor.department_id
            except Doctor.DoesNotExist:
                pass


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }


class DiagnosisPrescriptionForm(forms.Form):
    diagnosis = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical diagnosis & observations...'}),
        required=True
    )
    prescription = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Prescribed medicines, dosages, and instructions...'}),
        required=True
    )
    medical_notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dietary instructions, follow-up date, or test recommendations...'}),
        required=False
    )
