def user_type(request):
    if request.user.is_authenticated:
        try:
            is_student = hasattr(request.user, 'student_profile') and request.user.student_profile is not None
        except Exception:
            is_student = False
        return {'is_student': is_student}
    return {'is_student': False}