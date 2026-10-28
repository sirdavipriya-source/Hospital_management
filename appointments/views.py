from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Appointment
from .forms import AppointmentBookingForm, AppointmentStatusForm, DiagnosisPrescriptionForm
from patients.models import MedicalRecord
from doctors.models import Doctor
from departments.models import Department

@login_required
def book_appointment_view(request):
    department_id = request.GET.get('department')
    doctor_id = request.GET.get('doctor')
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.patient = request.user
                appointment.status = 'Pending'
                appointment.save()
                messages.success(request, f"Appointment booked successfully with Dr. {appointment.doctor.name} for {appointment.appointment_date} at {appointment.appointment_time.strftime('%I:%M %p')}!")
                return redirect('appointment_list')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, error)
            except Exception as e:
                messages.error(request, f"Error booking appointment: {str(e)}")
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = AppointmentBookingForm(department_id=department_id, doctor_id=doctor_id)
        
    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'departments': Department.objects.filter(is_active=True),
        'doctors': Doctor.objects.filter(is_available=True)
    })


@login_required
def appointment_list_view(request):
    user = request.user
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    appointments = Appointment.objects.all()
    
    # Filter based on user role
    if hasattr(user, 'profile') and user.profile.is_patient:
        appointments = appointments.filter(patient=user)
    elif hasattr(user, 'profile') and user.profile.is_doctor:
        try:
            doctor_profile = Doctor.objects.get(user=user)
            appointments = appointments.filter(doctor=doctor_profile)
        except Doctor.DoesNotExist:
            appointments = appointments.none()
    elif not (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin_user)):
        appointments = appointments.filter(patient=user)
        
    if status_filter:
        appointments = appointments.filter(status=status_filter)
        
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
        
    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(doctor__name__icontains=search_query) |
            Q(reason__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )
        
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        'status_choices': Appointment.STATUS_CHOICES
    })


@login_required
def update_appointment_status_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status') or request.GET.get('status')
    
    if not new_status:
        messages.error(request, "No status provided.")
        return redirect('appointment_list')
        
    # Permission check: Doctor or Admin or Patient (cancel only)
    is_doctor = hasattr(request.user, 'profile') and request.user.profile.is_doctor
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_admin_user)
    is_patient = appointment.patient == request.user
    
    if is_patient and new_status == 'Cancelled':
        appointment.status = 'Cancelled'
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} has been cancelled.")
    elif is_doctor or is_admin:
        if new_status in ['Pending', 'Confirmed', 'Completed', 'Cancelled', 'Rejected']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f"Appointment #{appointment.id} status updated to '{new_status}'.")
        else:
            messages.error(request, "Invalid status choice.")
    else:
        messages.error(request, "Unauthorized action.")
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'status': appointment.status, 'id': appointment.id})
        
    return redirect(request.META.get('HTTP_REFERER', 'appointment_list'))


@login_required
def add_diagnosis_prescription_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = DiagnosisPrescriptionForm(request.POST)
        if form.is_valid():
            # Get doctor profile if present
            doctor = appointment.doctor
            
            # Create or update MedicalRecord
            record, created = MedicalRecord.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'patient': appointment.patient,
                    'doctor': doctor,
                    'diagnosis': form.cleaned_data['diagnosis'],
                    'prescription': form.cleaned_data['prescription'],
                    'medical_notes': form.cleaned_data.get('medical_notes', '')
                }
            )
            
            if not created:
                record.diagnosis = form.cleaned_data['diagnosis']
                record.prescription = form.cleaned_data['prescription']
                record.medical_notes = form.cleaned_data.get('medical_notes', '')
                record.save()
                
            # Automatically set appointment status to Completed
            appointment.status = 'Completed'
            appointment.save()
            
            messages.success(request, f"Medical record & prescription saved for Appointment #{appointment.id}!")
            return redirect('doctor_dashboard')
    else:
        # Pre-fill if medical record exists
        initial = {}
        if hasattr(appointment, 'medical_record'):
            rec = appointment.medical_record
            initial = {
                'diagnosis': rec.diagnosis,
                'prescription': rec.prescription,
                'medical_notes': rec.medical_notes
            }
        form = DiagnosisPrescriptionForm(initial=initial)
        
    return render(request, 'appointments/add_prescription.html', {
        'form': form,
        'appointment': appointment
    })


@login_required
def check_doctor_availability_api(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'booked_slots': []})
        
    booked_slots = Appointment.objects.filter(
        doctor_id=doctor_id,
        appointment_date=date_str
    ).exclude(status__in=['Cancelled', 'Rejected']).values_list('appointment_time', flat=True)
    
    formatted_slots = [t.strftime('%H:%M:%S') for t in booked_slots]
    return JsonResponse({'booked_slots': formatted_slots})
