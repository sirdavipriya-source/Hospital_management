from django import forms
from .models import Doctor
from departments.models import Department, Specialization

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'doctor_id', 'name', 'department', 'specialization_ref', 'qualification', 'experience',
            'phone', 'email', 'address', 'consultation_fee', 'availability', 'about_doctor',
            'profile_image', 'image_url', 'status', 'is_available'
        ]
        widgets = {
            'doctor_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DOC-001 (auto if blank)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'required': True}),
            'department': forms.Select(attrs={'class': 'form-select', 'id': 'id_department', 'required': True}),
            'specialization_ref': forms.Select(attrs={'class': 'form-select', 'id': 'id_specialization_ref'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MBBS, MD (Cardiology)', 'required': True}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of experience', 'min': '0'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'doctor@medcare.org', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Clinic / Residential Address'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'availability': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mon - Sat (09:00 AM - 05:00 PM)'}),
            'about_doctor': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Professional bio, clinical expertise, awards...'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

