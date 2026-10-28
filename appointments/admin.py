from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'department', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'department', 'appointment_date')
    search_fields = ('patient__username', 'patient__first_name', 'patient__last_name', 'doctor__name', 'reason')
    ordering = ('-appointment_date', '-appointment_time')
