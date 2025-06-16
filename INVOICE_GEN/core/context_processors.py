from .models import UserProfile

def user_role_context(request):
    role = None
    if request.user.is_authenticated:
        try:
            role = UserProfile.objects.get(user=request.user).role
        except UserProfile.DoesNotExist:
            role = None
    return {'user_role': role}