from django.contrib import admin
from .models import Medicine, MedicineCategory, Prescription, PrescriptionItem

@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('medicine_id', 'name', 'generic_name', 'category', 'quantity', 'unit_price', 'expiry_date', 'status')
    list_filter = ('status', 'category', 'expiry_date')
    search_fields = ('medicine_id', 'name', 'generic_name', 'manufacturer', 'batch_number')

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('prescription_id', 'patient_name', 'doctor', 'department', 'prescription_date', 'status')
    list_filter = ('status', 'doctor', 'department', 'prescription_date')
    search_fields = ('prescription_id', 'patient_name', 'patient_id_number', 'doctor__name')
    inlines = [PrescriptionItemInline]
