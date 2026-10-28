from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from django.http import JsonResponse
import datetime

from .models import Medicine, MedicineCategory, Prescription, PrescriptionItem
from .forms import MedicineForm, MedicineCategoryForm, PrescriptionForm, PrescriptionItemFormSet
from doctors.models import Doctor
from departments.models import Department

# ==========================================
# MEDICINE CRUD & MANAGEMENT
# ==========================================

@login_required
def medicine_list_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user) or (hasattr(request.user, 'profile') and request.user.profile.is_doctor)):
        messages.error(request, "Access restricted to authorized personnel.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')

    medicines = Medicine.objects.select_related('category').all()

    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(generic_name__icontains=search_query) |
            Q(medicine_id__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(batch_number__icontains=search_query)
        )

    if category_id:
        medicines = medicines.filter(category_id=category_id)

    today = datetime.date.today()
    if status_filter == 'low_stock':
        medicines = medicines.filter(quantity__gt=0, quantity__lt=15)
    elif status_filter == 'out_of_stock':
        medicines = medicines.filter(quantity=0)
    elif status_filter == 'expired':
        medicines = medicines.filter(expiry_date__lt=today)
    elif status_filter == 'in_stock':
        medicines = medicines.filter(quantity__gte=15, expiry_date__gte=today)

    categories = MedicineCategory.objects.all()
    form = MedicineForm()
    category_form = MedicineCategoryForm()

    # Quick metrics
    total_meds = Medicine.objects.count()
    low_stock_count = Medicine.objects.filter(quantity__gt=0, quantity__lt=15).count()
    expired_count = Medicine.objects.filter(expiry_date__lt=today).count()
    out_stock_count = Medicine.objects.filter(quantity=0).count()

    return render(request, 'pharmacy/medicine_list.html', {
        'medicines': medicines,
        'categories': categories,
        'form': form,
        'category_form': category_form,
        'search_query': search_query,
        'selected_category': category_id,
        'status_filter': status_filter,
        'total_meds': total_meds,
        'low_stock_count': low_stock_count,
        'expired_count': expired_count,
        'out_stock_count': out_stock_count,
        'today': today,
    })


@login_required
def medicine_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('medicine_list')

    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            med = form.save()
            messages.success(request, f"Medicine '{med.name}' ({med.medicine_id}) added to inventory successfully!")
            return redirect('medicine_list')
        else:
            messages.error(request, "Error adding medicine. Please check the inputs.")
    else:
        form = MedicineForm()

    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Add New Medicine to Pharmacy'})


@login_required
def medicine_update_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('medicine_list')

    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, f"Medicine '{medicine.name}' updated successfully!")
            return redirect('medicine_list')
        else:
            messages.error(request, "Error updating medicine.")
    else:
        form = MedicineForm(instance=medicine)

    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'medicine': medicine, 'title': f'Edit Medicine: {medicine.name}'})


@login_required
def medicine_delete_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('medicine_list')

    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        name = medicine.name
        medicine.delete()
        messages.success(request, f"Medicine '{name}' removed from inventory.")
        return redirect('medicine_list')

    return render(request, 'pharmacy/medicine_confirm_delete.html', {'medicine': medicine})


@login_required
def category_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('medicine_list')

    if request.method == 'POST':
        form = MedicineCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Category '{cat.name}' created successfully.")
        else:
            messages.error(request, "Error creating category.")
    return redirect('medicine_list')


# ==========================================
# PRESCRIPTION CRUD & MULTI-MEDICINE MANAGEMENT
# ==========================================

@login_required
def prescription_list_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user) or (hasattr(request.user, 'profile') and request.user.profile.is_doctor)):
        messages.error(request, "Access restricted to medical & admin personnel.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    doctor_id = request.GET.get('doctor', '')
    department_id = request.GET.get('department', '')
    date_filter = request.GET.get('date', '')

    prescriptions = Prescription.objects.select_related('doctor', 'department').prefetch_related('items__medicine').all()

    if search_query:
        prescriptions = prescriptions.filter(
            Q(prescription_id__icontains=search_query) |
            Q(patient_name__icontains=search_query) |
            Q(patient_id_number__icontains=search_query) |
            Q(doctor__name__icontains=search_query) |
            Q(diagnosis__icontains=search_query)
        )

    if doctor_id:
        prescriptions = prescriptions.filter(doctor_id=doctor_id)

    if department_id:
        prescriptions = prescriptions.filter(department_id=department_id)

    if date_filter:
        prescriptions = prescriptions.filter(prescription_date=date_filter)

    doctors = Doctor.objects.all()
    departments = Department.objects.all()
    medicines = Medicine.objects.filter(quantity__gt=0)

    return render(request, 'pharmacy/prescription_list.html', {
        'prescriptions': prescriptions,
        'doctors': doctors,
        'departments': departments,
        'medicines': medicines,
        'search_query': search_query,
        'selected_doctor': doctor_id,
        'selected_department': department_id,
        'date_filter': date_filter,
    })


@login_required
def prescription_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user) or (hasattr(request.user, 'profile') and request.user.profile.is_doctor)):
        messages.error(request, "Access restricted.")
        return redirect('home')

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            prescription = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.prescription = prescription
                item.save()
                # Deduct stock if available
                if item.medicine and item.quantity:
                    med = item.medicine
                    if med.quantity >= item.quantity:
                        med.quantity = F('quantity') - item.quantity
                        med.save(update_fields=['quantity'])
            
            formset.save_m2m()
            messages.success(request, f"Prescription #{prescription.prescription_id} created successfully for {prescription.patient_name}!")
            return redirect('prescription_detail', pk=prescription.pk)
        else:
            messages.error(request, "Error saving prescription. Please ensure patient name, doctor, and at least one medicine item are provided.")
    else:
        form = PrescriptionForm(initial={'prescription_date': datetime.date.today()})
        formset = PrescriptionItemFormSet()

    medicines = Medicine.objects.filter(quantity__gt=0)
    doctors = Doctor.objects.filter(is_available=True)
    departments = Department.objects.filter(is_active=True)

    return render(request, 'pharmacy/prescription_form.html', {
        'form': form,
        'formset': formset,
        'medicines': medicines,
        'doctors': doctors,
        'departments': departments,
        'title': 'Create New Patient Prescription'
    })


@login_required
def prescription_update_view(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user) or (prescription.doctor.user == request.user)):
        messages.error(request, "Permission denied.")
        return redirect('prescription_list')

    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        formset = PrescriptionItemFormSet(request.POST, instance=prescription)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"Prescription #{prescription.prescription_id} updated successfully!")
            return redirect('prescription_detail', pk=prescription.pk)
        else:
            messages.error(request, "Error updating prescription.")
    else:
        form = PrescriptionForm(instance=prescription)
        formset = PrescriptionItemFormSet(instance=prescription)

    medicines = Medicine.objects.all()
    doctors = Doctor.objects.all()
    departments = Department.objects.all()

    return render(request, 'pharmacy/prescription_form.html', {
        'form': form,
        'formset': formset,
        'prescription': prescription,
        'medicines': medicines,
        'doctors': doctors,
        'departments': departments,
        'title': f'Edit Prescription: #{prescription.prescription_id}'
    })


@login_required
def prescription_detail_view(request, pk):
    """Clean, printable prescription view with hospital header, QR/Rx details, medicine dosages, instructions, and doctor signature block."""
    prescription = get_object_or_404(Prescription.objects.select_related('doctor', 'department', 'doctor__department'), pk=pk)
    items = prescription.items.select_related('medicine').all()
    return render(request, 'pharmacy/prescription_detail.html', {
        'prescription': prescription,
        'items': items,
    })


@login_required
def prescription_delete_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('prescription_list')

    prescription = get_object_or_404(Prescription, pk=pk)
    if request.method == 'POST':
        rx_id = prescription.prescription_id
        prescription.delete()
        messages.success(request, f"Prescription #{rx_id} deleted successfully.")
        return redirect('prescription_list')

    return render(request, 'pharmacy/prescription_confirm_delete.html', {'prescription': prescription})
