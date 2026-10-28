from django import forms
from django.forms import inlineformset_factory
from .models import Medicine, MedicineCategory, Prescription, PrescriptionItem
from doctors.models import Doctor
from departments.models import Department

class MedicineCategoryForm(forms.ModelForm):
    class Meta:
        model = MedicineCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Antibiotics', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Category description...'}),
        }


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'medicine_id', 'name', 'generic_name', 'category', 'manufacturer',
            'batch_number', 'quantity', 'unit_price', 'expiry_date', 'description', 'status'
        ]
        widgets = {
            'medicine_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MED-001 (auto if empty)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amoxicillin 500mg', 'required': True}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amoxicillin Trihydrate'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Pfizer / Sun Pharma'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BATCH-2026-X'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'required': True}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'required': True}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Usage indications, side effects, storage info...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            'prescription_id', 'patient_name', 'patient_id_number', 'patient_age', 'patient_gender',
            'doctor', 'department', 'prescription_date', 'diagnosis', 'notes', 'status'
        ]
        widgets = {
            'prescription_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RX-2026-001 (auto if empty)'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient Full Name', 'required': True}),
            'patient_id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. PAT-001'}),
            'patient_age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age', 'min': '1'}),
            'patient_gender': forms.Select(choices=[('', '-- Select --'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'prescription_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical symptoms, findings, and diagnosis...', 'required': True}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Doctor advice, precautions, follow-up recommendations...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medicine', 'dosage', 'frequency', 'duration', 'quantity', 'instructions']
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-select medicine-select', 'required': True}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500mg / 1 tab'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1-0-1 (Morning & Night)'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5 Days'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Units'}),
            'instructions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. After food'}),
        }

PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True
)
