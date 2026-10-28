from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Department, Specialization
from .forms import DepartmentForm, SpecializationForm

def department_list_view(request):
    search_query = request.GET.get('search', '')
    departments = Department.objects.filter(is_active=True)
    
    if search_query:
        departments = departments.filter(name__icontains=search_query) | departments.filter(description__icontains=search_query)
        
    return render(request, 'departments/department_list.html', {
        'departments': departments,
        'search_query': search_query
    })


def department_detail_view(request, pk):
    department = get_object_or_404(Department, pk=pk)
    doctors = department.doctors.filter(is_available=True)
    specializations = department.specializations.filter(is_active=True)
    return render(request, 'departments/department_detail.html', {
        'department': department,
        'doctors': doctors,
        'specializations': specializations,
    })


# ==========================================
# DEPARTMENT ADMIN CRUD
# ==========================================

@login_required
def department_admin_list(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')

    departments = Department.objects.all()

    if search_query:
        departments = departments.filter(name__icontains=search_query) | departments.filter(code__icontains=search_query) | departments.filter(description__icontains=search_query)

    if status_filter == 'active':
        departments = departments.filter(is_active=True)
    elif status_filter == 'inactive':
        departments = departments.filter(is_active=False)

    form = DepartmentForm()
    return render(request, 'departments/department_admin.html', {
        'departments': departments,
        'form': form,
        'search_query': search_query,
        'status_filter': status_filter,
    })


@login_required
def department_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')
        
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' created successfully!")
            return redirect('department_admin')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = DepartmentForm()
        
    return render(request, 'departments/department_form.html', {'form': form, 'title': 'Add New Medical Department'})


@login_required
def department_update_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')
        
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES, instance=department)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' updated successfully!")
            return redirect('department_admin')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = DepartmentForm(instance=department)
        
    return render(request, 'departments/department_form.html', {'form': form, 'title': f'Edit Department: {department.name}', 'department': department})


@login_required
def department_delete_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')
        
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f"Department '{name}' deleted successfully.")
        return redirect('department_admin')
        
    return render(request, 'departments/department_confirm_delete.html', {'department': department})


# ==========================================
# SPECIALIZATION CRUD
# ==========================================

@login_required
def specialization_list_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home')

    search_query = request.GET.get('search', '').strip()
    department_id = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')

    specializations = Specialization.objects.select_related('department').all()

    if search_query:
        specializations = specializations.filter(name__icontains=search_query) | specializations.filter(code__icontains=search_query) | specializations.filter(description__icontains=search_query)

    if department_id:
        specializations = specializations.filter(department_id=department_id)

    if status_filter == 'active':
        specializations = specializations.filter(is_active=True)
    elif status_filter == 'inactive':
        specializations = specializations.filter(is_active=False)

    departments = Department.objects.all()
    form = SpecializationForm()

    return render(request, 'departments/specialization_list.html', {
        'specializations': specializations,
        'departments': departments,
        'form': form,
        'search_query': search_query,
        'selected_department': department_id,
        'status_filter': status_filter,
    })


@login_required
def specialization_create_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')

    if request.method == 'POST':
        form = SpecializationForm(request.POST)
        if form.is_valid():
            spec = form.save()
            messages.success(request, f"Specialization '{spec.name}' added successfully!")
            return redirect('specialization_list')
        else:
            messages.error(request, "Error adding specialization. Please check your inputs.")
    else:
        form = SpecializationForm()

    departments = Department.objects.all()
    return render(request, 'departments/specialization_form.html', {'form': form, 'departments': departments, 'title': 'Add New Specialization'})


@login_required
def specialization_update_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')

    spec = get_object_or_404(Specialization, pk=pk)
    if request.method == 'POST':
        form = SpecializationForm(request.POST, instance=spec)
        if form.is_valid():
            form.save()
            messages.success(request, f"Specialization '{spec.name}' updated successfully!")
            return redirect('specialization_list')
        else:
            messages.error(request, "Error updating specialization.")
    else:
        form = SpecializationForm(instance=spec)

    return render(request, 'departments/specialization_form.html', {'form': form, 'specialization': spec, 'title': f'Edit Specialization: {spec.name}'})


@login_required
def specialization_delete_view(request, pk):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Permission denied. Admin access required.")
        return redirect('home')

    spec = get_object_or_404(Specialization, pk=pk)
    if request.method == 'POST':
        name = spec.name
        spec.delete()
        messages.success(request, f"Specialization '{name}' deleted successfully.")
        return redirect('specialization_list')

    return render(request, 'departments/specialization_confirm_delete.html', {'specialization': spec})


def specializations_by_department_api(request, dept_id):
    """API to return specializations for dynamic dropdown loading"""
    specs = Specialization.objects.filter(department_id=dept_id, is_active=True).values('id', 'name', 'code')
    return JsonResponse({'specializations': list(specs)})

