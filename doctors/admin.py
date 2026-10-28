from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'department', 'phone', 'consultation_fee', 'is_available')
    list_filter = ('department', 'is_available', 'specialization')
    search_fields = ('name', 'specialization', 'qualification', 'phone', 'email')
