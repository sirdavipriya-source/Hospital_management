from django.contrib import admin
from .models import MedicalRecord

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'created_at')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 'diagnosis', 'prescription')
    list_filter = ('created_at', 'doctor')
