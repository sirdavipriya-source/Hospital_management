from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import MedicalRecord

@login_required
def medical_history_view(request):
    """View patient's own medical records or doctor/admin viewing patient records."""
    if hasattr(request.user, 'profile') and request.user.profile.is_patient:
        records = MedicalRecord.objects.filter(patient=request.user)
    elif request.user.is_superuser or (hasattr(request.user, 'profile') and (request.user.profile.is_admin_user or request.user.profile.is_doctor)):
        patient_id = request.GET.get('patient_id')
        if patient_id:
            records = MedicalRecord.objects.filter(patient_id=patient_id)
        else:
            records = MedicalRecord.objects.all()
    else:
        records = MedicalRecord.objects.none()
        
    return render(request, 'patients/medical_history.html', {'records': records})


@login_required
def prescriptions_view(request):
    """View active prescriptions."""
    if hasattr(request.user, 'profile') and request.user.profile.is_patient:
        records = MedicalRecord.objects.filter(patient=request.user).exclude(prescription__isnull=True).exclude(prescription__exact='')
    else:
        records = MedicalRecord.objects.exclude(prescription__isnull=True).exclude(prescription__exact='')
        
    return render(request, 'patients/prescriptions.html', {'records': records})


@login_required
def patient_list_admin_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and (request.user.profile.is_admin_user or request.user.profile.is_doctor))):
        messages.error(request, "Permission denied.")
        return redirect('home')
        
    search_query = request.GET.get('search', '')
    patients = User.objects.filter(profile__role='PATIENT')
    
    if search_query:
        patients = patients.filter(
            first_name__icontains=search_query
        ) | patients.filter(
            last_name__icontains=search_query
        ) | patients.filter(
            username__icontains=search_query
        ) | patients.filter(
            email__icontains=search_query
        )
        
    return render(request, 'patients/patient_list.html', {
        'patients': patients,
        'search_query': search_query
    })
