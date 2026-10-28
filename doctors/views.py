from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Doctor
from .forms import DoctorForm
from departments.models import Department, Specialization

def doctor_list_view(request):
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    specialization = request.GET.get('specialization', '')
    
    doctors = Doctor.objects.select_related('department', 'specialization_ref').filter(is_available=True)
    
    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(doctor_id__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(specialization_ref__name__icontains=search_query) |
            Q(qualification__icontains=search_query)
        )
        
    if department_id:
        doctors = doctors.filter(department_id=department_id)
        
    if specialization:
        doctors = doctors.filter(Q(specialization__icontains=specialization) | Q(specialization_ref__name__icontains=specialization))
        
    departments = Department.objects.filter(is_active=True)
    specializations = Specialization.objects.filter(is_active=True)
    
    return render(request, 'doctors/doctor_list.html', {
        'doctors': doctors,
        'departments': departments,
        'specializations': specializations,
        'search_query': search_query,
        'selected_department': department_id,
        'selected_specialization': specialization
    })


def doctor_detail_view(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related('department', 'specialization_ref'), pk=pk)
    return render(request, 'doctors/doctor_detail.html', {'doctor': doctor})


@login_required
def doctor_admin_list(request):
    """Admin doctor management module with search, department/specialization/status filtering, and quick CRUD."""
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    department_id = request.GET.get('department', '')
    specialization_id = request.GET.get('specialization', '')
    status_filter = request.GET.get('status', '')

    doctors = Doctor.objects.select_related('department', 'specialization_ref').all()

    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(doctor_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(qualification__icontains=search_query)
        )

    if department_id:
        doctors = doctors.filter(department_id=department_id)

    if specialization_id:
        doctors = doctors.filter(specialization_ref_id=specialization_id)

    if status_filter:
        doctors = doctors.filter(status=status_filter)

    departments = Department.objects.filter(is_active=True)
    specializations = Specialization.objects.filter(is_active=True)
    form = DoctorForm()

    return render(request, 'doctors/doctor_admin.html', {
        'doctors': doctors,
        'departments': departments,
        'specializations': specializations,
        'form': form,
        'search_query': search_query,
        'selected_department': department_id,
        'selected_specialization': specialization_id,
        'selected_status': status_filter,
    })


@login_required
def doctor_create_view(request):
    if not request.user.is_superuser and not (hasattr(request.user, 'profile') and request.user.profile.is_admin_user):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')
        
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor Dr. {doctor.name} ({doctor.doctor_id}) added successfully!")
            return redirect('doctor_admin')
        else:
            messages.error(request, "Error adding doctor. Please check required fields.")
    else:
        form = DoctorForm()
        
    departments = Department.objects.filter(is_active=True)
    specializations = Specialization.objects.filter(is_active=True)
    return render(request, 'doctors/doctor_form.html', {
        'form': form,
        'departments': departments,
        'specializations': specializations,
        'title': 'Add New Doctor Profile'
    })


@login_required
def doctor_update_view(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    
    # Check permission: Admin or the Doctor user themselves
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)
    is_self = doctor.user == request.user
    
    if not (is_admin or is_self):
        messages.error(request, "Permission denied.")
        return redirect('home')
        
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profile for Dr. {doctor.name} updated successfully.")
            if is_admin:
                return redirect('doctor_admin')
            return redirect('doctor_dashboard')
        else:
            messages.error(request, "Error updating doctor profile.")
    else:
        form = DoctorForm(instance=doctor)
        
    departments = Department.objects.filter(is_active=True)
    specializations = Specialization.objects.filter(is_active=True)
    return render(request, 'doctors/doctor_form.html', {
        'form': form,
        'doctor': doctor,
        'departments': departments,
        'specializations': specializations,
        'title': f'Edit Profile: Dr. {doctor.name}'
    })


@login_required
def doctor_delete_view(request, pk):
    if not request.user.is_superuser and not (hasattr(request.user, 'profile') and request.user.profile.is_admin_user):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')
        
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        name = doctor.name
        doctor.delete()
        messages.success(request, f"Doctor Dr. {name} removed successfully.")
        return redirect('doctor_admin')
        
    return render(request, 'doctors/doctor_confirm_delete.html', {'doctor': doctor})

