def user_role_context(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {
                'user_profile': profile,
                'is_patient': profile.is_patient,
                'is_doctor': profile.is_doctor,
                'is_admin': profile.is_admin_user or request.user.is_superuser,
            }
        except Exception:
            return {
                'user_profile': None,
                'is_patient': False,
                'is_doctor': False,
                'is_admin': request.user.is_superuser,
            }
    return {
        'user_profile': None,
        'is_patient': False,
        'is_doctor': False,
        'is_admin': False,
    }
