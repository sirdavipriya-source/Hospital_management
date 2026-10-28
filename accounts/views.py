from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import PatientRegistrationForm, UserLoginForm, UserUpdateForm, UserProfileForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create associated patient profile
            UserProfile.objects.create(
                user=user,
                role='PATIENT',
                phone=form.cleaned_data.get('phone'),
                gender=form.cleaned_data.get('gender'),
                date_of_birth=form.cleaned_data.get('date_of_birth'),
                address=form.cleaned_data.get('address')
            )
            
            login(request, user)
            messages.success(request, f"Welcome to MedCare, {user.first_name}! Account created successfully.")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Please correct the errors below to complete registration.")
    else:
        form = PatientRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Allow login using email or username
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
                    
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('dashboard_redirect')
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form, 'title': 'Patient & General Login', 'role_badge': 'Patient / User Portal'})


def doctor_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
                    
            if user:
                if hasattr(user, 'profile') and (user.profile.is_doctor or user.profile.is_admin_user):
                    login(request, user)
                    messages.success(request, f"Welcome Doctor {user.last_name or user.username}!")
                    return redirect('doctor_dashboard')
                else:
                    messages.error(request, "Access restricted. This login is for medical staff and doctors only.")
            else:
                messages.error(request, "Invalid credentials for Doctor portal.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form, 'title': 'Doctor & Medical Staff Portal', 'role_badge': 'Doctor Access Only', 'is_doctor_login': True})


def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username_or_email, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
                    
            if user and (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_admin_user)):
                login(request, user)
                messages.success(request, f"System Administrator Logged In: {user.username}")
                return redirect('doctor_admin')
            else:
                messages.error(request, "Unauthorized admin credentials.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form, 'title': 'Hospital Administrator Console', 'role_badge': 'System Admin Access', 'is_admin_login': True})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('home')


@login_required
def dashboard_redirect_view(request):
    """Redirect user to appropriate role-based dashboard after authentication."""
    user = request.user
    if user.is_superuser:
        return redirect('doctor_admin')
        
    try:
        profile = user.profile
        if profile.is_admin_user:
            return redirect('doctor_admin')
        elif profile.is_doctor:
            return redirect('doctor_dashboard')
        else:
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        # Create default patient profile if missing
        UserProfile.objects.create(user=user, role='PATIENT')
        return redirect('patient_dashboard')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileForm(instance=profile)
        
    return render(request, 'accounts/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile
    })
