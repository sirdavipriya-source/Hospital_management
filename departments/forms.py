from django import forms
from .models import Department, Specialization

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'icon_class', 'image', 'image_url', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiology', 'required': True}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CARD-01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department overview...'}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. fa-heartbeat'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SpecializationForm(forms.ModelForm):
    class Meta:
        model = Specialization
        fields = ['name', 'code', 'department', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Interventional Cardiology', 'required': True}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SPEC-CRD-01'}),
            'department': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Specialization details and focus area...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

