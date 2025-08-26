from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator που επιτρέπει πρόσβαση μόνο αν ο χρήστης έχει ρόλο μέσα στο allowed_roles.
    Ο γραμματέας (secretary) έχει πάντα πρόσβαση ανεξαρτήτως.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Απαιτείται σύνδεση.")
            # Γραμματέας έχει πάντα πρόσβαση
            if request.user.role == 'secretary':
                return view_func(request, *args, **kwargs)
            # Άλλοι ρόλοι ελέγχονται
            if request.user.role not in allowed_roles:
                raise PermissionDenied("Δεν έχετε δικαίωμα πρόσβασης.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def secretary_required(view_func):
    return role_required(['secretary'])(view_func)

def client_required(view_func):
    return role_required(['client'])(view_func)

def mechanic_required(view_func):
    return role_required(['mechanic'])(view_func)
