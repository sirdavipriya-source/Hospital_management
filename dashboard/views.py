from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.contrib.auth.models import User
import datetime

from departments.models import Department, Specialization
from doctors.models import Doctor
from appointments.models import Appointment
from patients.models import MedicalRecord
from accounts.models import UserProfile
from pharmacy.models import Medicine, MedicineCategory, Prescription, PrescriptionItem

def home_view(request):
    departments = Department.objects.filter(is_active=True)[:6]
    featured_doctors = Doctor.objects.filter(is_available=True)[:4]
    
    total_patients_count = UserProfile.objects.filter(role='PATIENT').count() or 120
    total_doctors_count = Doctor.objects.count() or 18
    total_departments_count = Department.objects.count() or 10
    total_medicines_count = Medicine.objects.count() or 100
    
    return render(request, 'home.html', {
        'departments': departments,
        'doctors': featured_doctors,
        'total_patients': total_patients_count,
        'total_doctors': total_doctors_count,
        'total_departments': total_departments_count,
        'total_medicines': total_medicines_count,
    })


def about_view(request):
    return render(request, 'about.html')


@login_required
def patient_dashboard_view(request):
    user = request.user
    if hasattr(user, 'profile') and user.profile.is_doctor:
        return redirect('doctor_dashboard')
    elif user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin_user):
        return redirect('doctor_admin')

    patient_appointments = Appointment.objects.filter(patient=user)
    
    today = datetime.date.today()
    
    total_count = patient_appointments.count()
    upcoming_count = patient_appointments.filter(appointment_date__gte=today, status__in=['Pending', 'Confirmed']).count()
    completed_count = patient_appointments.filter(status='Completed').count()
    cancelled_count = patient_appointments.filter(status__in=['Cancelled', 'Rejected']).count()
    
    recent_appointments = patient_appointments.order_by('-appointment_date', '-appointment_time')[:5]
    recent_doctors = Doctor.objects.filter(appointments__patient=user).distinct()[:4]
    prescriptions = Prescription.objects.filter(Q(patient=user) | Q(patient_name__icontains=user.get_full_name() or user.username))[:5]
    
    return render(request, 'dashboard/patient_dashboard.html', {
        'total_appointments': total_count,
        'upcoming_appointments': upcoming_count,
        'completed_appointments': completed_count,
        'cancelled_appointments': cancelled_count,
        'recent_appointments': recent_appointments,
        'recent_doctors': recent_doctors,
        'prescriptions': prescriptions
    })


@login_required
def doctor_dashboard_view(request):
    user = request.user
    if not (user.is_superuser or (hasattr(request.user, 'profile') and (user.profile.is_doctor or user.profile.is_admin_user))):
        return redirect('patient_dashboard')

    try:
        doctor_profile = Doctor.objects.get(user=user)
        doctor_appointments = Appointment.objects.filter(doctor=doctor_profile)
        doctor_prescriptions = Prescription.objects.filter(doctor=doctor_profile)
    except Doctor.DoesNotExist:
        doctor_profile = Doctor.objects.first()
        doctor_appointments = Appointment.objects.filter(doctor=doctor_profile) if doctor_profile else Appointment.objects.all()
        doctor_prescriptions = Prescription.objects.all()

    today = datetime.date.today()
    
    today_count = doctor_appointments.filter(appointment_date=today).count()
    pending_count = doctor_appointments.filter(status='Pending').count()
    completed_count = doctor_appointments.filter(status='Completed').count()
    total_prescriptions = doctor_prescriptions.count()
    
    today_appointments_list = doctor_appointments.filter(appointment_date=today).order_by('appointment_time')
    recent_appointments = doctor_appointments.order_by('-created_at')[:7]
    recent_prescriptions = doctor_prescriptions.order_by('-created_at')[:5]

    return render(request, 'dashboard/doctor_dashboard.html', {
        'doctor': doctor_profile,
        'today_appointments_count': today_count,
        'pending_appointments_count': pending_count,
        'completed_appointments_count': completed_count,
        'total_prescriptions': total_prescriptions,
        'today_appointments': today_appointments_list,
        'recent_appointments': recent_appointments,
        'recent_prescriptions': recent_prescriptions,
    })


# ==========================================
# UNIFIED REPORTS MODULE
# ==========================================

@login_required
def reports_view(request):
    """Consolidated reporting suite for Doctors, Departments, Specializations, Medicine Stock/Expiry, and Prescriptions."""
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home')

    report_type = request.GET.get('report', 'overview')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    filter_category = request.GET.get('category', '')
    filter_status = request.GET.get('status', '')

    today = datetime.date.today()

    doctors = Doctor.objects.select_related('department', 'specialization_ref').all()
    departments = Department.objects.annotate(doc_count=Count('doctors'), spec_count=Count('specializations')).all()
    specializations = Specialization.objects.select_related('department').annotate(doc_count=Count('doctors')).all()
    
    medicines = Medicine.objects.select_related('category').all()
    expired_medicines = Medicine.objects.filter(expiry_date__lt=today)
    low_stock_medicines = Medicine.objects.filter(quantity__gt=0, quantity__lt=15)

    prescriptions = Prescription.objects.select_related('doctor', 'department').prefetch_related('items__medicine').all()
    if start_date:
        prescriptions = prescriptions.filter(prescription_date__gte=start_date)
    if end_date:
        prescriptions = prescriptions.filter(prescription_date__lte=end_date)

    # Summary Stats
    total_inventory_value = sum(m.quantity * float(m.unit_price) for m in medicines)

    return render(request, 'dashboard/reports.html', {
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
        'filter_category': filter_category,
        'filter_status': filter_status,

        'doctors': doctors,
        'departments': departments,
        'specializations': specializations,
        'medicines': medicines,
        'expired_medicines': expired_medicines,
        'low_stock_medicines': low_stock_medicines,
        'prescriptions': prescriptions,

        'total_inventory_value': total_inventory_value,
        'today': today,
    })


@login_required
def dashboard_stats_api(request):
    """AJAX real-time data endpoint for dynamic live stats updates."""
    total_doctors = Doctor.objects.count()
    total_departments = Department.objects.count()
    total_specializations = Specialization.objects.count()
    total_medicines = Medicine.objects.count()
    total_prescriptions = Prescription.objects.count()
    today = datetime.date.today()

    return JsonResponse({
        'total_doctors': total_doctors,
        'total_departments': total_departments,
        'total_specializations': total_specializations,
        'total_medicines': total_medicines,
        'total_prescriptions': total_prescriptions,
        'low_stock_count': Medicine.objects.filter(quantity__gt=0, quantity__lt=15).count(),
        'expired_count': Medicine.objects.filter(expiry_date__lt=today).count(),
        'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
    })


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def custom_500_view(request):
    return render(request, '500.html', status=500)


